from typing import Dict, List

def calculate_obfuscation_budget(
    calibration_data: Dict[int, Dict[str, float]],
    active_qubits: List[int],
    eta: float = 0.1
) -> float:
    """
    Calculates the maximum allowed obfuscation latency (in ns).

    Budget = eta * min(T1 for active qubits)

    Args:
        calibration_data: dict of qubit index to calibration metrics
        active_qubits: list of active qubit indices
        eta: safety margin coefficient

    Returns:
        Max allowed latency in nanoseconds (ns).
    """
    if not active_qubits:
        return 0.0

    if eta < 0:
        return 0.0

    min_t1_us = float('inf')

    for q in active_qubits:
        if q in calibration_data:
            t1_us = calibration_data[q].get("t1_us", 0.0)
            if t1_us < min_t1_us:
                min_t1_us = t1_us

    if min_t1_us == float('inf'):
        return 0.0

    # convert us to ns (1 us = 1000 ns)
    min_t1_ns = min_t1_us * 1000.0

    budget_ns = eta * min_t1_ns
    return max(0.0, budget_ns)
