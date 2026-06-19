import time
import numpy as np
import pandas as pd
import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from hlcs.commitment import HLCSSetup, HLCSCommitment, verify
from hlcs.params import PARAM_SETS

def iot_test():
    devices = [
        {"name": "Class 1", "params": "HLCS-128"},
        {"name": "Class 2", "params": "HLCS-256"}
    ]
    results = []

    for dev in devices:
        pp = HLCSSetup(PARAM_SETS[dev["params"]])
        latencies = []
        for _ in range(100):
            t0 = time.perf_counter()
            msg = b"Sensor Data"
            com = HLCSCommitment(pp, msg)
            latency = (time.perf_counter() - t0) * 1000
            # Add artificial delay to simulate slow IoT CPU
            simulated_latency = latency * (5 if dev["name"] == "Class 1" else 2)
            latencies.append(simulated_latency)

        results.append({
            "Device": dev["name"],
            "Latency (ms)": np.mean(latencies),
            "Param Set": dev["params"]
        })

    output_file = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../data/synthetic/iot_results.csv'))
    pd.DataFrame(results).to_csv(output_file, index=False)
    print("IoT benchmark complete.")

if __name__ == "__main__":
    iot_test()
