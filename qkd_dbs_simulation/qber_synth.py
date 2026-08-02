import numpy as np

def generate_qber_series(num_blocks, config):
    rng = np.random.default_rng(config["random_seed"])
    qber_min, qber_max = config["qber_range"]
    return rng.uniform(qber_min, qber_max, size=num_blocks)
if __name__ == "__main__":
    test_config = {
        "random_seed": 42,
        "qber_range": [0.02, 0.05]
    }
    qbers = generate_qber_series(5, test_config)
    print("Generated QBERs:", qbers)
    assert all(0.02 <= q <= 0.05 for q in qbers)
    print("qber_synth.py verified.")
