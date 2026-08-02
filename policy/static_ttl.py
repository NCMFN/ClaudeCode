def static_ttl_policy(rtt: float, timeout: float) -> str:
    """
    Static TTL baseline policy (fixed timeout, no telemetry awareness).
    If the latency (time in buffer before confirmation arrives) exceeds
    the fixed timeout, it assumes the key is stale and flushes it.

    Args:
        rtt: Network round-trip time in seconds (acting as the key age).
        timeout: Fixed timeout threshold in seconds.

    Returns:
        str: 'FLUSH' if rtt > timeout, else 'HOLD'.
    """
    if rtt > timeout:
        return "FLUSH"
    return "HOLD"
