# Approximation Error Upper and Lower Bounds for Hölder Class with Transformers

Independent, source-pinned audit for **Xin He, Yuling Jiao, Xiliang Lu, and Jerry Zhijian Yang**, “Approximation Error Upper and Lower Bounds for Hölder Class with Transformers” (ICML 2026; [arXiv:2605.07463v2](https://arxiv.org/abs/2605.07463v2)). The challenge contract identifies four claims with a maximum of eight points. This repository makes the evidence boundary explicit: one reduced constructive experiment is toy evidence, one specific lower-bound proof route is falsified, and the remaining claims are unverified. No challenge points are claimed.

Paper pages: [arXiv abstract](https://arxiv.org/abs/2605.07463v2) · [HTML paper](https://arxiv.org/html/2605.07463) · [OpenReview submission mWBxEAq9lv](https://openreview.net/forum?id=mWBxEAq9lv) · [ICML 2026 poster](https://icml.cc/virtual/2026/poster/61835)

Machine-readable overall verdict: PARTIAL_CLAIM_1_TOY_CLAIM_2_PINNED_ROUTE_FALSIFIED_CLAIMS_3_TO_4_UNVERIFIED.
Publication boundary: publication_allowed=false for a complete reproduction or
score; this repository publishes scoped toy and proof-route-falsification
evidence only. score_claim=false and official_author_endorsement=false.

## Outcome at a glance
The arXiv source and PDF audited here are retained under `evidence/source/` and checked by `evidence/source/SHA256SUMS`. The source-archive audit did not locate an author-maintained executable implementation, dataset, or checkpoint, so the experiments below are explicitly labeled independent or clean-room audits.

## Outcome at a glance

| Claim | Paper statement | Repository evidence | Current verdict |
| --- | --- | --- | --- |
| 1 | Theorem 4.1: at most (O(\varepsilon^{-d_0/\alpha})) Transformer blocks approximate every bounded Hölder-(\alpha) function in (L^2), under (d_0>2\alpha). | Source-condition/rate probe plus a five-seed, reduced (d_0=3,\alpha=1) Transformer-style approximation toy. | **Toy evidence; theorem unverified.** |
| 2 | Theorem 5.3: a VC-dimension argument gives (D=\Omega(\varepsilon^{-d_0/(4\alpha)})) blocks. | Continuous triangular-tent counterexample to the pinned proof’s (L^2\Rightarrow L^\infty) sign-preservation step. | **Falsified for the pinned proof route; alternative proofs not ruled out.** |
| 3 | The upper/lower block exponents leave a factor-of-four gap, (\varepsilon^{-d_0/(4\alpha)}\lesssim D\lesssim\varepsilon^{-d_0/\alpha}). | Algebraic comparison is stated in the contract, but no independent tightness audit is stored. | **Unverified.** |
| 4 | Theorem 6.2: the regression excess-risk rate is (N^{-\alpha/(2d_0+\alpha)}\log N + N^{-\alpha/(2d_0+\alpha)}), up to the optimization term. | No independent regression protocol or statistical-rate audit. | **Unverified.** |

## How the paper produces each claim

1. **Upper bound (Theorem 4.1).** The paper reshapes a Hölder function into a sequence-function class, approximates it by a piecewise-constant function, and then realizes the intermediate map with quantization, contextual mapping, and value mapping modules. The construction keeps a standard Softmax/ReLU/residual Transformer, counts the required blocks, and obtains the (O(\varepsilon^{-d_0/\alpha})) rate. The repository checks the stated assumptions and rate arithmetic, then runs a deliberately smaller clean-room approximation experiment; it does not rederive the construction or establish the universal quantifier.

2. **VC lower bound (Theorem 5.3).** The paper bounds the operations and parameters of the Transformer, applies a VC-dimension upper bound, and argues that approximating a special Hölder classification family preserves signs on enough witnesses to imply shattering. `src/claim2_l2_to_linf_counterexample.py` targets one essential proof step: boundedness on a compact domain does not make (L^2) and (L^\infty) norms equal. The result therefore falsifies the displayed proof route’s sign-preservation inference, not every possible lower-bound theorem.

3. **Exponent-gap statement.** The paper compares the upper exponent from Theorem 4.1 with the lower exponent from Theorem 5.3 and records the remaining factor-of-four gap as an open tightening opportunity. This repository records the contract statement but has not independently audited the asymptotic tightness analysis.

4. **Regression rate (Theorem 6.2).** The paper combines the approximation bound with a finite-sample statistical-error bound, chooses the model depth and auxiliary radius as functions of (N), and derives the excess-risk rate. This repository contains no regression data, estimator implementation, or rate-scaling experiment, so the claim remains unverified.

## Evidence and reproduction paths

The original challenge contract, paper snapshot, and source hashes are in `contract/` and `evidence/source/`.

### Claim 1 — reduced constructive toy

`src/claim1_direct_cpu_audit.py` confirms that the pinned source contains the conditions (d_0>2\alpha), the (O(\varepsilon^{-d_0/\alpha})) rate, and the (L^2) error criterion. At (d_0=3,\alpha=1), halving (\varepsilon) changes the rate proxy from 64 to 512, an eight-fold change. This is a transcription/rate audit, not a proof.

`src/claim1_constructive_transformer_toy.py` then uses a bounded Lipschitz target on ([0,1]^3), 4,000 training samples, 8,000 independent test samples, one explicit scalar-Q/K/V self-attention residual encoder, and a trained ReLU readout. Widths are 16, 64, and 256; five independent seeds are retained. The permuted-training-label control uses the same architecture and data inputs with training labels randomly permuted.

| Width | Mean held-out (L^2) error | Mean permuted-label control | Control worse in all 5 seeds |
| ---: | ---: | ---: | :---: |
| 16 | 0.307127 | 0.462269 | yes |
| 64 | 0.200269 | 0.471327 | yes |
| 256 | 0.093667 | 0.475721 | yes |

The evidence shows a useful increasing-width trend on one reduced target. It is **toy** evidence: it does not verify approximation of every Hölder function, the paper’s source construction, or the asymptotic block-count law.

### Claim 2 — proof-route counterexample

`src/claim2_l2_to_linf_counterexample.py` evaluates the continuous bounded family

```text
f_w(x) = max(1 - |x - 1/2| / w, 0),  x in [0, 1].
```

For every tested width, (\|f_w\|_\infty=1) while (\|f_w\|_2=\sqrt{2w/3}). The retained witness (w=0.0125) has (L^2=0.0912871<0.1) but (L^\infty=1); dense quadrature agrees with the analytic value to about (1.5\times10^{-10}). A constant-function control has equal norms, confirming that this special case cannot justify the universal inference. Raw JSON, logs, and checksums are in `outputs/claim2_l2_to_linf_counterexample/`.

## Reproduce the retained evidence

These commands assume the pinned environment has been installed from `requirements.txt`:

```bash
# Source and generated-artifact integrity
(cd evidence/source && sha256sum -c SHA256SUMS)

# Claim 1 source-condition/rate audit
.venv/bin/python src/claim1_direct_cpu_audit.py

# Claim 1 reduced constructive run; repeat for the five retained seeds if needed
for seed in 20260801 20260802 20260803 20260804 20260805; do
  .venv/bin/python src/claim1_constructive_transformer_toy.py \
    --seed "$seed" --out outputs/claim1_constructive_toy
done
(cd outputs/claim1_constructive_toy && sha256sum -c SHA256SUMS)

# Claim 2 proof-route counterexample
.venv/bin/python src/claim2_l2_to_linf_counterexample.py \
  --out outputs/claim2_l2_to_linf_counterexample
(cd outputs/claim2_l2_to_linf_counterexample && sha256sum -c SHA256SUMS)

# Existing deterministic tests
.venv/bin/python -m pytest -q
```

The commands reproduce finite numerical checks only. They cannot turn a toy experiment into a proof of a universal theorem.

## Audit dossier

The durable records for this scoped audit are:

- STATUS.md — current phase, claim boundary, and publication state.
- CLAIM_EVIDENCE.md — claim-to-code-to-output production paths.
- SOURCE_AUDIT.md — paper, source, and provenance pins.
- ENVIRONMENT.md — recorded runtime and compute scope.
- REPORT.md — concise result and limitation report.
- BRANCH_AUDIT.md — branch, history, and attribution audit.
- claims.json — machine-readable scoped verdicts.
- reproduction_verdicts.json — per-claim verdicts, production paths, evidence,
  and publication boundary.
- AUTONOMOUS_STATE.json — resumable audit state and canonical attribution
  checkpoint.
- EVIDENCE_MANIFEST.json — content and output hashes.
- verify_final.py — read-only final-state verifier.

These records are an independent reproduction dossier, not a complete theorem
proof or an author endorsement. The strongest results are a reduced
five-seed approximation experiment and a proof-route counterexample.

## Repository map

| Path | Purpose |
| --- | --- |
| `contract/` | Frozen ICML 2026 challenge metadata and the four live claims. |
| `evidence/source/` | Pinned arXiv source/PDF and SHA-256 manifest. |
| `src/claim1_direct_cpu_audit.py` | Deterministic audit of Claim 1’s source conditions and rate arithmetic. |
| `src/claim1_constructive_transformer_toy.py` | Reduced clean-room self-attention plus ReLU approximation experiment. |
| `src/claim2_l2_to_linf_counterexample.py` | Continuous counterexample to the pinned Claim 2 norm inference. |
| `outputs/claim1_constructive_toy/` | Five-seed CSV/JSON/log evidence, summary, and checksums. |
| `outputs/claim2_l2_to_linf_counterexample/` | Counterexample result, stdout, run log, and checksums. |
| `logbook/` | Claim-by-claim audit narrative for the next researcher. |
| `STATUS.md` | Current publication and claim status. |
| `AUTONOMOUS_STATE.json` | Machine-readable continuation state and evidence boundaries. |

## Branches and attribution

The repository is intentionally main-only. There are no experiment branches and no former `orx/*` branches to interpret. `branch-audit.md` records the branch and identity audit.

All reachable commits are normalized to:

```text
MachineLearning-Nerd <MachineLearning-Nerd@users.noreply.github.com>
```

## Citation

```bibtex
@article{he2026approximation,
  title         = {Approximation Error Upper and Lower Bounds for Hölder Class with Transformers},
  author        = {He, Xin and Jiao, Yuling and Lu, Xiliang and Yang, Jerry Zhijian},
  journal       = {arXiv preprint arXiv:2605.07463},
  year          = {2026},
  eprint        = {2605.07463},
  archivePrefix = {arXiv},
  primaryClass  = {cs.LG}
}
```

## Thank you

Thank you to Xin He, Yuling Jiao, Xiliang Lu, and Jerry Zhijian Yang for developing and sharing this theoretical study of Transformer approximation bounds. This independent audit is intended to make the paper’s assumptions, proof dependencies, and current reproduction evidence easier for other researchers to inspect; the audit verdicts are not author claims or author-maintained results.

## Current limitations and next steps

- Claim 1 needs a source-faithful construction audit and broader function-family/accuracy scaling before it can move beyond toy status.
- Claim 2 needs an independent review of the remaining lower-bound argument after the identified (L^2\)-to-(L^\infty) proof gap; the current result is scoped to the pinned route.
- Claims 3 and 4 need separate asymptotic and regression audits.
- `publication_allowed` remains `false` until the full four-claim audit is complete.
