"""
Zero-Knowledge Sigma Protocol + Non-Interactive Fiat-Shamir Transform.
Implements Algorithm 3 from the paper (Section VI).

Reference for Fiat-Shamir: https://eprint.iacr.org/2020/1012.pdf
"""
import numpy as np
import hashlib
from .lwe import sample_secret, sample_discrete_gaussian
from .encode import encode
from .hash_layer import hash_to_Zq, r_to_bytes

def fiat_shamir_challenge(pp, C, C_bar) -> int:
    """Non-interactive challenge c = H(C, C_bar) via Fiat-Shamir."""
    C1_bytes = C[0].tobytes()
    C2_bytes = C[1].tobytes()
    Cbar_bytes = C_bar.tobytes()
    h = hashlib.sha3_256(C1_bytes + C2_bytes + Cbar_bytes).digest()
    return int.from_bytes(h[:4], 'little') % pp.q

def prove(pp, C, r, e, m: bytes):
    """
    Non-interactive ZK proof π = (C_bar, z, f).
    Prover demonstrates knowledge of (r, e, m) s.t. C2 = Ar + Encode(m) + e.
    """
    r_bar = sample_secret(pp.n, pp.q)
    e_bar = sample_discrete_gaussian(pp.n, pp.sigma, pp.q)
    C_bar = (pp.A @ r_bar + e_bar) % pp.q

    c = fiat_shamir_challenge(pp, C, C_bar)

    z = (r_bar + c * r) % pp.q
    f = (e_bar + c * e) % pp.q

    return {"C_bar": C_bar, "z": z, "f": f, "c": c}

def verify_proof(pp, C, m: bytes, proof: dict) -> bool:
    """
    Verify ZK proof: Az + f ≡ C_bar + c*C2 - c*Encode(m) (mod q).
    """
    C_bar = proof["C_bar"]
    z = proof["z"]
    f = proof["f"]
    c = proof["c"]
    C2 = C[1]
    enc_m = encode(m, pp.n, pp.q)

    lhs = (pp.A @ z + f) % pp.q
    rhs = (C_bar + c * C2 - c * enc_m) % pp.q
    return np.array_equal(lhs, rhs)
