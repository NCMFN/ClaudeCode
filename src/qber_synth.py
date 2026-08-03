import json
import numpy as np

def generate_qber_series(num_blocks, config):
    """
    Generate synthetic QBER data uniformly over the config-driven range.
    """
    np.random.seed(config["random_seed"])
    min_qber, max_qber = config["qber_range"]
    return np.random.uniform(min_qber, max_qber, num_blocks)
