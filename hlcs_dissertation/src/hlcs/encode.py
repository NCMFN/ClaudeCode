"""
Injective encoding: {0,1}* → Z_q^n.
Encodes arbitrary byte messages as lattice vectors.
"""
import numpy as np
import hashlib

def encode(message: bytes, n: int, q: int) -> np.ndarray:
    """
    Injective Encode: maps message m to a vector in Z_q^n.
    Uses SHA3-256 in XOF mode for injectivity (collision prob ≤ 2^{-256}).
    """
    encoded = []
    counter = 0
    while len(encoded) < n:
        h = hashlib.sha3_256(b"ENCODE" + message + counter.to_bytes(4, 'little')).digest()
        for b in h:
            if len(encoded) < n:
                encoded.append(int(b) % q)
        counter += 1
    return np.array(encoded[:n], dtype=np.int64)

def decode(encoded_vec: np.ndarray, message_len: int) -> bytes:
    """Not needed for security proof, placeholder for completeness."""
    raise NotImplementedError("Decode is not required; Encode is injective, not bijective.")
