import numpy as np
import hmac
import hashlib

class DRPPVerifier:
    def __init__(self, k_bits: int):
        self.k = k_bits

    def generate_challenge(self) -> bytes:
        """Generates a random k-bit challenge."""
        num_bytes = (self.k + 7) // 8
        challenge = np.random.bytes(num_bytes)
        # Mask out extra bits if k is not a multiple of 8
        if self.k % 8 != 0:
            mask = (1 << (self.k % 8)) - 1
            challenge = bytes([challenge[0] & mask]) + challenge[1:]
        return challenge

    def verify_response(self, challenge: bytes, response: bytes, secret: bytes) -> bool:
        """Verifies if the response matches the expected PRF output."""
        expected_response = PRF(challenge, secret, self.k)
        return response == expected_response

def PRF(challenge: bytes, secret: bytes, k_bits: int) -> bytes:
    """Computes HMAC-SHA256(secret, challenge) truncated to k bits."""
    h = hmac.new(secret, challenge, hashlib.sha256).digest()
    num_bytes = (k_bits + 7) // 8
    truncated = h[:num_bytes]

    # Mask out extra bits if k is not a multiple of 8
    if k_bits % 8 != 0:
        mask = (1 << (k_bits % 8)) - 1
        truncated = bytes([truncated[0] & mask]) + truncated[1:]

    return truncated

class HonestProver:
    def __init__(self, secret: bytes, k_bits: int):
        self.secret = secret
        self.k = k_bits

    def compute_response(self, challenge: bytes) -> bytes:
        return PRF(challenge, self.secret, self.k)


class SingleGuessAdversary:
    def __init__(self, k_bits: int):
        self.k = k_bits

    def guess_response(self, challenge: bytes) -> bytes:
        """Randomly guesses a k-bit response."""
        num_bytes = (self.k + 7) // 8
        guess = np.random.bytes(num_bytes)
        if self.k % 8 != 0:
            mask = (1 << (self.k % 8)) - 1
            guess = bytes([guess[0] & mask]) + guess[1:]
        return guess

class CollusionAdversary:
    def __init__(self, k_bits: int, n_colluders: int):
        self.k = k_bits
        self.n_colluders = n_colluders

    def guess_responses(self, challenge: bytes) -> list[bytes]:
        """Returns n independent random guesses."""
        guesses = []
        for _ in range(self.n_colluders):
            num_bytes = (self.k + 7) // 8
            guess = np.random.bytes(num_bytes)
            if self.k % 8 != 0:
                mask = (1 << (self.k % 8)) - 1
                guess = bytes([guess[0] & mask]) + guess[1:]
            guesses.append(guess)
        return guesses

class TraditionalBaselineAdversary:
    def __init__(self, success_probability: float):
        self.p = success_probability

    def attempt_access(self) -> bool:
        """Simulates environmental-cue authentication attack success based on fixed probability."""
        return np.random.rand() < self.p

def run_monte_carlo_drpp(k_bits: int, trials: int, adversary_type: str, **kwargs) -> float:
    """
    Runs a Monte Carlo simulation of the DRPP security game.
    Returns the adversary's empirical advantage (success rate).
    """
    verifier = DRPPVerifier(k_bits)
    secret = np.random.bytes(32) # 256-bit secret
    successes = 0

    if adversary_type == "single":
        adv = SingleGuessAdversary(k_bits)
        for _ in range(trials):
            challenge = verifier.generate_challenge()
            response = adv.guess_response(challenge)
            if verifier.verify_response(challenge, response, secret):
                successes += 1

    elif adversary_type == "collusion":
        n = kwargs.get("n_colluders", 2)
        adv = CollusionAdversary(k_bits, n)
        for _ in range(trials):
            challenge = verifier.generate_challenge()
            responses = adv.guess_responses(challenge)
            # Adversary wins if ANY colluder guesses correctly
            for r in responses:
                if verifier.verify_response(challenge, r, secret):
                    successes += 1
                    break

    elif adversary_type == "baseline":
        p = kwargs.get("success_probability", 0.34)
        adv = TraditionalBaselineAdversary(p)
        for _ in range(trials):
            if adv.attempt_access():
                successes += 1

    else:
        raise ValueError(f"Unknown adversary type: {adversary_type}")

    return successes / trials
