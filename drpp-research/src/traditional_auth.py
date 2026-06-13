import random
import numpy as np
from typing import Dict, Any

class TraditionalAuth:
    """
    Models traditional ambient-cue-based authentication (voice, sound, visual signals).
    """
    def __init__(self, random_seed: int = None):
        """
        Args:
            random_seed (int): Random seed for reproducibility.
        """
        self.attack_success_probability = 0.34
        if random_seed is not None:
            random.seed(random_seed)
            np.random.seed(random_seed)

    def simulate(self, n_trials: int) -> Dict[str, Any]:
        """
        Simulates the traditional authentication attack over multiple trials.

        Each trial: adversary randomly controls ambient cues.
        Model as Bernoulli(0.34) for attack success.

        Args:
            n_trials (int): Number of trials.

        Returns:
            Dict: Simulation results including success_rate, n_trials, std_error.
        """
        # Run n_trials as a binomial distribution
        successes = np.random.binomial(n_trials, self.attack_success_probability)
        success_rate = successes / n_trials

        # Standard error for proportion: sqrt(p * (1-p) / n)
        std_error = np.sqrt(success_rate * (1 - success_rate) / n_trials)

        return {
            "success_rate": success_rate,
            "n_trials": n_trials,
            "std_error": std_error
        }
