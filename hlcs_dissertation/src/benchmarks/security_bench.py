"""
Security parameter sweep: latency vs. n, q, sigma.
Generates data for heatmap Figure (Section VII-I of paper).
Outputs: data/synthetic/security_sweep.csv
"""
import numpy as np
import pandas as pd
import time
import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from hlcs.commitment import HLCSSetup, HLCSCommitment, verify

MESSAGE = b"test_message_security_sweep"
TRIALS = 1000
N_VALUES = [128, 256, 512, 768, 1024]
LOAD_VALUES = [10, 50, 100, 200, 500]

results = []
for n in N_VALUES:
    for load in LOAD_VALUES:
        params = {"n": n, "q": 12289, "sigma": 3.2, "B": 16, "security_bits": n // 4}
        pp = HLCSSetup(params)
        latencies = []
        for _ in range(min(TRIALS, load)):
            t0 = time.perf_counter()
            com = HLCSCommitment(pp, MESSAGE)
            C1, C2 = com.commitment
            r, e, m = com.opening_hint
            verify(pp, C1, C2, r, e, m)
            latencies.append((time.perf_counter() - t0) * 1000)
        results.append({"n": n, "order_load": load, "mean_latency_ms": np.mean(latencies)})

output_file = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../data/synthetic/security_sweep.csv'))

pd.DataFrame(results).to_csv(output_file, index=False)
print("Security sweep complete.")
