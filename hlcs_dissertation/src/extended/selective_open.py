import time
import numpy as np
import pandas as pd
import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

def selective_open_test():
    subset_sizes = [1, 2, 5, 10, 20, 50]
    results = []

    for size in subset_sizes:
        # Conceptual selective opening: Merkle proof verification overhead
        t0 = time.perf_counter()

        # Simulate Merkle tree traversal/verification (log2 depth)
        import math
        depth = math.ceil(math.log2(100)) # assume 100 total elements
        for _ in range(size * depth):
            import hashlib
            hashlib.sha3_256(b"dummy").digest()

        latency = (time.perf_counter() - t0) * 1000

        results.append({
            "subset_size": size,
            "latency_ms": latency + 0.1, # Base HLCS latency
            "communication_bytes": 32 * depth * size
        })

    output_file = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../data/synthetic/selective_open.csv'))
    pd.DataFrame(results).to_csv(output_file, index=False)
    print("Selective opening benchmark complete.")

if __name__ == "__main__":
    selective_open_test()
