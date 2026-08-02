class StaticTTLPolicy:
    def __init__(self, timeout_seconds: float):
        """
        Args:
            timeout_seconds (float): Fixed timeout in seconds.
        """
        self.timeout_seconds = timeout_seconds

    def evaluate(self, rtt_seconds: float, t2: float = None) -> str:
        """
        Evaluate whether to HOLD or FLUSH based on a fixed static timeout.

        Args:
            rtt_seconds (float): Measured RTT in seconds.
            t2 (float, optional): Ignored. Included for signature compatibility.

        Returns:
            str: 'HOLD' if rtt_seconds <= timeout, else 'FLUSH'
        """
        if rtt_seconds > self.timeout_seconds:
            return 'FLUSH'
        return 'HOLD'
