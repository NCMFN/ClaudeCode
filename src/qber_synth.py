import numpy as np
def generate_qber_series(num_points, config): return np.random.RandomState(config['random_seed']).uniform(config['qber_range'][0], config['qber_range'][1], size=num_points)
