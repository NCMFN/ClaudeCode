import pytest
import numpy as np
from src.key_rate import compute_secure_key_rate, H2

def test_secure_key_rate_1():
    config = {
        "error_correction_efficiency_f": 1.16,
        "epsilon_security": 1e-10
    }
    N = 1000000
    qber = 0.02

    # Hand-computed reference
    q = 0.5
    f_E = 1.16
    epsilon = 1e-10

    h2_E = -qber * np.log2(qber) - (1 - qber) * np.log2(1 - qber)
    delta = 7 * np.sqrt(np.log2(2 / epsilon) / N)

    expected_rate = 0.5 * (q - f_E * h2_E - f_E * h2_E - delta)
    expected_rate = max(0.0, float(expected_rate))

    computed_rate = compute_secure_key_rate(N, qber, config)
    assert np.isclose(computed_rate, expected_rate, atol=1e-7)

def test_secure_key_rate_2():
    config = {
        "error_correction_efficiency_f": 1.16,
        "epsilon_security": 1e-10
    }
    N = 1024
    qber = 0.05

    # Hand-computed reference
    q = 0.5
    f_E = 1.16
    epsilon = 1e-10

    h2_E = -qber * np.log2(qber) - (1 - qber) * np.log2(1 - qber)
    delta = 7 * np.sqrt(np.log2(2 / epsilon) / N)

    expected_rate = 0.5 * (q - f_E * h2_E - f_E * h2_E - delta)
    expected_rate = max(0.0, float(expected_rate))

    computed_rate = compute_secure_key_rate(N, qber, config)
    assert np.isclose(computed_rate, expected_rate, atol=1e-7)

def test_secure_key_rate_zero_blocks():
    config = {
        "error_correction_efficiency_f": 1.16,
        "epsilon_security": 1e-10
    }
    assert compute_secure_key_rate(0, 0.02, config) == 0.0
