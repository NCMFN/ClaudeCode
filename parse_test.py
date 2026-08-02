import os
import pandas as pd
import numpy as np

def test_parse():
    dir_path = "/home/jules/workspace/NetLatency-Data/Seattle"
    samples = []
    # Just 10 files for test
    for i in range(1, 11):
        file_path = os.path.join(dir_path, f"SeattleData_{i}")
        df = pd.read_csv(file_path, sep='\t', header=None)
        # Flatten and filter out 0
        vals = df.values.flatten()
        vals = vals[vals > 0]
        samples.append(vals)
    all_samples = np.concatenate(samples)
    print(f"Total samples in 10 files: {len(all_samples)}")
    print(f"Mean RTT: {np.mean(all_samples)}")

test_parse()
