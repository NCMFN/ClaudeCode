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
from concurrent.futures import ThreadPoolExecutor

plt.rcParams.update({'font.size': 11, 'axes.titlesize': 13, 'axes.labelsize': 11, 'xtick.labelsize': 10, 'ytick.labelsize': 10, 'figure.dpi': 300, 'savefig.dpi': 300})
sns.set_theme(style="whitegrid")

def commit_task(pp, msg):
    _, _, t = hybrid_commitment.commit(pp, msg)
    return t[0] / 1e6

def run():
    print("Running Exp13: Multi-Trader Concurrency Simulation")
    T_vals = [1, 5, 10, 25, 50, 100]
    msg = b'L'*config.MSG_BYTES
    pp = hybrid_commitment.setup(config.N, config.Q, config.SIGMA, seed=config.SEED)

    results = []

    for T in T_vals:
        latencies = []
        t0 = time.perf_counter_ns()
        with ThreadPoolExecutor(max_workers=T) as executor:
            # Simulate 10 orders per trader
            futures = [executor.submit(commit_task, pp, msg) for _ in range(T * 10)]
            for future in futures:
                latencies.append(future.result())
        t1 = time.perf_counter_ns()

        total_time_s = (t1 - t0) / 1e9
        throughput = (T * 10) / total_time_s

        results.append({
            'T_traders': T,
            'mean_latency': np.mean(latencies),
            'P95_latency': np.percentile(latencies, 95),
            'P99_latency': np.percentile(latencies, 99),
            'throughput': throughput
        })

    df = pd.DataFrame(results)
    df.to_csv('../tables/TABLE_19_Concurrency.csv', index=False)

    plt.figure(figsize=(10, 6))
    plt.plot(df['T_traders'], df['P95_latency'], marker='o', color="#A23B72", label='P95 Latency')
    plt.plot(df['T_traders'], df['mean_latency'], marker='s', color="#1F4E79", label='Mean Latency')
    plt.xlabel('Number of Concurrent Traders')
    plt.ylabel('Latency (ms)')
    plt.title('Figure 22: Concurrency Contention Effect on Latency')
    plt.legend()
    plt.savefig('../figures/fig22_concurrency_p95_latency.png', bbox_inches='tight', pad_inches=0.1)
    plt.savefig('../figures/fig22_concurrency_p95_latency.pdf', bbox_inches='tight', pad_inches=0.1)
    plt.close()

    with open('../figures/fig22_concurrency_p95_latency.txt', 'w') as f:
        f.write("Figure 22: Line plot showing the effect of multi-trader contention on mean and P95 commit latency.")

    print("Exp13 completed.")
    return 1, 1

if __name__ == '__main__':
    run()
