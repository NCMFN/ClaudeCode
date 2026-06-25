import hashlib
import time
import numpy as np
from .lwe_utils import generate_matrix_A, sample_gaussian
from .encode import encode
from .hybrid_commitment import commit as hybrid_commit, setup as hybrid_setup

def prove(pp, commitment_tuple, witness):
    n = pp['n']
    q = pp['q']
    sigma = pp['sigma']
    A = pp['A']
    C1, C2 = commitment_tuple
    r, e, m = witness

    y_r = sample_gaussian(n, sigma * 10)
    y_e = sample_gaussian(n, sigma * 10)
    C_bar = (np.dot(A, y_r) + y_e) % q

    h = hashlib.sha3_256()
    h.update(C1)
    h.update(C2.tobytes())
    h.update(C_bar.tobytes())
    c = int.from_bytes(h.digest()[:1], 'big') % 2

    z_r = y_r + c * r
    z_e = y_e + c * e

    return (C_bar, z_r, z_e, c)

def verify_proof(pp, commitment_tuple, m, proof):
    n = pp['n']
    q = pp['q']
    A = pp['A']
    C1, C2 = commitment_tuple
    C_bar, z_r, z_e, c = proof

    h = hashlib.sha3_256()
    h.update(C1)
    h.update(C2.tobytes())
    h.update(C_bar.tobytes())
    c_prime = int.from_bytes(h.digest()[:1], 'big') % 2
    if c != c_prime:
        return False

    m_enc = encode(m, n, q)

    lhs = (np.dot(A, z_r) + z_e) % q
    rhs = (C_bar + c * (C2 - m_enc)) % q

    return np.array_equal(lhs, rhs)

def benchmark_prove_verify(pp, n_trials=1000, m_bytes=b'0'*32):
    prove_times = []
    verify_times = []
    proof_sizes = []

    # Correct unpack: C_tuple, hint, timings = hybrid_commit(pp, m_bytes)
    C_tuple, hint, timings = hybrid_commit(pp, m_bytes)

    for _ in range(n_trials):
        t0 = time.perf_counter_ns()
        proof = prove(pp, C_tuple, hint)
        t1 = time.perf_counter_ns()

        t2 = time.perf_counter_ns()
        valid = verify_proof(pp, C_tuple, m_bytes, proof)
        t3 = time.perf_counter_ns()

        prove_times.append((t1 - t0) / 1e6)
        verify_times.append((t3 - t2) / 1e6)

        C_bar_bytes = proof[0].nbytes
        z_r_bytes = proof[1].nbytes
        z_e_bytes = proof[2].nbytes
        c_bytes = 1
        total_size = C_bar_bytes + z_r_bytes + z_e_bytes + c_bytes
        proof_sizes.append((C_bar_bytes, z_r_bytes, z_e_bytes, total_size))

    return {
        'prove_mean': np.mean(prove_times),
        'prove_std': np.std(prove_times),
        'prove_p95': np.percentile(prove_times, 95),
        'verify_mean': np.mean(verify_times),
        'verify_std': np.std(verify_times),
        'verify_p95': np.percentile(verify_times, 95),
        'sizes': proof_sizes[0]
    }
