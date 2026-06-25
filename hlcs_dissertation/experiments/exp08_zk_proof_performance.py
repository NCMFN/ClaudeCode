import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from core import zk_proof, hybrid_commitment
import config

plt.rcParams.update({'font.size': 11, 'axes.titlesize': 13, 'axes.labelsize': 11, 'xtick.labelsize': 10, 'ytick.labelsize': 10, 'figure.dpi': 300, 'savefig.dpi': 300})
sns.set_theme(style="whitegrid")

def run(n_trials=1000):
    print(f"Running Exp08: ZK Proof Performance ({n_trials} trials)")
    pp = hybrid_commitment.setup(config.N, config.Q, config.SIGMA, seed=config.SEED)
    msg = b'H'*config.MSG_BYTES

    stats = zk_proof.benchmark_prove_verify(pp, n_trials, msg)

    # Timing table
    df_time = pd.DataFrame([{
        'Operation': 'Prove',
        'Mean_ms': stats['prove_mean'],
        'Std_ms': stats['prove_std'],
        'P95_ms': stats['prove_p95']
    }, {
        'Operation': 'Verify',
        'Mean_ms': stats['verify_mean'],
        'Std_ms': stats['verify_std'],
        'P95_ms': stats['verify_p95']
    }])
    df_time.to_csv('../tables/TABLE_13_ZK_Timing.csv', index=False)

    # Size table
    sizes = stats['sizes']
    df_size = pd.DataFrame([{
        'Component': 'C_bar', 'Bytes': sizes[0]
    }, {
        'Component': 'z_r', 'Bytes': sizes[1]
    }, {
        'Component': 'z_e', 'Bytes': sizes[2]
    }, {
        'Component': 'c (Challenge)', 'Bytes': sizes[3] - sum(sizes[:3])
    }, {
        'Component': 'Total', 'Bytes': sizes[3]
    }])
    df_size.to_csv('../tables/TABLE_14_ZK_Size.csv', index=False)

    # Figure 17
    hyb_latencies = []
    for _ in range(n_trials):
        _, _, t = hybrid_commitment.commit(pp, msg)
        hyb_latencies.append(t[0] / 1e6)
    hyb_mean = np.mean(hyb_latencies)

    palette = ["#1F4E79", "#2E86AB"]

    plt.figure(figsize=(10, 6))
    sns.barplot(x=['Plain Hybrid Commit', 'ZK Prove', 'ZK Verify'],
                y=[hyb_mean, stats['prove_mean'], stats['verify_mean']],
                hue=['Plain Hybrid Commit', 'ZK Prove', 'ZK Verify'], legend=False, palette=["#A23B72", "#1F4E79", "#2E86AB"])
    plt.ylabel('Latency (ms)')
    plt.title('Figure 17: ZK Proof Overhead Comparison')
    for i, v in enumerate([hyb_mean, stats['prove_mean'], stats['verify_mean']]):
        plt.text(i, v + 0.05*v, f"{v:.3f} ms", ha='center')
    plt.savefig('../figures/fig17_zk_overhead_comparison.png', bbox_inches='tight', pad_inches=0.1)
    plt.savefig('../figures/fig17_zk_overhead_comparison.pdf', bbox_inches='tight', pad_inches=0.1)
    plt.close()

    with open('../figures/fig17_zk_overhead_comparison.txt', 'w') as f:
        f.write("Figure 17: Side-by-side bar chart comparing the latency of a plain hybrid commitment against the ZK prove and verify operations.")

    print("Exp08 completed.")
    return 2, 1
