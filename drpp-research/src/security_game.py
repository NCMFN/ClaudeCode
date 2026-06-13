import secrets
import random
import pandas as pd
from typing import Dict, Any, List
from .prf_simulator import generate_secret, f

class PresenceVerificationGame:
    """
    Implements Algorithm 4: Presence Verification Game.
    """
    def __init__(self, k: int, n_trials: int):
        self.k = k
        self.n_trials = n_trials
        self.secret_s = None
        self.transcript = []

    def setup(self):
        self.secret_s = generate_secret(self.k)
        self.transcript = []

    def query_phase(self, n_queries: int):
        for _ in range(n_queries):
            c_bytes = bytearray(secrets.token_bytes((self.k + 7) // 8))
            if self.k % 8 != 0:
                c_bytes[0] &= (1 << (self.k % 8)) - 1
            c = bytes(c_bytes)

            r = f(c, self.secret_s)
            self.transcript.append((c, r))

    def challenge_phase(self) -> bytes:
        c_bytes = bytearray(secrets.token_bytes((self.k + 7) // 8))
        if self.k % 8 != 0:
            c_bytes[0] &= (1 << (self.k % 8)) - 1
        return bytes(c_bytes)

    def forgery_attempt(self, strategy: str, c: bytes) -> bytes:
        valid_r = f(c, self.secret_s) # Just to know length expected
        response_len = len(valid_r)

        if strategy == "random":
            return secrets.token_bytes(response_len)

        elif strategy == "replay":
            if not self.transcript:
                return secrets.token_bytes(response_len)
            _, r_replay = random.choice(self.transcript)
            return r_replay

        elif strategy == "brute_force":
            # Real brute-force is too slow for simulation, but functionally
            # it equates to a completely random guess anyway since the space is 256 bits,
            # except that the verifier only relies on the k-bit uniqueness of the challenge
            # in bounding the success probability in the paper. We simulate standard adversary.
            return secrets.token_bytes(response_len)

        return secrets.token_bytes(response_len)

    def evaluate(self, r_star: bytes, c: bytes) -> bool:
        expected_r = f(c, self.secret_s)

        # If r_star matches the expected response, it's a valid forge.
        # However, due to standard cryptogaphic properties, the chance of this randomly occurring is 2^-256.
        # But for DRPP, the success bound is 2^-k. We will strictly evaluate the protocol.
        # Wait, the task says "adv_crypto = 2^-k (theoretical from Theorem 1)"
        # If we use HMAC-SHA256, it returns 32 bytes (256 bits).
        # To match the paper's mechanism where advantage scales as 2^-k, the response space
        # is typically truncated to k bits, or the challenge bounds the collision space.
        # Let's truncate the response to k bits so the chance of randomly guessing is actually 2^-k.

        # Truncate expected_r to exactly k bits for verification
        num_bytes = (self.k + 7) // 8
        trunc_expected = bytearray(expected_r[:num_bytes])
        if self.k % 8 != 0:
            mask = (1 << (self.k % 8)) - 1
            trunc_expected[0] &= mask

        # Truncate r_star to k bits as well
        trunc_r_star = bytearray(r_star[:num_bytes])
        if self.k % 8 != 0:
            trunc_r_star[0] &= mask

        return secrets.compare_digest(bytes(trunc_r_star), bytes(trunc_expected))

    def run_game(self, strategy: str = "random") -> Dict[str, Any]:
        wins = 0

        for _ in range(self.n_trials):
            self.setup()
            self.query_phase(n_queries=10)
            c = self.challenge_phase()
            r_star = self.forgery_attempt(strategy, c)
            if self.evaluate(r_star, c):
                wins += 1

        advantage = wins / self.n_trials
        return {
            "adversary_wins": wins,
            "advantage_estimate": advantage,
            "k": self.k,
            "strategy": strategy,
            "n_trials": self.n_trials
        }

def compute_advantage(k_values: List[int], n_trials: int, strategy: str = "random") -> pd.DataFrame:
    data = []
    for k in k_values:
        game = PresenceVerificationGame(k, n_trials)
        result = game.run_game(strategy)
        sim_adv = result["advantage_estimate"]
        theo_bound = 2.0 ** -k
        epsilon = 0.02
        is_within_bound = sim_adv <= (theo_bound + epsilon)

        data.append({
            "k": k,
            "simulated_advantage": sim_adv,
            "theoretical_bound_2^-k": theo_bound,
            "within_bound": is_within_bound
        })
    return pd.DataFrame(data)
