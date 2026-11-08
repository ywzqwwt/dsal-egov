#!/usr/bin/env python3
"""Reference baseline harness for DSAL-Egov Concept Benchmark v1.

This is a light, dependency-free alternative to `evaluate_pipeline.py`.  It
implements two lexical/static baselines on the same candidate-ranking task, for
readers who do not want to install PyTorch.  The paper's reported results come
from `evaluate_pipeline.py`, not from this file:

  tfidf   TF-IDF (word 1-2 grams plus character 3-5 grams) cosine retrieval
  svd     PPMI + truncated-SVD static embeddings, mean-pooled, cosine

Both rank the 24 platform concepts of the target platform.  The harness repeats
the stratified split and the whole scoring procedure for five seeds and reports
t-based 95% intervals for Top-1, Recall@5 and MRR.

The purpose of the harness is to let readers reproduce the *protocol* and to
calibrate how difficult the benchmark is for lexical methods.  Its numbers are
not reported in the paper and are not interchangeable with them.

Usage:
  python3 evaluate_baselines.py --data ../benchmark/egov_concept_pairs.csv \
                                --vocab ../benchmark/concept_vocabulary.csv \
                                --out results --seeds 5
"""

from __future__ import annotations

import argparse
import csv
import json
import math
import random
from collections import Counter, defaultdict
from pathlib import Path

import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.preprocessing import normalize

PLATFORMS = ["fabric", "bcos", "corda"]
T975 = 2.776


def load(path: Path):
    with path.open(encoding="utf-8") as fh:
        return list(csv.DictReader(fh))


def candidates(path: Path):
    out = {p: {} for p in PLATFORMS}
    with path.open(encoding="utf-8") as fh:
        for row in csv.DictReader(fh):
            out[row["platform"]][row["concept_id"]] = (
                f"{row['platform_term']}. {row['documented_gloss']}")
    return out


def split(rows, seed):
    rng = random.Random(seed)
    buckets = defaultdict(list)
    for r in rows:
        buckets[(r["concept_id"], r["target_platform"])].append(r)
    train, test = [], []
    for items in buckets.values():
        items = items[:]
        rng.shuffle(items)
        n = len(items)
        a = int(round(0.85 * n))
        train += items[:a]
        test += items[a:]
    return train, test


class PPMI:
    def __init__(self, dim=100, window=5, min_count=1):
        self.dim, self.window, self.min_count = dim, window, min_count

    def fit(self, docs):
        toks = [d.lower().split() for d in docs]
        counts = Counter(t for d in toks for t in d)
        vocab = [w for w, c in counts.most_common() if c >= self.min_count]
        self.index = {w: i for i, w in enumerate(vocab)}
        co = np.zeros((len(vocab), len(vocab)), dtype=np.float32)
        for d in toks:
            ids = [self.index[t] for t in d if t in self.index]
            for i, w in enumerate(ids):
                for j in range(max(0, i - self.window), min(len(ids), i + self.window + 1)):
                    if j != i:
                        co[w, ids[j]] += 1.0
        total = co.sum()
        row = co.sum(1, keepdims=True)
        col = co.sum(0, keepdims=True)
        with np.errstate(divide="ignore", invalid="ignore"):
            pmi = np.log((co * total) / (row * col + 1e-12) + 1e-12)
        self.vecs = np.maximum(pmi, 0.0)
        return self

    def transform(self, docs):
        from sklearn.decomposition import TruncatedSVD
        svd = TruncatedSVD(n_components=min(self.dim, self.vecs.shape[0] - 1),
                           random_state=0).fit(self.vecs)
        emb = svd.transform(self.vecs)
        emb = normalize(emb)
        table = {w: emb[i] for w, i in self.index.items()}

        def mean_vec(text):
            ids = [table[t] for t in text.lower().split() if t in table]
            if not ids:
                return np.zeros(emb.shape[1])
            return normalize(np.mean(ids, 0, keepdims=True))[0]

        return mean_vec


def rank_metrics(sim_row, gold_idx):
    order = np.argsort(-sim_row)
    pos = int(np.where(order == gold_idx)[0][0])
    return float(pos == 0), float(pos < 5), 1.0 / (pos + 1)


def evaluate(get_vec, rows, cand, cand_index):
    per_p = {}
    for p in PLATFORMS:
        ids = sorted(cand_index[p], key=cand_index[p].get)
        mat = np.stack([get_vec(cand[p][cid]) for cid in ids])
        per_p[p] = (ids, normalize(mat))
    t1 = r5 = mrr = 0.0
    for r in rows:
        ids, mat = per_p[r["target_platform"]]
        v = normalize(get_vec(r["source_description"]).reshape(1, -1))[0]
        gold = ids.index(r["concept_id"])
        a, b, c = rank_metrics(mat @ v, gold)
        t1 += a
        r5 += b
        mrr += c
    n = len(rows)
    return t1 / n, r5 / n, mrr / n


def ci(vals, scale=100.0):
    v = np.array(vals) * scale
    m, sd = v.mean(), v.std(ddof=1)
    half = T975 * sd / math.sqrt(len(v))
    return dict(mean=round(float(m), 1), sd=round(float(sd), 1),
                lo=round(float(m - half), 1), hi=round(float(m + half), 1))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--data", default="../benchmark/egov_concept_pairs.csv")
    ap.add_argument("--vocab", default="../benchmark/concept_vocabulary.csv")
    ap.add_argument("--out", default="results")
    ap.add_argument("--seeds", type=int, default=5)
    args = ap.parse_args()

    rows = load(Path(args.data))
    cand = candidates(Path(args.vocab))
    cand_index = {p: {cid: i for i, cid in enumerate(sorted(cand[p]))} for p in PLATFORMS}

    res = {"tfidf": [], "svd": []}
    for seed in range(args.seeds):
        tr, te = split(rows, 1000 + seed)
        corpus = [r["source_description"] for r in rows] + \
                 [t for p in PLATFORMS for t in cand[p].values()]

        vec = TfidfVectorizer(ngram_range=(1, 2), sublinear_tf=True,
                              analyzer="word", min_df=1).fit(corpus)
        res["tfidf"].append(evaluate(lambda s: vec.transform([s]).toarray()[0], te, cand, cand_index))

        ppmi = PPMI().fit(corpus)
        res["svd"].append(evaluate(ppmi.transform(corpus), te, cand, cand_index))
        print(f"seed {seed}: tfidf {res['tfidf'][-1][0]:.3f}  svd {res['svd'][-1][0]:.3f}")

    summary = {k: dict(top1=ci([v[0] for v in vals]),
                       recall5=ci([v[1] for v in vals]),
                       mrr=ci([v[2] for v in vals], scale=1.0)) for k, vals in res.items()}

    out = Path(args.out)
    out.mkdir(parents=True, exist_ok=True)
    (out / "baseline_results.json").write_text(
        json.dumps({"per_seed": res, "summary": summary}, indent=2), encoding="utf-8")
    md = ["| Baseline | Top-1 % (SD) | 95% CI | Recall@5 % | MRR | Candidates |",
          "|---|---|---|---|---|---|"]
    for k, label in [("tfidf", "TF-IDF retrieval"), ("svd", "PPMI-SVD retrieval")]:
        s = summary[k]
        md.append(f"| {label} | {s['top1']['mean']} ({s['top1']['sd']}) | "
                  f"[{s['top1']['lo']}, {s['top1']['hi']}] | {s['recall5']['mean']} | "
                  f"{s['mrr']['mean']:.3f} | 24 |")
    (out / "baseline_results.md").write_text("\n".join(md) + "\n", encoding="utf-8")
    print("\n".join(md))


if __name__ == "__main__":
    main()
