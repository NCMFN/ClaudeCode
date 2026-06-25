import hashlib
import os
import time

def setup():
    """Setup pp dict."""
    return {}

def commit(pp, message_bytes):
    """
    Commit using SHA3-256. C1 = H(r || m).
    Returns (C, opening_hint), where opening_hint is (r, m).
    Also returns wall-clock time in ns.
    """
    t0 = time.perf_counter_ns()
    r = os.urandom(32)
    h = hashlib.sha3_256()
    h.update(r)
    h.update(message_bytes)
    C = h.digest()
    t1 = time.perf_counter_ns()
    return (C, (r, message_bytes)), t1 - t0

def verify(pp, C, opening_hint):
    """
    Verify hash commitment.
    Returns bool and wall-clock time in ns.
    """
    r, m = opening_hint
    t0 = time.perf_counter_ns()
    h = hashlib.sha3_256()
    h.update(r)
    h.update(m)
    C_prime = h.digest()
    t1 = time.perf_counter_ns()
    return (C == C_prime), t1 - t0
