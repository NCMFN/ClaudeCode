import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from core import hash_commitment, lattice_commitment, hybrid_commitment
import config

plt.rcParams.update({'font.size': 11, 'axes.titlesize': 13, 'axes.labelsize': 11, 'xtick.labelsize': 10, 'ytick.labelsize': 10, 'figure.dpi': 300, 'savefig.dpi': 300})
sns.set_theme(style="whitegrid")

def run(n_trials=10000):
    print(f"Running Exp01: Latency Microbenchmark ({n_trials} trials)")
    msg = b'A'*config.MSG_BYTES

    # Setups
    pp_hash = hash_commitment.setup()
    pp_lat = lattice_commitment.setup(config.N, config.Q, config.SIGMA, seed=config.SEED)
    pp_hyb = hybrid_commitment.setup(config.N, config.Q, config.SIGMA, seed=config.SEED)

    hash_t = []
    lat_t = []
    hyb_t = []

    for _ in range(n_trials):
        _, t = hash_commitment.commit(pp_hash, msg)
        hash_t.append(t / 1e6) # ms

        _, t = lattice_commitment.commit(pp_lat, msg)
        lat_t.append(t / 1e6)

        _, _, t_tuple = hybrid_commitment.commit(pp_hyb, msg)
        hyb_t.append(t_tuple[0] / 1e6)

    df = pd.DataFrame({
        'Hash': hash_t,
        'Lattice': lat_t,
        'Hybrid': hyb_t
    })

    # Calculate stats
    stats = []
    for col in df.columns:
        s = df[col]
        stats.append({
            'Scheme': col,
            'Mean': s.mean(),
            'Std': s.std(),
            'Median': s.median(),
            'P5': s.quantile(0.05),
            'P25': s.quantile(0.25),
            'P75': s.quantile(0.75),
            'P95': s.quantile(0.95),
            'P99': s.quantile(0.99),
            'Min': s.min(),
            'Max': s.max()
        })
    df_stats = pd.DataFrame(stats)
    df_stats.to_csv('../tables/TABLE_01_Latency_Summary.csv', index=False)

    # Percentiles table
    percentiles = range(1, 100)
    pct_dict = {'Percentile': percentiles}
    for col in df.columns:
        pct_dict[col] = [df[col].quantile(p/100) for p in percentiles]
    df_pct = pd.DataFrame(pct_dict)
    df_pct.to_csv('../tables/TABLE_02_Latency_Percentiles.csv', index=False)

    palette = ["#1F4E79", "#2E86AB", "#A23B72"]

    # Boxplot
    plt.figure(figsize=(10, 6))
    sns.boxplot(data=df, palette=palette)
    plt.yscale('log')
    plt.ylabel('Latency (ms)')
    plt.title('Figure 1: Latency Microbenchmark (Boxplot)')
    plt.savefig('../figures/fig01_boxplot_latency_comparison.png', bbox_inches='tight', pad_inches=0.1)
    plt.savefig('../figures/fig01_boxplot_latency_comparison.pdf', bbox_inches='tight', pad_inches=0.1)
    plt.close()

    with open('../figures/fig01_boxplot_latency_comparison.txt', 'w') as f:
        f.write("Figure 1: Boxplot comparing the commit latency of Hash-only, Lattice-only, and Hybrid schemes on a logarithmic scale.")

    # Violin plot
    plt.figure(figsize=(10, 6))
    sns.violinplot(data=df, palette=palette, inner="quartile")
    plt.yscale('log')
    plt.ylabel('Latency (ms)')
    plt.title('Figure 2: Latency Microbenchmark (Violin)')
    plt.savefig('../figures/fig02_violin_latency.png', bbox_inches='tight', pad_inches=0.1)
    plt.savefig('../figures/fig02_violin_latency.pdf', bbox_inches='tight', pad_inches=0.1)
    plt.close()

    with open('../figures/fig02_violin_latency.txt', 'w') as f:
        f.write("Figure 2: Violin plot showing the distribution of commit latencies with embedded quartile markers.")

    # CDF
    plt.figure(figsize=(10, 6))
    sns.ecdfplot(data=df, palette=palette)
    plt.xscale('log')
    plt.xlabel('Latency (ms)')
    plt.ylabel('Cumulative Probability')
    plt.title('Figure 3: Latency CDF')
    plt.savefig('../figures/fig03_cdf_latency.png', bbox_inches='tight', pad_inches=0.1)
    plt.savefig('../figures/fig03_cdf_latency.pdf', bbox_inches='tight', pad_inches=0.1)
    plt.close()

    with open('../figures/fig03_cdf_latency.txt', 'w') as f:
        f.write("Figure 3: Cumulative Distribution Function (CDF) curves for all 3 schemes on a log-x scale.")

    print("Exp01 completed.")
    return 2, 3

if __name__ == '__main__':
    run()
