import numpy as np
from src.claim1_constructive_transformer_toy import encode_attention, run, target

def test_attention_encoder_is_finite_and_shape_preserving_readout():
    z=encode_attention(np.array([[.1,.2,.3],[.4,.5,.6]]))
    assert z.shape == (2,6)
    assert np.isfinite(z).all()

def test_constructive_fit_beats_permuted_label_control():
    rows=run(seed=17,ntrain=600,ntest=800,widths=[16,64])
    assert all(r['control_degrades'] for r in rows)
    assert rows[-1]['l2_test_error'] < .5

def test_bounded_target():
    y=target(np.array([[0.,0.,0.],[.25,.5,.75]]))
    assert np.max(np.abs(y)) <= 1.0
