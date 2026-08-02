from model.fidelity import calculate_fidelity

def adaptive_ttl_policy(rtt: float, t2: float, threshold: float = 0.85) -> str:
    """
    Adaptive TTL policy that computes fidelity based on real-time RTT telemetry.
    If the fidelity drops below the threshold, it flushes the buffer to prevent
    'Zombie Data' exposure.

    Args:
        rtt: Network round-trip time in seconds.
        t2: T2 coherence time of the hardware in seconds.
        threshold: Fidelity threshold (default 0.85).

    Returns:
        str: 'FLUSH' if F(t) < threshold, else 'HOLD'.
    """
    fidelity = calculate_fidelity(rtt, t2)
    if fidelity < threshold:
        return "FLUSH"
    return "HOLD"
