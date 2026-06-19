"""
Micro-benchmark: 100,000 HybridCommit + Verify cycles.
Replicates Table I and Table III from the paper.
Outputs: data/synthetic/latency_results.csv
"""
import time, csv, numpy as np
import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from hlcs.commitment import HLCSSetup, HLCSCommitment, verify
from hlcs.params import PARAM_SETS

TRIALS = 1000
MESSAGE = b"EUR/USD 1500.00 BUY 2025-01-01T00:00:00Z"

results = []
for name, params in PARAM_SETS.items():
    pp = HLCSSetup(params)
    latencies = []
    for _ in range(TRIALS):
        t0 = time.perf_counter()
        com = HLCSCommitment(pp, MESSAGE)
        C1, C2 = com.commitment
        r, e, m = com.opening_hint
        ok = verify(pp, C1, C2, r, e, m)
        latencies.append((time.perf_counter() - t0) * 1000)
    arr = np.array(latencies)
    results.append({
        "param_set": name,
        "n": params["n"],
        "q": params["q"],
        "security_bits": params["security_bits"],
        "mean_ms": arr.mean(),
        "std_ms": arr.std(),
        "p50_ms": np.percentile(arr, 50),
        "p95_ms": np.percentile(arr, 95),
        "p99_ms": np.percentile(arr, 99),
        "min_ms": arr.min(),
        "max_ms": arr.max(),
        "throughput_ops_sec": 1000 / arr.mean()
    })

output_file = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../data/synthetic/latency_results.csv'))

with open(output_file, "w", newline="") as f:
    writer = csv.DictWriter(f, fieldnames=results[0].keys())
    writer.writeheader()
    writer.writerows(results)

print("Latency benchmark complete. Results saved.")
