import numpy as np

# T2 Decoherence regimes (in seconds)
# IonQ Aria: T2 ≈ 1.0 s (source: https://www.ionq.com/quantum-systems/aria)
# AQT ring chip: T2 ≈ 50 ms typical (source: https://aqt.lbl.gov/about-aqt/collaborate-with-us/aqt-capabilities/)
T2_REGIMES = {
    'IonQ_Aria': 1.0,
    'AQT': 0.05
}

def compute_fidelity(t: float, t2: float) -> float:
    """
    Computes fidelity F(t) given elapsed time t (latency) and coherence time T2.
    Formula: F(t) = 0.5 + 0.5 * exp(-t / T2)

    Args:
        t (float): Elapsed time (RTT latency) in seconds.
        t2 (float): Transverse relaxation time (T2) in seconds.

    Returns:
        float: Fidelity value bounded [0.5, 1.0]
    """
    if t < 0:
        raise ValueError("Time t cannot be negative")
    if t2 <= 0:
        raise ValueError("T2 must be positive")

    return 0.5 + 0.5 * np.exp(-t / t2)
