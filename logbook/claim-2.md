# Claim 2 — VC-dimension lower bound

**Live claim:** Theorem 5.3 states that a Transformer approximating the Hölder class to error \(\epsilon\) needs at least \(\Omega(\epsilon^{-d_0/(4\alpha)})\) blocks, derived through VC-dimension analysis.

## Source-faithful direct audit

The pinned source proof (`evidence/source/arxiv_source.tar.gz`, `Approximation_rates_Transformers.tex`, lower-bound proof) makes this inference: because \(g_\phi\) and \(f_\phi\) are bounded on compact \([0,1]^{d_0}\), their \(L^2\) and \(L^\infty\) metrics are equal. It then uses an \(L^2\) approximation statement as a uniform pointwise error bound to preserve signs of all bump witnesses and infer shattering.

`src/claim2_l2_to_linf_counterexample.py` independently executes a continuous bounded counterexample family on compact \([0,1]\):
\[
f_w(x)=\max(1-|x-1/2|/w,0).
\]
It has \(\|f_w\|_\infty=1\) and \(\|f_w\|_2=\sqrt{2w/3}\). For the retained concrete witness \(w=0.0125\), \(\|f_w\|_2=0.0912871<0.1\) while \(\|f_w\|_\infty=1\). Dense numerical quadrature independently matches the analytic norm for six widths; the ratio diverges as \(w\to0\). A constant-function control has equal norms, showing why that special case does not justify the universal assertion.

Run and verify:
```bash
.venv/bin/python src/claim2_l2_to_linf_counterexample.py --out outputs/claim2_l2_to_linf_counterexample
(cd outputs/claim2_l2_to_linf_counterexample && sha256sum -c SHA256SUMS)
.venv/bin/python -m pytest -q
```
Raw JSON, stdout, command log, and checksums are retained under `outputs/claim2_l2_to_linf_counterexample/`.

## Verdict

**falsified (proof route).** The compactness/boundedness \(L^2=L^\infty\) inference used to obtain the sign/shattering step is false. This falsifies the claim that the pinned displayed VC-dimension proof establishes the stated lower bound. It does **not** prove that no alternative proof of a Transformer lower bound exists.
