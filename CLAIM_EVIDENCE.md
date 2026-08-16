# Claim-to-evidence ledger

This ledger keeps theorem statements, executable producers, raw artifacts, and
scope boundaries separate.

## Claim 1 — Hölder approximation upper bound

Paper target: Theorem 4.1, the upper block-count rate for approximating every
bounded Hölder-alpha function.

Production path:

1. src/claim1_direct_cpu_audit.py reads the pinned source archive and checks the
   theorem conditions and rate expression. For d0=3 and alpha=1, halving
   epsilon changes the rate proxy from 64 to 512.
2. src/claim1_constructive_transformer_toy.py generates a bounded Lipschitz
   target on [0,1]^3, encodes it with one explicit scalar-Q/K/V attention
   residual block, and fits a ReLU readout on train data only.
3. Five seeds use 4,000 train and 8,000 test samples at widths 16, 64, and
   256. Each has a permuted-label control with the same input architecture.
4. outputs/claim1_constructive_toy/summary.json aggregates the 15 normal and
   15 control cells; raw CSV, metadata, logs, and SHA256SUMS are retained.
5. tests/test_claim1_constructive.py checks finite encoder output, control
   degradation, and bounded target behavior.

Recorded means:

| width | mean held-out L2 | mean permuted-label L2 |
|---:|---:|---:|
| 16 | 0.3071274077 | 0.4622693141 |
| 64 | 0.2002687395 | 0.4713274960 |
| 256 | 0.0936669784 | 0.4757207771 |

Verdict: **TOY_REDUCED_CONSTRUCTIVE_APPROXIMATION**. The run shows an increasing
width trend on one reduced target and the control degrades in all 15 cells. It
does not verify the universal quantifier, the paper's source construction, or
the asymptotic block-count theorem.

## Claim 2 — VC lower bound

Paper target: Theorem 5.3 and its VC-dimension lower-bound proof.

Production path:

1. src/claim2_l2_to_linf_counterexample.py defines continuous triangular tents
   on [0,1], with analytic L2 norm sqrt(2w/3) and Linfinity norm 1.
2. Dense numerical quadrature checks the analytic norm for widths
   0.4, 0.2, 0.1, 0.05, 0.025, and 0.0125.
3. The retained witness w=0.0125 has L2 0.0912870929 and Linfinity 1.0;
   outputs/claim2_l2_to_linf_counterexample/result.json records the rows,
   logs, stdout, and hashes.
4. tests/test_claim2_l2_to_linf.py checks the formula and the witness.

Verdict: **FALSIFIED_PINNED_L2_LINF_PROOF_ROUTE**. The displayed inference that
bounded functions on a compact domain have equal L2 and Linfinity norms is
false, so the sign-preservation step in that proof route does not establish the
lower bound. This does not rule out an alternative lower-bound proof.

## Claim 3 — exponent gap

Paper target: the factor-of-four gap between the upper and lower exponents.
The repository records the contract statement but contains no independent
tightness or asymptotic audit. Verdict: **UNVERIFIED_NOT_STARTED**.

## Claim 4 — regression rate

Paper target: Theorem 6.2's nonparametric regression excess-risk rate. No
regression data, estimator, or rate-scaling experiment is present. Verdict:
**UNVERIFIED_NOT_STARTED**.

## Boundary

The repository supports a finite toy experiment and a specific proof-route
counterexample. It does not claim theorem verification, full-paper points, or
that the printed lower-bound theorem is impossible by every method.
