class EPDePINFSM:
    STATES = ['S1_FULL', 'S2_PROOF_ONLY', 'S3_RELAY_ONLY', 'S4_PRIMARY_ONLY']
    THRESHOLDS = {'S1_to_S2': 60, 'S2_to_S3': 35, 'S3_to_S4': 15}
    HYSTERESIS = 5  # +5% buffer on upward transitions to prevent thrashing

    def __init__(self, thresholds=None):
        if thresholds:
            self.THRESHOLDS = thresholds
        self.current_state = 'S1_FULL'

    def get_state(self, soc: float) -> str:
        # Determine the target state based on SoC
        if soc <= self.THRESHOLDS['S3_to_S4']:
            target_state = 'S4_PRIMARY_ONLY'
        elif soc <= self.THRESHOLDS['S2_to_S3']:
            target_state = 'S3_RELAY_ONLY'
        elif soc <= self.THRESHOLDS['S1_to_S2']:
            target_state = 'S2_PROOF_ONLY'
        else:
            target_state = 'S1_FULL'

        # Apply hysteresis if transitioning upward
        if self.current_state == 'S4_PRIMARY_ONLY':
            if soc > self.THRESHOLDS['S3_to_S4'] + self.HYSTERESIS:
                if soc > self.THRESHOLDS['S2_to_S3'] + self.HYSTERESIS:
                    if soc > self.THRESHOLDS['S1_to_S2'] + self.HYSTERESIS:
                        self.current_state = 'S1_FULL'
                    else:
                        self.current_state = 'S2_PROOF_ONLY'
                else:
                    self.current_state = 'S3_RELAY_ONLY'
        elif self.current_state == 'S3_RELAY_ONLY':
            if soc <= self.THRESHOLDS['S3_to_S4']:
                self.current_state = 'S4_PRIMARY_ONLY'
            elif soc > self.THRESHOLDS['S2_to_S3'] + self.HYSTERESIS:
                if soc > self.THRESHOLDS['S1_to_S2'] + self.HYSTERESIS:
                    self.current_state = 'S1_FULL'
                else:
                    self.current_state = 'S2_PROOF_ONLY'
        elif self.current_state == 'S2_PROOF_ONLY':
            if soc <= self.THRESHOLDS['S2_to_S3']:
                if soc <= self.THRESHOLDS['S3_to_S4']:
                    self.current_state = 'S4_PRIMARY_ONLY'
                else:
                    self.current_state = 'S3_RELAY_ONLY'
            elif soc > self.THRESHOLDS['S1_to_S2'] + self.HYSTERESIS:
                self.current_state = 'S1_FULL'
        elif self.current_state == 'S1_FULL':
            if soc <= self.THRESHOLDS['S1_to_S2']:
                if soc <= self.THRESHOLDS['S2_to_S3']:
                    if soc <= self.THRESHOLDS['S3_to_S4']:
                        self.current_state = 'S4_PRIMARY_ONLY'
                    else:
                        self.current_state = 'S3_RELAY_ONLY'
                else:
                    self.current_state = 'S2_PROOF_ONLY'

        return self.current_state

    def get_blockchain_ops(self, state: str) -> dict:
        if state == 'S1_FULL':
            return {'sign_proofs': True, 'submit_tx': True, 'relay_peers': True}
        elif state == 'S2_PROOF_ONLY':
            return {'sign_proofs': True, 'submit_tx': True, 'relay_peers': False}
        elif state == 'S3_RELAY_ONLY':
            return {'sign_proofs': False, 'submit_tx': False, 'relay_peers': True}
        else: # S4_PRIMARY_ONLY
            return {'sign_proofs': False, 'submit_tx': False, 'relay_peers': False}

    def primary_task_active(self, state: str) -> bool:
        return True  # INVARIANT: primary task is ALWAYS preserved

    def transition_log(self, soc_series: list) -> list:
        log = []
        for i, soc in enumerate(soc_series):
            # For simplicity, timestamp is index
            state = self.get_state(soc)
            log.append((i, state))
        return log
