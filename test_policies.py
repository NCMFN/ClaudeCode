import sys
import os
sys.path.append(os.path.abspath(os.path.dirname(__file__)))

from policy.adaptive_ttl import adaptive_ttl_policy
from policy.static_ttl import static_ttl_policy
import numpy as np

def test_adaptive_ttl_policy():
    assert adaptive_ttl_policy(0, 1.0) == "HOLD"
    assert adaptive_ttl_policy(0.3, 1.0) == "HOLD"
    assert adaptive_ttl_policy(0.4, 1.0) == "FLUSH"

def test_static_ttl_policy():
    assert static_ttl_policy(0.1, timeout=0.2) == "HOLD"
    assert static_ttl_policy(0.3, timeout=0.2) == "FLUSH"
    assert static_ttl_policy(0.2, timeout=0.2) == "HOLD"
