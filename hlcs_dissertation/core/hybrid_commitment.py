import hashlib
import time
import os
import numpy as np
from .lwe_utils import generate_matrix_A, sample_gaussian
from .encode import encode

def setup(n, q, sigma, seed=None):
    A = generate_matrix_A(n, q, seed)
    return {'n': n, 'q': q, 'sigma': sigma, 'A': A}

def commit(pp, message_bytes):
    """
    HLCS:
    Returns (C_tuple, st, timings)
    C_tuple = (C1, C2)
    st = (r, e, message_bytes)
    timings = (t_total, t_c1, t_c2)
    """
    t0 = time.perf_counter_ns()
    n = pp['n']
    q = pp['q']
    sigma = pp['sigma']
    A = pp['A']

    t_c2_start = time.perf_counter_ns()
    r = sample_gaussian(n, sigma)
    e = sample_gaussian(n, sigma)
    m_enc = encode(message_bytes, n, q)
    C2 = (np.dot(A, r) + m_enc + e) % q
    t_c2_end = time.perf_counter_ns()

    t_c1_start = time.perf_counter_ns()
    h = hashlib.sha3_256()
    h.update(r.tobytes())
    h.update(message_bytes)
    C1 = h.digest()
    t_c1_end = time.perf_counter_ns()

    t1 = time.perf_counter_ns()

    return ((C1, C2), (r, e, message_bytes), (t1 - t0, t_c1_end - t_c1_start, t_c2_end - t_c2_start))

def verify(pp, C_tuple, opening_hint):
    C1, C2 = C_tuple
    r, e, m = opening_hint
    v1 = fast_verify_C1(pp, C1, r, m)
    v2 = full_verify_C2(pp, C2, r, e, m)
    return v1 and v2

def fast_verify_C1(pp, C1, r, m):
    h = hashlib.sha3_256()
    h.update(r.tobytes())
    h.update(m)
    return h.digest() == C1

def full_verify_C2(pp, C2, r, e, m):
    n = pp['n']
    q = pp['q']
    sigma = pp['sigma']
    A = pp['A']
    m_enc = encode(m, n, q)
    C2_prime = (np.dot(A, r) + m_enc + e) % q
    bound = 10 * sigma
    return np.array_equal(C2, C2_prime) and (np.max(np.abs(e)) < bound) and (np.max(np.abs(r)) < bound)
