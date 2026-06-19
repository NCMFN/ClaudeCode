import time
import numpy as np
import pandas as pd
import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from hlcs.commitment import HLCSSetup, HLCSCommitment, verify
from hlcs.params import DEFAULT_PARAMS

def throughput_test():
    pp = HLCSSetup(DEFAULT_PARAMS)
    msg = b"Throughput Test"
    start_time = time.perf_counter()
    count = 0

    while time.perf_counter() - start_time < 5.0: # run for 5 seconds
        com = HLCSCommitment(pp, msg)
        count += 1

    ops_sec = count / 5.0
    print(f"Throughput benchmark complete: {ops_sec} ops/sec")

if __name__ == "__main__":
    throughput_test()
