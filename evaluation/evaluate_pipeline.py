#!/usr/bin/env python3
"""Reference implementation of the DSAL two-stage concept-mapping pipeline.

Stage 1  static-embedding retrieval: Word2Vec (skip-gram with negative sampling,
         trained on the benchmark corpus) ranks every platform concept by cosine
         similarity to the source description and keeps the top K.
Stage 2  Bi-LSTM reranker: scores each retained candidate against the source
         description and selects one.

Compared methods, all on the same data and the same splits:
  retrieval   static embeddings only, ranking all candidates
  mlp         static embeddings + multilayer-perceptron scorer over the top-K
  bilstm      Bi-LSTM reranker over the top-K  (the DSAL pipeline)

Protocol: stratified 70/15/15 split by (concept, platform); five seeds; t-based
95 % intervals (df = 4).  Also runs a leave-one-platform-out check in which the
model is trained on Fabric + FISCO BCOS pairs and applied to Corda pairs without
retraining.

Usage:
  PYTHONPATH=/tmp/torchlib python3 evaluate_pipeline.py --seeds 5
"""

from __future__ import annotations

import argparse
import csv
import json
import math
import random
from collections import defaultdict
from pathlib import Path

import numpy as np
import torch
import torch.nn as nn
import torch.nn.functional as F

# Single-threaded execution keeps the floating-point reduction order fixed, so
# repeated runs on the same machine reproduce the reported numbers bit for bit.
torch.set_num_threads(1)

PLATFORMS = ["fabric", "bcos", "corda"]
PAD, UNK = 0, 1
MAXLEN = 32
T975_4 = 2.776


def tokenize(text: str):
    out, cur = [], []
    for ch in text.lower():
        if ch.isalnum():
            cur.append(ch)
        elif cur:
            out.append("".join(cur))
            cur = []
    if cur:
        out.append("".join(cur))
    return out


def load_rows(path: Path):
    with path.open(encoding="utf-8") as fh:
        rows = list(csv.DictReader(fh))
    for r in rows:
        r["tokens"] = tokenize(r["source_description"])
    return rows


def load_candidates(path: Path):
    out = {p: {} for p in PLATFORMS}
    with path.open(encoding="utf-8") as fh:
        for row in csv.DictReader(fh):
            out[row["platform"]][row["concept_id"]] = tokenize(
                f"{row['platform_term']} {row['documented_gloss']}")
    return out


def build_vocab(rows, cand):
    counts = defaultdict(int)
    for r in rows:
        for t in r["tokens"]:
            counts[t] += 1
    for p in PLATFORMS:
        for toks in cand[p].values():
            for t in toks:
                counts[t] += 1
    return {w: i + 2 for i, w in enumerate(sorted(counts, key=lambda w: (-counts[w], w)))}


def encode(tokens, vocab):
    ids = [vocab.get(t, UNK) for t in tokens][:MAXLEN]
    return ids + [PAD] * (MAXLEN - len(ids))


def split_rows(rows, seed):
    rng = random.Random(seed)
    buckets = defaultdict(list)
    for r in rows:
        buckets[(r["concept_id"], r["target_platform"])].append(r)
    train, val, test = [], [], []
    for items in buckets.values():
        items = items[:]
        rng.shuffle(items)
        n = len(items)
        a, b = int(round(0.70 * n)), int(round(0.15 * n))
        train += items[:a]
        val += items[a:a + b]
        test += items[a + b:]
    return train, val, test


def train_word2vec(corpus, vocab, dim=100, seed=0, epochs=8, window=5):
    torch.manual_seed(seed)
    size = len(vocab) + 2
    emb, ctx = nn.Embedding(size, dim), nn.Embedding(size, dim)
    nn.init.uniform_(emb.weight, -0.5 / dim, 0.5 / dim)
    nn.init.zeros_(ctx.weight)
    opt = torch.optim.Adam(list(emb.parameters()) + list(ctx.parameters()), lr=5e-3)
    pairs = []
    for doc in corpus:
        ids = [vocab.get(t, UNK) for t in doc]
        for i, w in enumerate(ids):
            for j in range(max(0, i - window), min(len(ids), i + window + 1)):
                if j != i:
                    pairs.append((w, ids[j]))
    idx = torch.tensor(pairs)
    for _ in range(epochs):
        perm = torch.randperm(len(idx))
        for s in range(0, len(idx), 4096):
            b = idx[perm[s:s + 4096]]
            w, c = b[:, 0], b[:, 1]
            neg = torch.randint(2, size, (w.size(0), 5))
            v = emb(w)
            pos = (v * ctx(c)).sum(1)
            negs = torch.bmm(ctx(neg), v.unsqueeze(2)).squeeze(2)
            loss = -(F.logsigmoid(pos).mean() + F.logsigmoid(-negs).mean())
            opt.zero_grad()
            loss.backward()
            opt.step()
    return emb.weight.detach()


def mean_vec(tokens, vocab, table):
    ids = [vocab.get(t, UNK) for t in tokens][:MAXLEN]
    if not ids:
        return torch.zeros(table.size(1))
    return table[torch.tensor(ids)].mean(0)


class MLPScorer(nn.Module):
    def __init__(self, dim):
        super().__init__()
        self.net = nn.Sequential(nn.Linear(dim * 4, 128), nn.ReLU(),
                                 nn.Dropout(0.2), nn.Linear(128, 1))

    def forward(self, s, c):
        s = s.unsqueeze(1).expand(-1, c.size(1), -1)
        return self.net(torch.cat([s, c, s * c, (s - c).abs()], -1)).squeeze(-1)


class BiLSTMReranker(nn.Module):
    def __init__(self, vocab_size, dim=100, hidden=64):
        super().__init__()
        self.emb = nn.Embedding(vocab_size, dim, padding_idx=PAD)
        self.lstm = nn.LSTM(dim, hidden, batch_first=True, bidirectional=True)
        self.drop = nn.Dropout(0.3)
        self.net = nn.Sequential(nn.Linear(hidden * 8, 128), nn.ReLU(),
                                 nn.Dropout(0.3), nn.Linear(128, 1))

    def encode(self, x):
        out, _ = self.lstm(self.drop(self.emb(x)))
        mask = (x != PAD).float().unsqueeze(-1)
        return (out * mask).sum(1) / mask.sum(1).clamp(min=1)

    def forward(self, src, cand):
        b, k, _ = cand.shape
        hs = self.encode(src)
        hc = self.encode(cand.reshape(b * k, -1))
        hs = hs.unsqueeze(1).expand(b, k, -1).reshape(b * k, -1)
        return self.net(torch.cat([hs, hc, hs * hc, (hs - hc).abs()], -1)).view(b, k)


class VecModel(nn.Module):
    def __init__(self, table, vec_lookup):
        super().__init__()
        self.table = table
        self.vec_lookup = vec_lookup
        self.inner = MLPScorer(table.size(1))

    def forward(self, s, c):
        return self.inner(s, c)


def candidate_tensors(cand, vocab, index, table):
    ids, vecs, lookup = {}, {}, {}
    for p in PLATFORMS:
        cids = sorted(index[p], key=index[p].get)
        ids[p] = (cids, torch.tensor([encode(cand[p][c], vocab) for c in cids]))
        vecs[p] = (cids, torch.stack([mean_vec(cand[p][c], vocab, table) for c in cids]))
        for c in cids:
            lookup[(p, c)] = mean_vec(cand[p][c], vocab, table)
    return ids, vecs, lookup


def retrieve(rows, vecs, table, vocab, k):
    out = []
    for r in rows:
        cids, mat = vecs[r["target_platform"]]
        v = F.normalize(mean_vec(r["tokens"], vocab, table).unsqueeze(0), dim=1)
        sims = (F.normalize(mat, dim=1) @ v.T).squeeze(1)
        out.append((cids, sims.argsort(descending=True)[:k].tolist()))
    return out


def score_pair(model, r, sel, kind, cand_ids, vocab, lookup):
    p = r["target_platform"]
    if kind == "ids":
        s = torch.tensor(encode(r["tokens"], vocab)).unsqueeze(0)
        table = dict(zip(cand_ids[p][0], cand_ids[p][1]))
        c = torch.stack([table[cid] for cid in sel]).unsqueeze(0)
        return model(s, c).squeeze(0)
    s = mean_vec(r["tokens"], vocab, model.table).unsqueeze(0).expand(len(sel), -1)
    c = torch.stack([lookup[(p, cid)] for cid in sel])
    return model(s, c)


def batch_scores(model, rows, retrievals, kind, cand_ids, vocab, lookup):
    """Score every row's retrieved candidate set, grouped by platform."""
    out = [None] * len(rows)
    by_p = defaultdict(list)
    for i, r in enumerate(rows):
        by_p[r["target_platform"]].append(i)
    for p, idxs in by_p.items():
        k = len(retrievals[idxs[0]][1])
        sel = torch.tensor([[retrievals[i][1][j] for j in range(k)] for i in idxs])
        if kind == "ids":
            s = torch.tensor([encode(rows[i]["tokens"], vocab) for i in idxs])
            c = cand_ids[p][1][sel]                      # (B,K,32)
            sc = model(s, c)
        else:
            s = torch.stack([mean_vec(rows[i]["tokens"], vocab, model.table) for i in idxs])
            c = torch.stack([lookup[(p, cid)] for cid in cand_ids[p][0]])[sel]
            sc = model(s, c)
        for j, i in enumerate(idxs):
            out[i] = sc[j]
    return out


def evaluate(model, rows, retrievals, cand_ids, vocab, kind, lookup):
    model.eval()
    top1 = rec5 = mrr = 0.0
    with torch.no_grad():
        scores = batch_scores(model, rows, retrievals, kind, cand_ids, vocab, lookup)
        for r, (cids, order), sc in zip(rows, retrievals, scores):
            sel = [cids[j] for j in order]
            if r["concept_id"] not in sel:
                continue
            pos = int((sc > sc[sel.index(r["concept_id"])]).sum())
            top1 += pos == 0
            rec5 += pos < 5
            mrr += 1.0 / (pos + 1)
    n = len(rows)
    return top1 / n, rec5 / n, mrr / n


def train(model, train_rows, val_rows, rtr, rva, cand_ids, vocab, kind,
          lookup, seed, epochs=10, lr=2e-3, bs=32):
    torch.manual_seed(seed)
    opt = torch.optim.Adam(model.parameters(), lr=lr)
    best, best_state = -1.0, None
    for _ in range(epochs):
        model.train()
        perm = torch.randperm(len(train_rows)).tolist()
        for s0 in range(0, len(perm), bs):
            batch = perm[s0:s0 + bs]
            b_rows = [train_rows[i] for i in batch]
            b_ret = [rtr[i] for i in batch]
            keep = [i for i in range(len(b_rows))]
            scores = batch_scores(model, b_rows, b_ret, kind, cand_ids, vocab, lookup)
            golds = []
            valid_scores = []
            for j in keep:
                sel = [b_ret[j][0][q] for q in b_ret[j][1]]
                if b_rows[j]["concept_id"] not in sel:
                    continue
                valid_scores.append(scores[j])
                golds.append(sel.index(b_rows[j]["concept_id"]))
            if not valid_scores:
                continue
            loss = F.cross_entropy(torch.stack(valid_scores), torch.tensor(golds))
            opt.zero_grad()
            loss.backward()
            opt.step()
        acc = evaluate(model, val_rows, rva, cand_ids, vocab, kind, lookup)[0]
        if acc > best:
            best = acc
            best_state = {k: v.detach().clone() for k, v in model.state_dict().items()}
    if best_state:
        model.load_state_dict(best_state)
    return model


def ci(vals, scale=100.0):
    v = np.array(vals) * scale
    m, sd = v.mean(), v.std(ddof=1)
    half = T975_4 * sd / math.sqrt(len(v))
    return dict(mean=round(float(m), 1), sd=round(float(sd), 1),
                lo=round(float(m - half), 1), hi=round(float(m + half), 1))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--data", default="../benchmark/egov_concept_pairs.csv")
    ap.add_argument("--vocab", default="../benchmark/concept_vocabulary.csv")
    ap.add_argument("--out", default="results")
    ap.add_argument("--seeds", type=int, default=5)
    ap.add_argument("--k", type=int, default=10)
    ap.add_argument("--epochs", type=int, default=3)
    args = ap.parse_args()

    rows = load_rows(Path(args.data))
    cand = load_candidates(Path(args.vocab))
    vocab = build_vocab(rows, cand)
    index = {p: {c: i for i, c in enumerate(sorted(cand[p]))} for p in PLATFORMS}
    dim_vocab = len(vocab) + 2

    per_seed, lopo, recall = [], {}, {}
    for seed in range(args.seeds):
        tr, va, te = split_rows(rows, 1000 + seed)
        corpus = [r["tokens"] for r in tr] + [d for p in PLATFORMS for d in cand[p].values()]
        table = train_word2vec(corpus, vocab, seed=seed)
        cand_ids, cand_vecs, lookup = candidate_tensors(cand, vocab, index, table)

        rtr = retrieve(tr, cand_vecs, table, vocab, args.k)
        rva = retrieve(va, cand_vecs, table, vocab, args.k)
        rte = retrieve(te, cand_vecs, table, vocab, args.k)
        recall[seed] = float(np.mean([1.0 if r["concept_id"] in [c[j] for j in o] else 0.0
                                      for r, (c, o) in zip(te, rte)]))

        # pure retrieval over all candidates
        rall = retrieve(te, cand_vecs, table, vocab, len(next(iter(index.values()))))
        ret_t1 = ret_mrr = 0.0
        for r, (cids, order) in zip(te, rall):
            sel = [cids[j] for j in order]
            s = mean_vec(r["tokens"], vocab, table).unsqueeze(0).expand(len(sel), -1)
            c = torch.stack([lookup[(r["target_platform"], cid)] for cid in sel])
            sims = F.cosine_similarity(s, c, dim=1)
            pos = int((sims > sims[sel.index(r["concept_id"])]).sum())
            ret_t1 += pos == 0
            ret_mrr += 1.0 / (pos + 1)
        ret = (ret_t1 / len(te), None, ret_mrr / len(te))

        mlp = VecModel(table, lookup)
        train(mlp, tr, va, rtr, rva, cand_ids, vocab, "vec", lookup, seed, args.epochs)
        mlp_m = evaluate(mlp, te, rte, cand_ids, vocab, "vec", lookup)

        bi = BiLSTMReranker(dim_vocab)
        train(bi, tr, va, rtr, rva, cand_ids, vocab, "ids", lookup, seed, args.epochs)
        bi_m = evaluate(bi, te, rte, cand_ids, vocab, "ids", lookup)

        per_seed.append(dict(seed=seed, n_test=len(te), recall_at_k=recall[seed],
                             retrieval=ret, mlp=mlp_m, bilstm=bi_m))
        print(f"seed {seed}: R@{args.k}={recall[seed]:.3f} "
              f"retrieval={ret[0]:.3f} mlp={mlp_m[0]:.3f} bilstm={bi_m[0]:.3f}")

        tr2 = [x for x in tr if x["target_platform"] != "corda"]
        va2 = [x for x in va if x["target_platform"] != "corda"]
        te2 = [x for x in te if x["target_platform"] == "corda"]
        bi2 = BiLSTMReranker(dim_vocab)
        train(bi2, tr2, va2, retrieve(tr2, cand_vecs, table, vocab, args.k),
              retrieve(va2, cand_vecs, table, vocab, args.k),
              cand_ids, vocab, "ids", lookup, seed, args.epochs)
        lopo[seed] = evaluate(bi2, te2, retrieve(te2, cand_vecs, table, vocab, args.k),
                              cand_ids, vocab, "ids", lookup)
        print(f"  Corda held out: top1={lopo[seed][0]:.3f} (n={len(te2)})")

    summary = dict(
        recall_at_k=ci(list(recall.values())),
        retrieval=dict(top1=ci([r["retrieval"][0] for r in per_seed]),
                       mrr=ci([r["retrieval"][2] for r in per_seed], 1.0)),
        mlp=dict(top1=ci([r["mlp"][0] for r in per_seed]),
                 recall5=ci([r["mlp"][1] for r in per_seed]),
                 mrr=ci([r["mlp"][2] for r in per_seed], 1.0)),
        bilstm=dict(top1=ci([r["bilstm"][0] for r in per_seed]),
                    recall5=ci([r["bilstm"][1] for r in per_seed]),
                    mrr=ci([r["bilstm"][2] for r in per_seed], 1.0)),
        lopo_bilstm=dict(top1=ci([v[0] for v in lopo.values()]),
                         recall5=ci([v[1] for v in lopo.values()]),
                         mrr=ci([v[2] for v in lopo.values()], 1.0)),
    )
    out = Path(args.out)
    out.mkdir(parents=True, exist_ok=True)
    (out / "pipeline_results.json").write_text(
        json.dumps(dict(k=args.k, per_seed=per_seed, lopo=lopo, summary=summary), indent=2),
        encoding="utf-8")
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
