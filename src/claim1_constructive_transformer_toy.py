"""Local CPU clean-room constructive Transformer-style Hölder approximation experiment.

This is deliberately a reduced-dimensional empirical test, not a proof of Theorem 4.1.
A deterministic self-attention encoder is followed by a trained ReLU readout.  We use an
explicit bounded Lipschitz target on [0,1]^3 and independent train/test draws.  The
implementation retains a label-permutation negative control.
"""
from __future__ import annotations
import argparse, csv, json, platform, sys
from pathlib import Path
import numpy as np

ROOT = Path(__file__).resolve().parents[1]


def target(x: np.ndarray) -> np.ndarray:
    """Bounded 2π-Lipschitz (up to a fixed constant) target on [0,1]^3."""
    return (np.sin(2*np.pi*x[:,0]) + .5*np.cos(2*np.pi*x[:,1]) + .25*np.sin(4*np.pi*x[:,2])) / 1.75


def encode_attention(x: np.ndarray) -> np.ndarray:
    """One explicit single-head self-attention/residual encoder, no learned oracle."""
    tokens = x[:, :, None]                         # n, L=3, d=1
    pos = np.array([[-.15], [0.0], [.15]])
    z = tokens + pos[None, :, :]
    q = z * 1.1; k = z * .9; v = z                 # scalar Q,K,V maps
    logits = q * np.swapaxes(k, 1, 2) / np.sqrt(1.)
    logits -= logits.max(axis=2, keepdims=True)
    weights = np.exp(logits); weights /= weights.sum(axis=2, keepdims=True)
    attended = weights @ v
    # standard residual-plus-ReLU feed-forward path, then flatten readout tokens
    h = attended + z
    ff = np.maximum(0., 1.25*h - .05) - .35*np.maximum(0., -.8*h + .12)
    return np.concatenate((h, ff), axis=2).reshape(x.shape[0], -1)


def fit_predict(xtr, ytr, xte, width: int, seed: int):
    rng = np.random.default_rng(seed + 1009*width)
    ztr, zte = encode_attention(xtr), encode_attention(xte)
    scale = 1 / np.sqrt(ztr.shape[1])
    W = rng.normal(0, scale, size=(ztr.shape[1], width))
    b = rng.uniform(-1, 1, size=(width,))
    phi = np.maximum(0, ztr @ W + b)
    phite = np.maximum(0, zte @ W + b)
    # ridge is fitted solely on train targets
    lam = 1e-6
    A = phi.T @ phi + lam*np.eye(width)
    coef = np.linalg.solve(A, phi.T @ ytr)
    return phite @ coef


def run(seed: int, ntrain: int, ntest: int, widths: list[int]):
    rng = np.random.default_rng(seed)
    xtr = rng.random((ntrain, 3)); xte = rng.random((ntest, 3))
    ytr, yte = target(xtr), target(xte)
    rows=[]
    for width in widths:
        pred=fit_predict(xtr,ytr,xte,width,seed)
        mse=float(np.mean((pred-yte)**2)); l2=float(np.sqrt(mse))
        # destructive control: same fitted architecture, independently permuted train labels
        perm=rng.permutation(ntrain)
        wrong=fit_predict(xtr,ytr[perm],xte,width,seed+77)
        control=float(np.sqrt(np.mean((wrong-yte)**2)))
        rows.append({'seed':seed,'width':width,'l2_test_error':l2,'mse_test_error':mse,
                     'permuted_label_l2_error':control,'control_degrades':bool(control>l2)})
    return rows


def main():
    p=argparse.ArgumentParser(); p.add_argument('--seed',type=int,default=20260801); p.add_argument('--ntrain',type=int,default=4000); p.add_argument('--ntest',type=int,default=8000); p.add_argument('--widths',default='16,64,256'); p.add_argument('--out',type=Path,default=ROOT/'outputs/claim1_constructive_toy')
    a=p.parse_args(); widths=[int(v) for v in a.widths.split(',')]; a.out.mkdir(parents=True,exist_ok=True)
    rows=run(a.seed,a.ntrain,a.ntest,widths)
    with (a.out/f'rows_seed{a.seed}.csv').open('w',newline='') as f:
        w=csv.DictWriter(f,fieldnames=rows[0].keys()); w.writeheader(); w.writerows(rows)
    meta={'experiment':'clean-room one-attention-block plus ReLU-readout approximation','claim_scope':'reduced d0=3 alpha=1 bounded Lipschitz target; toy empirical evidence, not a universal theorem proof','seed':a.seed,'ntrain':a.ntrain,'ntest':a.ntest,'widths':widths,'device':'local CPU','python':sys.version,'numpy':np.__version__,'platform':platform.platform(),'rows':rows}
    (a.out/f'meta_seed{a.seed}.json').write_text(json.dumps(meta,indent=2)+'\n')
    print(json.dumps(meta,indent=2))

if __name__=='__main__': main()
