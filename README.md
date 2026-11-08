# DSAL-Egov — reproducibility package

Supplementary material for the manuscript *A Domain-Specific Abstraction Layer for
Interoperability across Heterogeneous Blockchain Platforms in E-Government Systems*.

| | |
|---|---|
| Public repository | `https://github.com/ywzqwwt/dsal-egov` |
| Frozen release | tag `v1.0.0` — `https://github.com/ywzqwwt/dsal-egov/tree/v1.0.0` |
| Archive download | `https://github.com/ywzqwwt/dsal-egov/archive/refs/tags/v1.0.0.zip` |
| Code licence | MIT (`LICENSE`) |
| Data licence | CC BY 4.0 (`DATA_LICENSE.md`) |
| Dependencies | `requirements.txt` (Python 3.10+) |

> **TODO before submission:** add all manuscript co-authors to `CITATION.cff`
> and to the Title Page. Then delete this TODO block.

This package contains the artifacts for the manuscript. Everything here is
synthetic, computational, or derived from public documentation. No agency data, no
employer material, and no person-level data are included.

The complete, versioned artefact set is hosted at the public repository above and
frozen at the `v1.0.0` tag rather than attached to the journal's submission system,
so that reviewers and readers always obtain the exact directory layout the scripts
expect. The `main` branch may receive subsequent revisions; the tag does not change.

## Contents

```
benchmark/     DSAL-Egov Concept Benchmark v1 (generator + generated instance)
evaluation/    pipeline reference implementation + evaluation harness + recorded results
figures/       Python sources for the manuscript's figures
tla/           TLA+ module, TLC configuration and recorded model-checking log
```

## 1. Scope of the benchmark

The study's annotated concept-mapping corpus was produced under a separate
institutional agreement and is not redistributable. To keep the candidate-ranking
protocol reproducible, this package provides a *controlled synthetic* benchmark that
encodes the same task on terminology drawn from the public documentation of
Hyperledger Fabric, FISCO BCOS and Corda.

It is honest about what it is: **a controlled test bed, not a sample of agency
documentation.** Accuracy on this benchmark measures whether a pipeline recovers
documented term correspondences under controlled surface variation. It does not
predict accuracy on an unseen agency's vocabulary, and it must not be presented as
if it did.

## 2. Benchmark specification

| Property | Value |
|---|---|
| Version | 1.0 |
| Concepts | 24 abstract DSAL concepts in 8 families |
| Platforms | Hyperledger Fabric, FISCO BCOS, Corda |
| Surface variants per (concept, platform) | 75 |
| Pairs | 5,400 |
| Candidate pool | 24 (all concepts of the target platform) |
| Split (released default) | 70 / 15 / 15, stratified by concept x platform |
| Labels | exact by construction (no human annotation) |

Columns of `benchmark/egov_concept_pairs.csv`:

| Column | Meaning |
|---|---|
| `pair_id` | stable identifier |
| `concept_id` | abstract DSAL concept (`C01`-`C24`) |
| `family` | isolation, identity, consensus, contract, policy, workflow, audit, data |
| `dsal_term` | abstract concept name |
| `target_platform` | `fabric`, `bcos`, `corda` |
| `gold_term` | the platform term that must be ranked first |
| `source_description` | the concept description shown to the model |
| `split` | released default split (`train` / `val` / `test`) |

`benchmark/concept_vocabulary.csv` lists the 24 concepts with their three platform
realisations; it is the candidate pool for ranking.

Regenerate the instance (deterministic):

```bash
cd benchmark
python3 generate_benchmark.py --out . --variants 75 --seed 20261105
```

Integrity of the split is enforced by the generator: it samples each cell's 75
variants without replacement and asserts that all 5,400 descriptions are distinct and
that no test description also occurs in training or validation (0 overlap).

## 3. Reference implementation and its results

`evaluation/evaluate_pipeline.py` implements the two-stage pipeline described in the
paper (static-embedding retrieval of the top K = 10 candidates, then an MLP or
Bi-LSTM reranker) and the single-stage retrieval baseline. It repeats the whole
split-and-train procedure for five seeds and reports t-based 95 % intervals (df = 4):

```bash
cd evaluation
python3 evaluate_pipeline.py --data ../benchmark/egov_concept_pairs.csv \
                             --vocab ../benchmark/concept_vocabulary.csv \
                             --out results --seeds 5 --k 10 --epochs 3
```

It requires PyTorch. `evaluate_baselines.py` is a dependency-light alternative
(TF-IDF and PPMI-SVD retrieval only) for readers who do not want to install it.

Recorded output (`evaluation/results/pipeline_results.json`):

| Configuration | Top-1 % (95% CI) | Recall@5 % | MRR |
|---|---|---|---|
| Static retrieval, all 24 candidates | 66.9 (65.6-68.1) | - | - |
| + MLP head over top-10 | 87.5 (85.8-89.2) | 94.7 | 0.93 |
| + Bi-LSTM head over top-10 | 95.2 (94.4-96.0) | 95.2 | 0.95 |
| Retrieval recall@10 (ceiling for stage 2) | 95.2 (94.4-96.0) | - | - |
| Bi-LSTM, Corda held out (no retraining) | 55.9 (52.9-58.9) | 79.4 | - |

Read these with the caveat stated in the paper: the end-to-end result sits on the
retrieval ceiling. Each source description is a rendered variant of the same gloss that
appears in the candidate text, so source and gold candidate share vocabulary by
construction. The benchmark tests that the pipeline is wired correctly and that
retrieval bounds it; it does not estimate accuracy on agency documentation, and the
gap between the MLP and the Bi-LSTM is a property of this benchmark rather than a
general claim about encoder families.

## 4. Figures

| Script | Output |
|---|---|
| `fig1_logical_structure.py` | Fig. 1 |
| `fig2_problem_definition.py` | Fig. 2 |
| `fig3_architecture.py` | Fig. 3 |
| `fig4_uml_class_diagram.py` | Fig. 4 |
| `fig5_translation_rule.py` | Fig. 5 |
| `fig6_pipeline.py` | Fig. 6 |
| `fig7_sequence.py` | Fig. 7 |
| `fig8_dev_effort.py` | Fig. 8 |
| `fig9_tps.py` | Fig. 9 |
| `fig10_latency.py` | Fig. 10 |
| `fig11_workflow.py` | Fig. 11 |

Each script is drawn at the manuscript's text-column width (5.03 in) so that the
type is reproduced at the designed size. Run any script from this directory; it
writes a 400 dpi PNG and a vector PDF. Fig. 9 plots the throughput means and 95 %
intervals reported in Section 6.3; Figs. 10 and 11 plot the latency and workflow
measurements of Section 6.

## 5. What is not included

- the 5,240-pair annotated concept-mapping corpus (not used in this manuscript);
- raw per-run performance logs (not retained; Section 6 reports retained summaries).

## 6. TLA+ module

`tla/DSALCoordination.tla` and `tla/DSALCoordination.cfg` model the coordination logic
of Section 5.3: Request, Translate, Prepare, Commit, Respond and Abort over three
organizations, two platforms and two interleaved requests, with one lock and one commit
flag per (platform, request). Permissions are a fixed table: organisation 3 may start
either flow, organisation 1 only flow 1, organisation 2 only flow 2.

Run it with Java 11+ and `tla2tools.jar` release v1.7.1, which ships TLC 2.16:

```bash
java -XX:+UseParallelGC -cp tla2tools.jar tlc2.TLC \
     -config DSALCoordination.cfg -cleanup DSALCoordination.tla
```

The configuration contains `CHECK_DEADLOCK FALSE`. Terminal states, in which every
request has responded or aborted (576 of the reachable states), have no successor
action by construction, so a deadlock check would report them as errors. Do not add
`-deadlock` on the command line: in TLC 2.16 that flag switches the check off, so the
reported result would then depend on an undocumented switch rather than on the
configuration file.

Recorded run (`tla/tlc_output.txt`, TLC 2.16, about 9 s on one core): 55,569 states
generated, 22,801 distinct states, search depth 15, no violation of
SemanticConsistency, NoPermissionLeakage or Termination. The log also reports 45,602 total
distinct states while checking temporal properties; that figure is the state graph
augmented with the property automaton (two branches), not a second model, and the count
to quote is the 22,801 above.

Termination is structural in this model: status only advances and the lock and commit
flags only move from false to true, so the state graph is acyclic. The liveness check
confirms that no interleaving leaves a request in a non-terminal state; it does not
exercise contention, because the two requests share no lock.

Non-vacuity checks (each is a one-line edit of the released module):

| Mutation | Counterexample | Violating states |
|---|---|---|
| remove the role check from `Prepare` | `NoPermissionLeakage` | 12,224 of 42,849 |
| remove the refinement constraint from `Translate` | `SemanticConsistency` | 61,744 of 87,025 |

Scope: no coordinator crash or failover, no partitions, no lock expiry, and no Case
(3) partial commit. Raising `MaxReq` enlarges the state space sharply.

## 7. Licence

- Data (`*.csv`, `*.json`): CC BY 4.0.
- Code (`*.py`): MIT.

## 8. Citation

If you use the benchmark, cite the manuscript and this package:

> DSAL-Egov Concept Benchmark v1 (2026). Supplementary material to *A
> Domain-Specific Abstraction Layer for Interoperability across Heterogeneous
> Blockchain Platforms in E-Government Systems*.
