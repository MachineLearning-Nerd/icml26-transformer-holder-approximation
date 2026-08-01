# Claim 1 — Transformer Hölder approximation upper bound

**Live claim:** Theorem 4.1 says a Transformer with at most \(\widetilde O(\epsilon^{-d_0/\alpha})\) blocks approximates every bounded Hölder-\(\alpha\) function of a \(d_0\)-dimensional input to L2 error below \(\epsilon\).

## New executable evidence

A clean-room local-CPU constructive experiment is retained at `outputs/claim1_constructive_toy/`. It runs a one-head self-attention residual encoder and trained ReLU readout on a bounded Lipschitz `d0=3, alpha=1` target. Across five independent train/test/feature seeds, held-out L2 error falls from 0.3071 (width 16) to 0.09367 (width 256); a permuted-training-label control is worse in every seed×width cell (mean control error 0.4623–0.4757).

Exact commands, raw CSV/JSON/logs, environment, source location, and hashes are in `outputs/claim1_constructive_toy/audit.md` and `SHA256SUMS`.

## Verdict

**toy.** This is real local executable approximation evidence, but not a universal proof, source construction, or theorem-scale block-complexity validation. It cannot by itself verify/falsify Theorem 4.1.
