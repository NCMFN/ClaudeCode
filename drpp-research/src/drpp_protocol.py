import secrets
from typing import Dict, Any
from .prf_simulator import f

class DRPPProtocol:
    """
    Deception-Resistant Presence Proof (DRPP) Protocol Implementation.
    Implements Algorithm 3 from the paper.
    """
    def __init__(self, k: int, secret_s: bytes):
        self.k = k
        self.secret_s = secret_s
        self.history = []

    def generate_challenge(self) -> bytes:
        num_bytes = (self.k + 7) // 8
        c_bytes = bytearray(secrets.token_bytes(num_bytes))
        if self.k % 8 != 0:
            mask = (1 << (self.k % 8)) - 1
            c_bytes[0] &= mask
        return bytes(c_bytes)

    def compute_response(self, c: bytes) -> bytes:
        # Full HMAC response
        full_r = f(c, self.secret_s)
        # Truncate response to exactly k bits so that the guessing probability is 2^-k
        num_bytes = (self.k + 7) // 8
        trunc_r = bytearray(full_r[:num_bytes])
        if self.k % 8 != 0:
            mask = (1 << (self.k % 8)) - 1
            trunc_r[0] &= mask
        return bytes(trunc_r)

    def verify(self, c: bytes, r: bytes) -> bool:
        expected_r = self.compute_response(c)
        # Verify the truncated response
        num_bytes = (self.k + 7) // 8
        trunc_r = bytearray(r[:num_bytes])
        if self.k % 8 != 0:
            mask = (1 << (self.k % 8)) - 1
            trunc_r[0] &= mask
        return secrets.compare_digest(bytes(trunc_r), expected_r)

    def run_protocol(self, prover_present: bool) -> Dict[str, Any]:
        c = self.generate_challenge()
        num_bytes = (self.k + 7) // 8

        if prover_present:
            r = self.compute_response(c)
        else:
            # Adversary guesses blindly with a sequence of bytes matching the challenge size
            r = secrets.token_bytes(num_bytes)

        is_valid = self.verify(c, r)

        run_data = {
            "challenge": c,
            "response": r,
            "outcome": is_valid,
            "presence_status": prover_present
        }
        self.history.append(run_data)

        return run_data
