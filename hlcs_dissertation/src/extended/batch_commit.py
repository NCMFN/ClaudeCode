import time
import numpy as np
import pandas as pd
import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from hlcs.commitment import HLCSSetup, HLCSCommitment, verify
from hlcs.params import DEFAULT_PARAMS

def batch_commit_test():
    pp = HLCSSetup(DEFAULT_PARAMS)
    batch_sizes = [1, 5, 10, 50, 100, 500]
    results = []

    for size in batch_sizes:
        messages = [f"Message {i}".encode() for i in range(size)]

        t0 = time.perf_counter()

        # Simulated batch commitment: commit to hash of all messages
        # O(N) overhead reduction conceptual
        import hashlib
        h = hashlib.sha3_256()
        for m in messages:
            h.update(m)
        batch_hash = h.digest()

        com = HLCSCommitment(pp, batch_hash)
        latency = (time.perf_counter() - t0) * 1000

        results.append({
            "batch_size": size,
            "mean_latency_ms": latency,
            "throughput_ops_sec": size / (latency / 1000) if latency > 0 else 0
        })

    output_file = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../data/synthetic/batch_results.csv'))
    pd.DataFrame(results).to_csv(output_file, index=False)
    print("Batch commit benchmark complete.")

if __name__ == "__main__":
    batch_commit_test()
