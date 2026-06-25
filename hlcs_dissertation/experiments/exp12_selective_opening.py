import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import time
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from core import hybrid_commitment
import config

plt.rcParams.update({'font.size': 11, 'axes.titlesize': 13, 'axes.labelsize': 11, 'xtick.labelsize': 10, 'ytick.labelsize': 10, 'figure.dpi': 300, 'savefig.dpi': 300})
sns.set_theme(style="whitegrid")

def run():
    print("Running Exp12: Selective Opening Benchmark")
    k = 10
    subsets = [1, 2, 5, 8, 10]
    msg = b'K'*config.MSG_BYTES
    pp = hybrid_commitment.setup(config.N, config.Q, config.SIGMA, seed=config.SEED)

    # Pre-commit k messages
    commits = []
    hints = []
    for _ in range(k):
        C, h, _ = hybrid_commitment.commit(pp, msg)
        commits.append(C)
        hints.append(h)

    results = []

    # Full open baseline
    t0 = time.perf_counter_ns()
    for i in range(k):
        hybrid_commitment.full_verify_C2(pp, commits[i][1], hints[i][0], hints[i][1], hints[i][2])
    t1 = time.perf_counter_ns()
    full_open_time = (t1 - t0) / 1e6
    full_open_comm = k * (hints[0][0].nbytes + hints[0][1].nbytes + len(hints[0][2]))

    for s in subsets:
        t0 = time.perf_counter_ns()
        for i in range(s):
            hybrid_commitment.full_verify_C2(pp, commits[i][1], hints[i][0], hints[i][1], hints[i][2])
        t1 = time.perf_counter_ns()
        open_time = (t1 - t0) / 1e6
        comm_bytes = s * (hints[0][0].nbytes + hints[0][1].nbytes + len(hints[0][2]))

        results.append({
            's': s,
            'open_time_ms': open_time,
            'comm_bytes': comm_bytes,
            'vs_full_open': open_time / full_open_time
        })

    df = pd.DataFrame(results)
    df.to_csv('../tables/TABLE_18_Selective_Opening.csv', index=False)

    plt.figure(figsize=(10, 6))
    sns.barplot(data=df, x='s', y='comm_bytes', color="#2E86AB")
    plt.axhline(full_open_comm, color='red', linestyle='--', label='Full Open Communication')
    plt.xlabel('Number of Opened Messages (s)')
    plt.ylabel('Communication Overhead (Bytes)')
    plt.title('Figure 21: Communication Overhead of Selective Opening')
    plt.legend()
    plt.savefig('../figures/fig21_selective_opening_overhead.png', bbox_inches='tight', pad_inches=0.1)
    plt.savefig('../figures/fig21_selective_opening_overhead.pdf', bbox_inches='tight', pad_inches=0.1)
    plt.close()

    with open('../figures/fig21_selective_opening_overhead.txt', 'w') as f:
        f.write("Figure 21: Bar chart displaying the communication overhead of selectively opening subsets of a batch of 10 commitments.")

    print("Exp12 completed.")
    return 1, 1
