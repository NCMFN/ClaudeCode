import pytest
import numpy as np
from src.drpp_core import DRPPVerifier, PRF, HonestProver, SingleGuessAdversary, CollusionAdversary
from src.modalities import generate_synthetic_data, train_and_evaluate_classifiers

def test_prf_deterministic():
    secret = b"test_secret_123"
    challenge = b"test_challenge_123"
    k = 16
    out1 = PRF(challenge, secret, k)
    out2 = PRF(challenge, secret, k)
    assert out1 == out2
    assert len(out1) == 2 # 16 bits = 2 bytes

def test_prf_truncation():
    secret = b"test_secret"
    challenge = b"test_challenge"

    # Test 12 bits
    k = 12
    out = PRF(challenge, secret, k)
    assert len(out) == 2
    # The top 4 bits should be 0
    assert out[0] & 0xF0 == 0

def test_honest_prover():
    k = 16
    secret = b"my_secret"
    verifier = DRPPVerifier(k)
    prover = HonestProver(secret, k)

    challenge = verifier.generate_challenge()
    response = prover.compute_response(challenge)

    assert verifier.verify_response(challenge, response, secret)

def test_single_guess_adversary():
    k = 8
    adv = SingleGuessAdversary(k)
    challenge = b"challenge"
    guess = adv.guess_response(challenge)
    assert len(guess) == 1

def test_collusion_adversary():
    k = 8
    n = 3
    adv = CollusionAdversary(k, n)
    challenge = b"challenge"
    guesses = adv.guess_responses(challenge)
    assert len(guesses) == n
    for g in guesses:
        assert len(g) == 1

def test_modalities_generation():
    X, y = generate_synthetic_data("knock", 100, 0.1)
    assert X.shape == (100, 3)
    assert len(y) == 100
    assert sum(y) == 50

def test_classifiers():
    X, y = generate_synthetic_data("touch", 200, 0.05)
    metrics = train_and_evaluate_classifiers(X, y)
    assert "LR" in metrics
    assert "RF" in metrics
    assert metrics["LR"]["accuracy"] >= 0.5
    assert metrics["RF"]["accuracy"] >= 0.5
