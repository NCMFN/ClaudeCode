from src.model.fidelity import compute_fidelity

class AdaptiveTTLPolicy:
    def __init__(self, threshold: float = 0.85):
        self.threshold = threshold

    def evaluate(self, rtt_seconds: float, t2: float) -> str:
        """
        Evaluate whether to HOLD or FLUSH the key based on adaptive fidelity decay.

        Args:
            rtt_seconds (float): Measured RTT in seconds.
            t2 (float): T2 parameter for the specific regime.

        Returns:
            str: 'HOLD' if F(t) >= threshold, else 'FLUSH'
        """
        fidelity = compute_fidelity(rtt_seconds, t2)
        if fidelity < self.threshold:
            return 'FLUSH'
        return 'HOLD'
