import numpy as np
import scipy.stats

def generate_matrix_A(n, q, seed=None):
    """
    Generate matrix A shape (n,n) mod q.
    """
    rng = np.random.default_rng(seed)
    return rng.integers(0, q, size=(n, n), dtype=np.int64)

def sample_gaussian(n, sigma, seed=None):
    """
    Sample discrete Gaussian error vector.
    """
    rng = np.random.default_rng(seed)
    return np.round(rng.normal(0, sigma, size=n)).astype(np.int64)

def discrete_gaussian_cdf(x, sigma):
    """
    Tail probability for failure analysis.
    Returns the normal CDF evaluated at x.
    """
    return scipy.stats.norm.cdf(x, scale=sigma)

def estimate_bkz_complexity(n, q, sigma):
    """
    Estimated bit-ops for BKZ attack.
    Based on Cost ≈ 2^(0.292 * n).
    """
    # Use float for large exponents
    return float(2**(0.292 * n))
