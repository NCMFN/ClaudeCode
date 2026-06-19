"""
Hybrid Hash-Lattice Commitment Scheme (HLCS).
Implements Algorithm 1 (HybridCommit) and Algorithm 2 (Verify) from the paper.

Paper: "Hybrid Post-Quantum Commitment Schemes for Latency-Constrained Financial Systems"
"""
import time
import numpy as np
from .lwe import sample_matrix_A, sample_discrete_gaussian, sample_secret
from .hash_layer import hash_to_Zq, r_to_bytes
from .encode import encode
from .params import DEFAULT_PARAMS

class HLCSSetup:
    """Public parameters pp = (A, q, H)."""
    def __init__(self, params=None):
        p = params or DEFAULT_PARAMS
        self.n = p["n"]
        self.q = p["q"]
        self.sigma = p["sigma"]
        self.B = p["B"]
        self.A = sample_matrix_A(self.n, self.q)  # A ∈ Z_q^{n×n}

class HLCSCommitment:
    """
    Algorithm 1: HybridCommit(pp, m)
    Returns commitment C = (C1, C2) and opening hint st = (r, e, m).

    C1 = H(r)                         ← fast path (hash)
    C2 = Ar + Encode(m) + e (mod q)   ← quantum-safe path (LWE)
    """
    def __init__(self, pp: HLCSSetup, message: bytes):
        self.pp = pp
        self.message = message
        self._commit()

    def _commit(self):
        t0 = time.perf_counter()
        # Sample randomness and error
        self.r = sample_secret(self.pp.n, self.pp.q)
        self.e = sample_discrete_gaussian(self.pp.n, self.pp.sigma, self.pp.q)
        r_bytes = r_to_bytes(self.r)
        # C1: hash of r (fast path)
        self.C1 = hash_to_Zq(r_bytes, self.pp.n, self.pp.q)
        # C2: LWE commitment to Encode(m) (quantum-safe path)
        enc_m = encode(self.message, self.pp.n, self.pp.q)
        self.C2 = (self.pp.A @ self.r + enc_m + self.e) % self.pp.q
        self.latency_ms = (time.perf_counter() - t0) * 1000

    @property
    def commitment(self):
        return (self.C1, self.C2)

    @property
    def opening_hint(self):
        return (self.r, self.e, self.message)


def verify(pp: HLCSSetup, C1, C2, r, e, message: bytes) -> bool:
    """
    Algorithm 2: Verify(pp, C, m, r, e)
    Returns True iff both C1 = H(r) and C2 = Ar + Encode(m) + e (mod q).
    """
    # Check C1 (hash fast path)
    r_bytes = r_to_bytes(r)
    expected_C1 = hash_to_Zq(r_bytes, pp.n, pp.q)
    if not np.array_equal(C1, expected_C1):
        return False
    # Check C2 (LWE quantum-safe path)
    enc_m = encode(message, pp.n, pp.q)
    expected_C2 = (pp.A @ r + enc_m + e) % pp.q
    return np.array_equal(C2, expected_C2)
