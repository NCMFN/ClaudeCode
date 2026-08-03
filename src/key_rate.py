import numpy as np

def H2(x):
    """Binary Shannon entropy"""
    if x <= 0 or x >= 1:
        return 0
    return -x * np.log2(x) - (1 - x) * np.log2(1 - x)

def compute_secure_key_rate(N, qber, config):
    """
    Computes finite-size-corrected Secure Key Rate per block.

    Formula: R(N) = (n/N) * [ q - f(E) * H2(E) - leak_EC/n - Δ(N, ε) ]
    where:
    - N = raw block size (bits)
    - n = sifted key length within the block
    - q = 0.5 (BB84)
    - E = QBER per block
    - H2 = binary Shannon entropy
    - f(E) = error_correction_efficiency_f (e.g. 1.16 from standard BB84 cascade assumption)
    - leak_EC = n * H2(E) * f(E)
    - Δ(N, ε) = 7 * sqrt(log2(2/ε) / N) (simplified pedagogical approximation of Tomamichel et al. bound)
    """
    if N <= 0:
        return 0.0

    q = 0.5
    f_E = config["error_correction_efficiency_f"]
    epsilon = config["epsilon_security"]

    n = N * q
    E = qber
    h2_E = H2(E)

    leak_EC = n * h2_E * f_E
    leak_EC_per_n = leak_EC / n if n > 0 else 0

    # simplified pedagogical approximation of Tomamichel et al. bound
    delta = 7 * np.sqrt(np.log2(2 / epsilon) / N)

    rate = (n / N) * (q - f_E * h2_E - leak_EC_per_n - delta)

    return max(0.0, float(rate))
