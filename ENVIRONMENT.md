# Environment and compute record

## Recorded runs

Claim 1 constructive toy:

- Device: local CPU
- Python: 3.14.5
- NumPy: 2.4.6
- Platform: Linux-7.0.9-arch2-1-x86_64-with-glibc2.43
- Seeds: 20260801 through 20260805
- Train/test samples: 4,000 / 8,000
- Target dimension: d0=3, alpha=1
- Readout widths: 16, 64, 256

Claim 2 counterexample:

- Device: local CPU
- Python: 3.14.5
- NumPy: 2.4.6
- Platform: Linux-7.0.9-arch2-1-x86_64-with-glibc2.43
- Quadrature grid: 1,000,001 points

## Reproduction commands

~~~bash
.venv/bin/python src/claim1_direct_cpu_audit.py
for seed in 20260801 20260802 20260803 20260804 20260805; do
  .venv/bin/python src/claim1_constructive_transformer_toy.py \
    --seed "$seed" --out outputs/claim1_constructive_toy
done
.venv/bin/python src/claim2_l2_to_linf_counterexample.py \
  --out outputs/claim2_l2_to_linf_counterexample
~~~

The committed outputs are the audited records. Re-running may change timings
or floating-point least-squares values on another machine.

## Compute policy

Only local CPU or local GPU execution is in scope. No Hugging Face Jobs, paid
remote compute, or external GPU service is used for this dossier.
