import sys
import os
sys.path.append(os.path.abspath(os.path.dirname(__file__)))

import numpy as np
from model.fidelity import calculate_fidelity, T2_CONFIGS

def test_calculate_fidelity():
    assert np.isclose(calculate_fidelity(0, 1.0), 1.0)
    assert np.isclose(calculate_fidelity(float('inf'), 1.0), 0.5)
    assert np.isclose(calculate_fidelity(1.0, 1.0), 0.5 + 0.5 * np.exp(-1))

def test_t2_configs():
    assert 'ionq_aria' in T2_CONFIGS
    assert 'aqt_ring' in T2_CONFIGS
    assert T2_CONFIGS['ionq_aria'] == 1.0
    assert T2_CONFIGS['aqt_ring'] == 0.05
