import numpy as np

def calculate_latency_budget(t1_times: dict, active_qubits: list, eta: float = 0.1) -> float:
    """
    Calculate the allowed latency budget for obfuscation.

    Args:
        t1_times: Dict mapping qubit index to T1 time (in seconds, typically).
        active_qubits: List of active qubit indices.
        eta: Safety coefficient. Default is 0.1.

    Returns:
        float: allowed obfuscation latency = eta * min(T1 times of active qubits)
    """
    if not active_qubits:
        return 0.0

    # Get T1 times for active qubits, filtering out any missing ones safely or treating them as np.inf if not found
    active_t1s = [t1_times.get(q, np.inf) for q in active_qubits]

    # If a qubit has no T1 data and returns np.inf, the minimum ignores it unless all are inf
    min_t1 = min(active_t1s)

    if min_t1 == np.inf:
        return 0.0

    return eta * min_t1
