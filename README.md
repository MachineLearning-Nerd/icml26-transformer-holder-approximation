# Independent reproduction: Transformer Hölder approximation bounds

Pinned-source, CPU-executable reproduction workspace for ICML 2026 paper `mWBxEAq9lv`. Claim 1 now also has a local-CPU clean-room constructive **toy** experiment (`outputs/claim1_constructive_toy/`): an explicit self-attention encoder plus ReLU readout approximates a bounded Lipschitz d0=3 target over five independent seeds with a label-permutation negative control. It is not a universal theorem verification or source construction, and no challenge points are claimed.

```bash
.venv/bin/python -m pytest -q
.venv/bin/python src/claim1_direct_cpu_audit.py
.venv/bin/python src/claim1_constructive_transformer_toy.py --seed 20260801 --out outputs/claim1_constructive_toy
sha256sum -c evidence/source/SHA256SUMS
```

## Claim 2

A direct executable counterexample falsifies the pinned theorem proof route: `logbook/claim-2.md`.
