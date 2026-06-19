import time
import numpy as np
import pandas as pd
import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from hlcs.commitment import HLCSSetup, HLCSCommitment
from hlcs.zk_proof import prove, verify_proof
from hlcs.params import DEFAULT_PARAMS

def zk_bench_test():
    pp = HLCSSetup(DEFAULT_PARAMS)
    results = []

    for _ in range(100):
        msg = b"ZK Bench Test"
        com = HLCSCommitment(pp, msg)
        C = com.commitment
        r, e, m = com.opening_hint

        t0 = time.perf_counter()
        proof = prove(pp, C, r, e, m)
        prove_time = (time.perf_counter() - t0) * 1000

        t1 = time.perf_counter()
        verify_proof(pp, C, m, proof)
        verify_time = (time.perf_counter() - t1) * 1000

        results.append({
            "param_set": "HLCS-256",
            "prove_ms": prove_time,
            "verify_ms": verify_time
        })

    output_file = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../data/synthetic/zk_latency.csv'))
    pd.DataFrame(results).to_csv(output_file, index=False)
    print("ZK benchmark complete.")

if __name__ == "__main__":
    zk_bench_test()
