import hmac
import hashlib
import secrets
import random

def f(challenge_c: bytes, secret_s: bytes) -> bytes:
    h = hmac.new(secret_s, challenge_c, hashlib.sha256)
    return h.digest()

def generate_secret(k: int) -> bytes:
    return secrets.token_bytes((k + 7) // 8)

def distinguish_test(k: int, q: int, n_trials: int = 1000) -> float:
    """
    Simulates the PRF distinguishing game.
    """
    wins = 0
    for _ in range(n_trials):
        secret_s = generate_secret(k)

        # Challenger flips a coin b
        b = random.choice([0, 1])

        # Define oracle O
        # If b=0: O is f(s, .)
        # If b=1: O is truly random function
        random_map = {}

        def oracle(challenge: bytes) -> bytes:
            if b == 0:
                return f(challenge, secret_s)
            else:
                if challenge not in random_map:
                    # Output size matches HMAC-SHA256 (32 bytes)
                    random_map[challenge] = secrets.token_bytes(32)
                return random_map[challenge]

        # Adversary makes q adaptive queries
        # Since the adversary has no way to break SHA256, their strategy is just to guess randomly
        # Or look for collisions, but space is too large.
        for _ in range(q):
            c = secrets.token_bytes((k + 7) // 8)
            oracle(c)

        # Adversary outputs guess b_prime
        # Without key, outputs of HMAC look random, so best guess is random coin flip
        b_prime = random.choice([0, 1])

        if b_prime == b:
            wins += 1

    # Advantage = | P(b' = b) - 1/2 | * 2
    # But usually advantage is defined as P[D(F_k) = 1] - P[D(R) = 1]
    # Let's use standard definition: | 2 * P(win) - 1 |
    prob_win = wins / n_trials
    advantage = abs(2.0 * prob_win - 1.0)

    return advantage
