# Claim 1 Attempt 1 — direct source/CPU rate audit

Exact contract: Theorem 4.1 asserts at most `O(epsilon^{-d0/alpha})` Transformer blocks for bounded Hölder-alpha functions, error below epsilon.

Pinned source `Approximation_rates_Transformers.tex` contains the theorem at lines 262–267. The executable CPU probe uses `d0=3, alpha=1`, satisfying `d0 > 2 alpha`: changing epsilon from .25 to .125 changes the rate proxy from 64 to 512 (8x), exactly `2^(d0/alpha)`.

Verdict: **inconclusive**. This validates the literal rate transcription/conditions but is not a construction or independent proof; next action is a clean-room low-dimensional Transformer experiment using the stated L2 metric and fixed seeds.
