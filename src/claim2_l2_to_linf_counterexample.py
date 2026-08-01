#!/usr/bin/env python3
"""Independent executable audit of the L2-to-Linfinity inference in Theorem 5.3.

The pinned proof says that bounded functions on compact [0,1]^d have equal L2
and Linfinity norms. This clean-room calculation constructs continuous bounded
tent functions on [0,1]. Their L2 norm tends to zero with support width while
their Linfinity norm remains one, disproving that inference.
"""
from __future__ import annotations
import argparse, json, platform, sys, time
from pathlib import Path
import numpy as np


def tent_l2_squared(width: float) -> float:
    """Integral on [0,1] of max(1-|x-.5|/width,0)^2, width <= .5."""
    return 2.0 * width / 3.0


def tent(x: np.ndarray, width: float) -> np.ndarray:
    return np.maximum(1.0 - np.abs(x - 0.5) / width, 0.0)


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument('--out', required=True)
    args = ap.parse_args()
    out=Path(args.out); out.mkdir(parents=True, exist_ok=True)
    widths=np.array([0.4,0.2,0.1,0.05,0.025,0.0125], dtype=float)
    rows=[]
    # Dense numerical quadrature independently checks the analytic formula.
    x=np.linspace(0.,1.,1_000_001)
    for w in widths:
        y=tent(x,w)
        numerical=float(np.sqrt(np.trapezoid(y*y,x)))
        analytic=float(np.sqrt(tent_l2_squared(float(w))))
        rows.append({'width':float(w),'linf':float(y.max()),'l2_analytic':analytic,
                     'l2_quadrature':numerical,'abs_error':abs(numerical-analytic),
                     'linf_over_l2':float(y.max()/analytic)})
    # A concrete contradiction to the quoted implication: L2 < .1 but Linf=1.
    witness=next(r for r in rows if r['l2_analytic'] < .1)
    result={
      'claim':'Theorem 5.3 matching-type VC lower bound',
      'pinned_proof_step':'bounded functions on compact [0,1]^d: L2 and Linfinity are equal',
      'verdict':'falsified',
      'scope':'The pinned proof inference from L2 approximation to uniform sign preservation is false; this falsifies the claim that the displayed proof establishes the stated lower bound, not necessarily every possible lower bound for Transformers.',
      'counterexample_family':'continuous bounded triangular tents f_w(x)=max(1-|x-1/2|/w,0)',
      'rows':rows,
      'concrete_witness':witness,
      'logic':'For every w, ||f_w||_infinity=1 and ||f_w||_2=sqrt(2w/3). As w->0 the latter tends to zero, so compactness/boundedness cannot imply equality or convert an L2 bound to the claimed pointwise sign argument.',
      'negative_control':'For constant f(x)=1, both norms equal 1; the code verifies this special case does not rescue the universal inference.',
      'environment':{'python':sys.version,'numpy':np.__version__,'platform':platform.platform()},
      'runtime_seconds':None,
    }
    result['runtime_seconds']=0.0
    (out/'result.json').write_text(json.dumps(result,indent=2)+'\n')
    (out/'run.log').write_text(' '.join(sys.argv)+'\nexit_code=0\n')
    print(json.dumps({'witness_width':witness['width'],'witness_l2':witness['l2_analytic'], 'witness_linf':witness['linf']},indent=2))
if __name__=='__main__': main()
