"""
LWE and SIS operations.
LWE Reference: https://eprint.iacr.org/2015/939.pdf (Peikert 2016 survey)
"""
import numpy as np
from .params import DEFAULT_PARAMS

def sample_matrix_A(n, q, seed=None):
    """Sample uniform random matrix A ∈ Z_q^{n×n}."""
    rng = np.random.default_rng(seed)
    return rng.integers(0, q, size=(n, n))

def sample_discrete_gaussian(n, sigma, q, seed=None):
    """Sample error vector e ← χ^n (discrete Gaussian with std σ)."""
    rng = np.random.default_rng(seed)
    e = np.round(rng.normal(0, sigma, n)).astype(int) % q
    return e

def sample_secret(n, q, seed=None):
    """Sample secret/randomness r ← Z_q^n (uniform)."""
    rng = np.random.default_rng(seed)
    return rng.integers(0, q, size=n)

def lwe_instance(A, s, e, q):
    """Compute LWE sample b = As + e (mod q)."""
    return (A @ s + e) % q

def verify_lwe(A, r, encode_m, e, C2, q):
    """Verify C2 = Ar + Encode(m) + e (mod q)."""
    expected = (A @ r + encode_m + e) % q
    return np.array_equal(expected, C2)

def sis_norm_check(z, beta):
    """Check if z is short enough for SIS: ||z|| ≤ β."""
    return np.linalg.norm(z) <= beta
