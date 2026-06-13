import random
from typing import List, Dict, Any

class PresenceDenialAttack:
    """
    Simulates Algorithm 1: Adversarial Presence Denial.
    Adversary controls C_a to forge evidence set E'.
    """
    def __init__(self, belief_threshold: float = 0.5, random_seed: int = None):
        """
        Args:
            belief_threshold (float): Verifier belief threshold below which presence is denied.
            random_seed (int): Random seed for reproducibility.
        """
        self.belief_threshold = belief_threshold
        if random_seed is not None:
            random.seed(random_seed)
        self.results = []

    def attack(self, evidence_set: List[float]) -> bool:
        """
        Randomly forge a subset E' of E via ambient channel C_a.

        Args:
            evidence_set (List[float]): Initial evidence set values.

        Returns:
            bool: True if forged set flips verifier belief to False (attack success).
        """
        # The adversary suppresses some of the evidence to lower the verifier's belief.
        # We simulate this by taking a random subset or attenuating the evidence.
        forged_evidence = [e * random.uniform(0, 1) for e in evidence_set]

        # Calculate belief as average of evidence
        belief = sum(forged_evidence) / len(forged_evidence) if forged_evidence else 0.0

        # Attack succeeds if belief falls below threshold
        success = belief < self.belief_threshold

        return success

    def simulate(self, n_trials: int) -> float:
        """
        Simulates the attack over multiple trials.

        Args:
            n_trials (int): Number of trials.

        Returns:
            float: Attack success rate.
        """
        successes = 0
        for _ in range(n_trials):
            # Generate a random initial evidence set that strongly supports presence
            evidence_set = [random.uniform(0.7, 1.0) for _ in range(5)]
            if self.attack(evidence_set):
                successes += 1

        success_rate = successes / n_trials
        self.results.append({"n_trials": n_trials, "success_rate": success_rate})
        return success_rate

class AmbientSignalInjection:
    """
    Simulates Algorithm 2: Ambient Signal Injection.
    A2 injects signals to grant access to hidden A1.
    """
    def __init__(self, signal_strength: float, random_seed: int = None):
        """
        Args:
            signal_strength (float): Injection fidelity, 0.0-1.0.
            random_seed (int): Random seed for reproducibility.
        """
        self.signal_strength = signal_strength
        if random_seed is not None:
            random.seed(random_seed)
        self.results = []

    def inject(self, verifier_belief: float) -> float:
        """
        Injects signals to artificially boost the verifier's belief.

        Args:
            verifier_belief (float): Initial belief without injection.

        Returns:
            float: Manipulated belief after injection.
        """
        # The adversary attempts to boost the belief towards 1.0 based on signal strength
        boost = (1.0 - verifier_belief) * self.signal_strength * random.uniform(0.8, 1.0)
        return min(1.0, verifier_belief + boost)

    def simulate(self, n_trials: int, drpp_active: bool) -> Dict[str, Any]:
        """
        Simulates the injection attack.

        Args:
            n_trials (int): Number of trials.
            drpp_active (bool): True if DRPP protocol is active.

        Returns:
            Dict: Simulation results including success_rate, mean_manipulated_belief, attack_blocked_rate.
        """
        successes = 0
        blocked = 0
        total_manipulated_belief = 0.0

        # Assume a threshold of 0.5 for granting access
        access_threshold = 0.5

        for _ in range(n_trials):
            # Initial low belief (A1 is hidden)
            initial_belief = random.uniform(0.0, 0.3)

            if drpp_active:
                # DRPP blocks C_a manipulation; belief comes from C_d only
                # Since A1 cannot complete DRPP (no secret), belief stays low
                final_belief = initial_belief
                blocked += 1
            else:
                # Traditional auth; belief from ambient only
                final_belief = self.inject(initial_belief)

            total_manipulated_belief += final_belief
            if final_belief >= access_threshold:
                successes += 1

        success_rate = successes / n_trials
        mean_belief = total_manipulated_belief / n_trials
        blocked_rate = blocked / n_trials

        result = {
            "success_rate": success_rate,
            "mean_manipulated_belief": mean_belief,
            "attack_blocked_rate": blocked_rate
        }
        self.results.append(result)
        return result
