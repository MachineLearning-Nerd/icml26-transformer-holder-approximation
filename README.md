# Independent reproduction: Transformer Hölder approximation bounds

Pinned-source, CPU-executable reproduction workspace for ICML 2026 paper `mWBxEAq9lv`. This initial checkpoint audits Claim 1's exact theorem conditions and rate algebra; it is **not** an end-to-end constructive Transformer approximation and earns no claimed challenge points.

```bash
python3 -m pytest -q
python3 src/claim1_direct_cpu_audit.py
sha256sum -c evidence/source/SHA256SUMS
```
