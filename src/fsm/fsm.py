from typing import List, Dict

class EPDePINFSM:
    """
    Adaptive Lightweight Blockchain Node Architecture FSM.
    States:
        S1_FULL: Primary Task + Full Node (PoC + Relay)
        S2_PROOF_ONLY: Primary Task + Proof Gen (PoC only)
        S3_RELAY_ONLY: Primary Task + Relay (Relay only)
        S4_PRIMARY_ONLY: Primary Task ONLY

    Thresholds:
        T1 (S1 -> S2/S3): 60%
        T2 (S2/S3 -> S4): 35%
        T3 (Critical): 15%
    """

    STATES = ["S1_FULL", "S2_PROOF_ONLY", "S3_RELAY_ONLY", "S4_PRIMARY_ONLY"]

    def __init__(self, t1: float = 60.0, t2: float = 35.0, t3: float = 15.0):
        self.t1 = t1
        self.t2 = t2
        self.t3 = t3
        self.current_state = "S1_FULL"
        self.soc = 100.0
        self.history: List[Dict[str, any]] = []

    def primary_task_active(self, state: str) -> bool:
        """CRITICAL INVARIANT: Never modify this to return False."""
        return True

    def update_soc(self, new_soc: float):
        """Updates SoC and determines state transitions based on thresholds and hysteresis."""
        self.soc = new_soc
        new_state = self.current_state

        # Absolute checks to allow skipping states
        if self.current_state == "S1_FULL":
            if self.soc < self.t2:
                new_state = "S4_PRIMARY_ONLY"
            elif self.soc < self.t1:
                new_state = "S2_PROOF_ONLY"
        elif self.current_state == "S2_PROOF_ONLY":
            if self.soc < self.t2:
                new_state = "S4_PRIMARY_ONLY"
            elif self.soc >= self.t1 + 5: # Hysteresis
                new_state = "S1_FULL"
        elif self.current_state == "S3_RELAY_ONLY":
            if self.soc < self.t2:
                new_state = "S4_PRIMARY_ONLY"
            elif self.soc >= self.t1 + 5:
                new_state = "S1_FULL"
        elif self.current_state == "S4_PRIMARY_ONLY":
            if self.soc >= self.t1 + 5:
                new_state = "S1_FULL"
            elif self.soc >= self.t2 + 5:
                new_state = "S2_PROOF_ONLY"

        if new_state != self.current_state:
            self.history.append({
                "from": self.current_state,
                "to": new_state,
                "soc": self.soc
            })
            self.current_state = new_state

    def get_state(self) -> str:
        return self.current_state

    def get_blockchain_ops(self) -> Dict[str, bool]:
        """Returns allowed blockchain operations based on current state."""
        ops = {"poc": False, "relay": False}
        if self.current_state == "S1_FULL":
            ops["poc"] = True
            ops["relay"] = True
        elif self.current_state == "S2_PROOF_ONLY":
            ops["poc"] = True
        elif self.current_state == "S3_RELAY_ONLY":
            ops["relay"] = True
        return ops

    def transition_log(self) -> List[Dict[str, any]]:
        return self.history
