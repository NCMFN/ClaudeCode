import numpy as np

def h2(x):
    if x == 0 or x == 1:
        return 0.0
    if x < 0 or x > 1:
        return float('nan')
    return -x * np.log2(x) - (1 - x) * np.log2(1 - x)

def compute_skr_per_block(N, E, config):
    q = 0.5
    n = N * q
    f_E = config["error_correction_efficiency_f"]
    H_E = h2(E)

    leak_EC = n * H_E * f_E

    eps = config["epsilon_security"]
    delta = 7 * np.sqrt( np.log2(2 / eps) / N )

    term = q - f_E * H_E - (leak_EC / n) - delta
    R_N = (n / N) * term

    if R_N < 0:
        return 0.0
    return R_N

def test_key_rate():
    test_config = {
        "error_correction_efficiency_f": 1.16,
        "epsilon_security": 1e-10,
    }
    N1, E1 = 100000, 0.02
    q = 0.5
    n1 = N1 * q
    H1 = h2(E1)
    f_E = 1.16
    leak_EC1 = n1 * H1 * f_E
    delta1 = 7 * np.sqrt( np.log2(2 / 1e-10) / N1 )
    term1 = q - f_E * H1 - (leak_EC1 / n1) - delta1
    R_N1 = max(0.0, (n1 / N1) * term1)

    assert np.isclose(compute_skr_per_block(N1, E1, test_config), R_N1)

if __name__ == "__main__":
    test_key_rate()
