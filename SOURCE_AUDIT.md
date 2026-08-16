# Source and provenance audit

## Paper identity

- Title: *Approximation Error Upper and Lower Bounds for Hölder Class with Transformers*
- Authors: Xin He, Yuling Jiao, Xiliang Lu, and Jerry Zhijian Yang
- arXiv: [2605.07463v2](https://arxiv.org/abs/2605.07463v2)
- OpenReview: [mWBxEAq9lv](https://openreview.net/forum?id=mWBxEAq9lv)
- Submission number: 9121
- Live snapshot: outputs/live/20260801T083019Z

## Pinned source

| artifact | path | SHA-256 |
|---|---|---|
| arXiv source archive | evidence/source/arxiv_source.tar.gz | 5251830a4370729109be794b7c5c38ea3ab6976073b9044a01d0f1bccde9ba4f |
| paper PDF | evidence/source/arxiv.pdf | 801cf7d435d1075c3d792b8d6dcb5cc3346e64b40411a6cee6864e7f3b0aaafe |
| source contract | contract/contract_manifest.json | recorded in EVIDENCE_MANIFEST.json |
| live claim text | contract/live_claims.json | recorded in EVIDENCE_MANIFEST.json |

The theorem statements and verdict boundaries follow the pinned live contract
and source archive. The source archive audit did not locate an author-maintained
executable implementation, dataset, or checkpoint. Claim 1 is therefore a
clean-room reduced experiment, not a rerun of an official artifact.

## Source locations

- Theorem 4.1 assumptions and upper-rate expression: the pinned
  Approximation_rates_Transformers.tex.
- Theorem 5.3 lower-bound proof route: the pinned source's lower-bound section.
- The local source-condition producer: src/claim1_direct_cpu_audit.py.
- The local constructive producer: src/claim1_constructive_transformer_toy.py.
- The proof-route counterexample: src/claim2_l2_to_linf_counterexample.py.

## Provenance boundary

Paper and contract files are pinned inputs. Numerical outputs are independently
generated local artifacts. No author review, endorsement, score, or full
theorem reproduction is implied.
