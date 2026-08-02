def calculate_budget_ns(t1_times_us: list[float], eta: float = 0.1) -> float:
    """
    Calculates the allowed obfuscation latency (noise budget) in nanoseconds.

    Allowed obfuscation latency = eta * min(T1 over active qubits)

    Args:
        t1_times_us: A list of T1 coherence times in microseconds for all
                     qubits actively used in the circuit.
        eta: The safety coefficient (default 0.1). Must be >= 0.

    Returns:
        The allowed latency budget in nanoseconds. Returns 0.0 if eta is 0
        or if the minimum T1 is 0.

    Raises:
        ValueError: If the list of t1 times is empty, or if eta < 0, or if any T1 < 0.
    """
    if not t1_times_us:
        raise ValueError("Must provide at least one T1 time.")

    if eta < 0:
        raise ValueError("Safety coefficient eta must be non-negative.")

    if any(t < 0 for t in t1_times_us):
        raise ValueError("T1 times cannot be negative.")

    min_t1_us = min(t1_times_us)

    # Convert T1 from microseconds to nanoseconds
    min_t1_ns = min_t1_us * 1000.0

    budget_ns = eta * min_t1_ns

    return budget_ns
