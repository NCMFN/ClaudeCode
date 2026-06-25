import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from core import hybrid_commitment, lwe_utils, security_analysis
import config

plt.rcParams.update({'font.size': 11, 'axes.titlesize': 13, 'axes.labelsize': 11, 'xtick.labelsize': 10, 'ytick.labelsize': 10, 'figure.dpi': 300, 'savefig.dpi': 300})
sns.set_theme(style="whitegrid")

def run():
    print("Running Exp09: Security Parameter Sweep")
    lambdas = [80, 100, 112, 128, 192, 256]
    msg = b'I'*config.MSG_BYTES

    results = []

    for lam in lambdas:
        # Simple heuristic mapping for n based on lambda to mimic NIST levels
        n = max(256, lam * 4)
        q = config.Q
        sigma = config.SIGMA

        pp = hybrid_commitment.setup(n, q, sigma, seed=config.SEED)
        latencies = []
        for _ in range(1000):
            _, _, t = hybrid_commitment.commit(pp, msg)
            latencies.append(t[0] / 1e6)

        avg_lat = np.mean(latencies)
        tp = 1000 / (sum(latencies)/1000) # approx throughput

        results.append({
            'lambda': lam,
            'n': n,
            'q': q,
            'Grover_ops': security_analysis.compute_grover_bound(lam*2), # Using hash size 2*lambda
            'BKZ_est_bits': 0.292 * n,
            'avg_latency_ms': avg_lat,
            'throughput': tp
        })

    df = pd.DataFrame(results)
    df.to_csv('../tables/TABLE_15_Security_Sweep.csv', index=False)

    # Dual-axis plot
    fig, ax1 = plt.subplots(figsize=(10, 6))

    color = '#1F4E79'
    ax1.set_xlabel('Security Parameter λ (bits)')
    ax1.set_ylabel('Latency (ms)', color=color)
    ax1.plot(df['lambda'], df['avg_latency_ms'], color=color, marker='o', label='Latency')
    ax1.tick_params(axis='y', labelcolor=color)

    ax2 = ax1.twinx()
    color = '#A23B72'
    ax2.set_ylabel('BKZ Cost (bits)', color=color)
    ax2.plot(df['lambda'], df['BKZ_est_bits'], color=color, marker='s', label='BKZ Security')
    ax2.tick_params(axis='y', labelcolor=color)

    plt.title('Figure 18: Security vs Performance Tradeoff')
    fig.tight_layout()
    plt.savefig('../figures/fig18_security_vs_latency_dual_axis.png', bbox_inches='tight', pad_inches=0.1)
    plt.savefig('../figures/fig18_security_vs_latency_dual_axis.pdf', bbox_inches='tight', pad_inches=0.1)
    plt.close()

    with open('../figures/fig18_security_vs_latency_dual_axis.txt', 'w') as f:
        f.write("Figure 18: Dual-axis plot showing the tradeoff between security parameter λ, commit latency, and estimated BKZ security strength.")

    print("Exp09 completed.")
    return 1, 1

if __name__ == '__main__':
    run()
