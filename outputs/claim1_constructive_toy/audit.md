# Claim 1 Attempt 2 — local constructive Transformer-style approximation (toy)

**Exact live claim.** Theorem 4.1 states that a Transformer with at most \(\widetilde O(\epsilon^{-d_0/\alpha})\) blocks can approximate every bounded Hölder-\(\alpha\) function of a \(d_0\)-dimensional input to L2 error below \(\epsilon\).

**Source pin.** `evidence/source/SHA256SUMS` pins arXiv:2605.07463 source/PDF. `Approximation_rates_Transformers.tex`, Theorem 4.1 (lines 262–267 in the pinned source) states \(\alpha\in(0,1], d_0>2\alpha\), the L2 metric, and the block upper-bound exponent. The proof sketch describes a self-attention contextual-mapping stage (lines 282–285).

**Pre-registered reduced protocol.** This clean-room local-CPU experiment uses `d0=3, alpha=1`, a bounded Lipschitz target on `[0,1]^3`, 4,000 IID training inputs, 8,000 independently drawn test inputs, five fixed seeds, and widths 16/64/256. `src/claim1_constructive_transformer_toy.py` executes an explicit scalar-Q/K/V self-attention residual encoder over three input tokens, followed by a ReLU readout fitted using training data only. This is a real executable Transformer-style approximation experiment, but it is **not** the theorem's source construction, a universal quantification over the Hölder class, or a block-count scaling proof.

**Command.**
```bash
.venv/bin/python src/claim1_constructive_transformer_toy.py --seed 20260801 --out outputs/claim1_constructive_toy
.venv/bin/python -m pytest -q
(cd outputs/claim1_constructive_toy && sha256sum -c SHA256SUMS)
```

**Result.** From `summary.json`, mean held-out L2 error across five independent data/feature seeds was 0.3071 (width 16), 0.2003 (width 64), and 0.09367 (width 256); corresponding label-permutation negative-control errors were 0.4623, 0.4713, and 0.4757. The control degraded on all 15 seed×width cells. Thus the direct construction has a measured increasing-width approximation trend on this fixed target, rather than merely source-rate arithmetic.

**Verdict: toy.** The experiment is reduced scale and covers one target/function family, not every bounded Hölder function or the theorem's asymptotic number-of-blocks result. It must not be labeled verified/falsified for the live theorem. Raw seed CSV/JSON/logs and their SHA-256 manifest are in this directory.
