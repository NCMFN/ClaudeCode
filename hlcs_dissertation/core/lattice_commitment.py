import time
import numpy as np
from .lwe_utils import generate_matrix_A, sample_gaussian
from .encode import encode

def setup(n, q, sigma, seed=None):
    """Setup pp with matrix A."""
    A = generate_matrix_A(n, q, seed)
    return {'n': n, 'q': q, 'sigma': sigma, 'A': A}

def commit(pp, message_bytes):
    """
    C2 = A*r + Encode(m) + e mod q
    Returns (C2, opening_hint=(r, e, m)) and timing in ns.
    """
    t0 = time.perf_counter_ns()
    n = pp['n']
    q = pp['q']
    sigma = pp['sigma']
    A = pp['A']

    # r sampled from {0, 1}^n or small Gaussian? For LWE commitment, r is typically small or ternary.
    # In Regev/Kyber, r is typically from a small binomial or Gaussian.
    # Let's use Gaussian for r as well.
    r = sample_gaussian(n, sigma)
    e = sample_gaussian(n, sigma)
    m_enc = encode(message_bytes, n, q)

    C2 = (np.dot(A, r) + m_enc + e) % q
    t1 = time.perf_counter_ns()

    return (C2, (r, e, message_bytes)), t1 - t0

def verify(pp, C2, opening_hint):
    """
    Verify lattice commitment.
    Check if A*r + Encode(m) + e mod q == C2, and if e is small.
    Returns bool and timing in ns.
    """
    r, e, m = opening_hint
    t0 = time.perf_counter_ns()
    n = pp['n']
    q = pp['q']
    sigma = pp['sigma']
    A = pp['A']

    m_enc = encode(m, n, q)
    C2_prime = (np.dot(A, r) + m_enc + e) % q

    # Norm checks on r and e (heuristic bound: say 10*sigma)
    is_valid = np.array_equal(C2, C2_prime)
    bound = 10 * sigma
    is_valid = is_valid and (np.max(np.abs(e)) < bound) and (np.max(np.abs(r)) < bound)
    t1 = time.perf_counter_ns()

    return is_valid, t1 - t0
