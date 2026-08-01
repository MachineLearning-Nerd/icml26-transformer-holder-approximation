"""Deterministic CPU audit of Claim 1's stated rate and source conditions."""
import re, tarfile
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
def upper_blocks(epsilon,d0,alpha): return epsilon ** (-d0/alpha)
def audit():
    with tarfile.open(ROOT/'evidence/source/arxiv_source.tar.gz','r:gz') as tf:
        tex=tf.extractfile('Approximation_rates_Transformers.tex').read().decode('utf-8')
    required=['d_{0}>2\\alpha','\\mathcal{O}(\\varepsilon^{-\\frac{d_{0}}{\\alpha}})','\\norm{f-g}_{2}<\\varepsilon']
    found={x:x in tex for x in required}
    # Fixed alpha=1,d0=3 satisfies d0>2alpha; halving eps should multiply rate proxy by 8.
    coarse, fine=upper_blocks(.25,3,1),upper_blocks(.125,3,1)
    return {'source_conditions_found':found,'all_source_conditions_found':all(found.values()),'cpu_rate_probe':{'d0':3,'alpha':1,'epsilons':[.25,.125],'block_proxies':[coarse,fine],'ratio':fine/coarse,'expected_ratio':8.0},'scope':'direct deterministic CPU audit of the stated asymptotic rate and theorem conditions; not a constructive end-to-end Transformer approximation.'}
if __name__=='__main__':
 import json; print(json.dumps(audit(),indent=2))
