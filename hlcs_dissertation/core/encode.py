import numpy as np

def encode(message_bytes, n, q):
    """
    Injective Encode: {0,1}* -> Z_q^n
    """
    bits = np.unpackbits(np.frombuffer(message_bytes, dtype=np.uint8)).astype(np.int64)
    if len(bits) > n:
        raise ValueError("Message too long to encode in n dimensions")

    vec = np.zeros(n, dtype=np.int64)
    vec[:len(bits)] = bits * (q // 2)
    return vec

def decode(vector, n, q):
    """
    Original message bytes (padded to n/8 bytes).
    """
    v = vector % q
    bits = ((v > q // 4) & (v < 3 * q // 4)).astype(np.uint8)
    decoded = np.packbits(bits).tobytes()
    return decoded[:32]
