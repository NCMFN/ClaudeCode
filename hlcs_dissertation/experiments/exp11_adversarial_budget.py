import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from core import security_analysis
import config

plt.rcParams.update({'font.size': 11, 'axes.titlesize': 13, 'axes.labelsize': 11, 'xtick.labelsize': 10, 'ytick.labelsize': 10, 'figure.dpi': 300, 'savefig.dpi': 300})
sns.set_theme(style="whitegrid")

def run():
    print("Running Exp11: Latency-Adaptive Security")
    taus = [0.1, 0.5, 1, 5, 10, 100, 1000] # ms

    n = config.N
    grover = security_analysis.compute_grover_bound(256) # 256 bit hash -> 128 bit security
    bkz = 2**(0.292 * n)

    results = []

    for tau in taus:
        max_ops = tau * 1e9 # 10^9 ops per ms as an aggressive upper bound for an adversary
        las_secure = max_ops < grover and max_ops < bkz

        results.append({
            'tau_ms': tau,
            'max_ops': max_ops,
            'Grover_ratio': max_ops / grover,
            'BKZ_ratio': max_ops / bkz,
            'LAS_secure': las_secure
        })

    df = pd.DataFrame(results)
    df.to_csv('../tables/TABLE_17_LAS_Security.csv', index=False)

    plt.figure(figsize=(10, 6))
    plt.plot(df['tau_ms'], df['max_ops'], label='Adversary Budget', marker='o', color="#1F4E79")
    plt.axhline(grover, color='red', linestyle='--', label=f'Grover Bound ({grover:.1e})')
    plt.axhline(bkz, color='orange', linestyle='--', label=f'BKZ Bound ({bkz:.1e})')
    plt.xscale('log')
    plt.yscale('log')
    plt.xlabel('Latency Window τ (ms)')
    plt.ylabel('Operations')
    plt.title('Figure 20: LAS Adversary Budget vs Security Bounds')
    plt.legend()
    plt.savefig('../figures/fig20_las_adversary_budget.png', bbox_inches='tight', pad_inches=0.1)
    plt.savefig('../figures/fig20_las_adversary_budget.pdf', bbox_inches='tight', pad_inches=0.1)
    plt.close()

    with open('../figures/fig20_las_adversary_budget.txt', 'w') as f:
        f.write("Figure 20: Log-log plot comparing the maximum quantum adversary operations budget against Grover and BKZ bounds over varying latency windows τ.")

    print("Exp11 completed.")
    return 1, 1

if __name__ == '__main__':
    run()
