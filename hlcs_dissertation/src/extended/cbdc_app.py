import time
import numpy as np
import pandas as pd
import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from hlcs.commitment import HLCSSetup, HLCSCommitment, verify
from hlcs.params import DEFAULT_PARAMS

def cbdc_test():
    pp = HLCSSetup(DEFAULT_PARAMS)
    volumes = [1000, 5000, 10000]
    results = []

    for vol in volumes:
        latencies = []
        errors = 0
        for _ in range(vol):
            t0 = time.perf_counter()
            msg = b"CBDC TX 1.00 USD"
            com = HLCSCommitment(pp, msg)
            latency = (time.perf_counter() - t0) * 1000
            latencies.append(latency)
            if latency > 0.5:
                errors += 1

        results.append({
            "Volume": vol,
            "Latency": np.mean(latencies),
            "Errors": errors,
            "Throughput": vol / (np.sum(latencies)/1000)
        })

    output_file = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../data/synthetic/cbdc_results.csv'))
    pd.DataFrame(results).to_csv(output_file, index=False)
    print("CBDC benchmark complete.")

if __name__ == "__main__":
    cbdc_test()
