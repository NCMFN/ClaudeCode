import pytest
import numpy as np

from src.model.fidelity import compute_fidelity
from src.policy.adaptive_ttl import AdaptiveTTLPolicy
from src.policy.static_ttl import StaticTTLPolicy

def test_compute_fidelity():
    assert compute_fidelity(0, 1.0) == 1.0
    assert np.isclose(compute_fidelity(1.0, 1.0), 0.5 + 0.5 * np.exp(-1))

    with pytest.raises(ValueError):
        compute_fidelity(-1.0, 1.0)
    with pytest.raises(ValueError):
        compute_fidelity(1.0, 0.0)

def test_adaptive_ttl_policy():
    policy = AdaptiveTTLPolicy(threshold=0.85)

    # 0.85 corresponds to t such that 0.5 + 0.5 * exp(-t/T2) = 0.85
    # 0.5 * exp(-t/T2) = 0.35 => exp(-t/T2) = 0.7 => -t/T2 = ln(0.7) => t = -T2 * ln(0.7)
    # For T2=1.0, threshold_t is ~0.35667
    t2 = 1.0

    assert policy.evaluate(0.1, t2) == 'HOLD'
    assert policy.evaluate(0.5, t2) == 'FLUSH'

def test_static_ttl_policy():
    policy = StaticTTLPolicy(timeout_seconds=0.35)

    assert policy.evaluate(0.1) == 'HOLD'
    assert policy.evaluate(0.5) == 'FLUSH'
