import numpy as np

# T2 Coherence Parameters
# Trapped-ion (IonQ Aria): T2 ≈ 1.0 s
# Source: https://www.ionq.com/quantum-systems/aria
# Superconducting transmon (AQT ring chip): T2 ≈ 50 ms typical
# Source: https://aqt.lbl.gov/about-aqt/collaborate-with-us/aqt-capabilities/
T2_CONFIGS = {
    'ionq_aria': 1.0,
    'aqt_ring': 0.05
}

def calculate_fidelity(rtt: float, t2: float) -> float:
    """
    Computes fidelity decay based on transverse relaxation T2 and classical RTT.

    Formula: F(t) = 0.5 + 0.5 * exp(-t / T2)
    where t is the measured classical RTT latency in seconds.

    Args:
        rtt: Network round-trip time in seconds.
        t2: T2 coherence time in seconds.

    Returns:
        float: Fidelity of the entangled state.
    """
    return 0.5 + 0.5 * np.exp(-rtt / t2)
