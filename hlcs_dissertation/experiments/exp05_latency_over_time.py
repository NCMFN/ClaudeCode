import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from core import hybrid_commitment
import config

plt.rcParams.update({'font.size': 11, 'axes.titlesize': 13, 'axes.labelsize': 11, 'xtick.labelsize': 10, 'ytick.labelsize': 10, 'figure.dpi': 300, 'savefig.dpi': 300})
sns.set_theme(style="whitegrid")

def run(n_trials=1000):
    print(f"Running Exp05: Latency Over Time ({n_trials} trials)")
    msg = b'E'*config.MSG_BYTES
    pp = hybrid_commitment.setup(config.N, config.Q, config.SIGMA, seed=config.SEED)

    latencies = []
    for _ in range(n_trials):
        _, _, t = hybrid_commitment.commit(pp, msg)
        latencies.append(t[0] / 1e6)

    df = pd.DataFrame({'Order': range(n_trials), 'Latency': latencies})
    df['Rolling_Mean'] = df['Latency'].rolling(50).mean()
    df['Rolling_Std'] = df['Latency'].rolling(50).std()

    df_sampled = df.iloc[49::50].copy()
    df_sampled.to_csv('../tables/TABLE_09_Rolling_Stats.csv', index=False)

    palette = ["#1F4E79", "#2E86AB"]

    plt.figure(figsize=(10, 6))
    plt.plot(df['Order'], df['Latency'], alpha=0.3, color=palette[1], label='Latency')
    plt.plot(df['Order'], df['Rolling_Mean'], color=palette[0], label='Rolling Mean (w=50)')
    plt.axhline(0.2, color='red', linestyle='--', label='0.2ms Threshold')
    plt.axhline(1.0, color='orange', linestyle='--', label='1.0ms Threshold')
    plt.xlabel('Order')
    plt.ylabel('Latency (ms)')
    plt.title('Figure 12: Latency Stability Over Time')
    plt.legend()
    plt.savefig('../figures/fig12_latency_stability.png', bbox_inches='tight', pad_inches=0.1)
    plt.savefig('../figures/fig12_latency_stability.pdf', bbox_inches='tight', pad_inches=0.1)
    plt.close()

    with open('../figures/fig12_latency_stability.txt', 'w') as f:
        f.write("Figure 12: Latency per order over time for 1,000 sequential commits, with rolling mean and HFT budget thresholds.")

    print("Exp05 completed.")
    return 1, 1

if __name__ == '__main__':
    run()
