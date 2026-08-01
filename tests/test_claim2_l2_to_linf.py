import numpy as np
from src.claim2_l2_to_linf_counterexample import tent, tent_l2_squared

def test_tent_norm_formula_matches_quadrature():
    x=np.linspace(0,1,500001)
    for width in [0.4,0.1,0.025]:
        got=np.trapezoid(tent(x,width)**2,x)
        assert abs(got-tent_l2_squared(width)) < 2e-8

def test_bounded_compact_tent_separates_l2_and_linf():
    width=0.0125
    assert tent(np.array([.5]),width)[0] == 1.0
    assert np.sqrt(tent_l2_squared(width)) < .1
