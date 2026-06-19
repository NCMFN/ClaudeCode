"""
Hash-based commitment layer using SHA3-256.
Quantum security: 128-bit under Grover's bound (2^{n/2} = 2^{128}).
Reference: https://arxiv.org/abs/quant-ph/9605043 (Grover 1996)
"""
import hashlib
import numpy as np

def hash_to_Zq(r_bytes: bytes, n: int, q: int) -> np.ndarray:
    """
    H: {0,1}* → Z_q^n modelled as a random oracle.
    Uses SHA3-256 in counter mode to expand to n elements in Z_q.
    """
    output = []
    counter = 0
    while len(output) < n:
        h = hashlib.sha3_256(r_bytes + counter.to_bytes(4, 'little')).digest()
        for byte in h:
            if len(output) < n:
                output.append(byte % q)
        counter += 1
    return np.array(output[:n], dtype=np.int64)

def hash_bytes(data: bytes) -> bytes:
    """Raw SHA3-256 hash."""
    return hashlib.sha3_256(data).digest()

def r_to_bytes(r: np.ndarray) -> bytes:
    """Convert integer vector r to canonical byte representation."""
    return r.astype(np.int64).tobytes()
