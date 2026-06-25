import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import time
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from core import hash_commitment, lattice_commitment, hybrid_commitment
import config

plt.rcParams.update({'font.size': 11, 'axes.titlesize': 13, 'axes.labelsize': 11, 'xtick.labelsize': 10, 'ytick.labelsize': 10, 'figure.dpi': 300, 'savefig.dpi': 300})
sns.set_theme(style="whitegrid")

def run():
    print("Running Exp02: Throughput Comparison")
    msg = b'B'*config.MSG_BYTES
    batch_sizes = [100, 500, 1000, 5000, 10000] # Reduced max for reasonable python simulation time

    pp_hash = hash_commitment.setup()
    pp_lat = lattice_commitment.setup(config.N, config.Q, config.SIGMA, seed=config.SEED)
    pp_hyb = hybrid_commitment.setup(config.N, config.Q, config.SIGMA, seed=config.SEED)

    results = []

    for bs in batch_sizes:
        # Hash
        t0 = time.perf_counter_ns()
        for _ in range(bs):
            hash_commitment.commit(pp_hash, msg)
        t1 = time.perf_counter_ns()
        hash_ops = bs / ((t1-t0)/1e9)

        # Lattice
        t0 = time.perf_counter_ns()
        for _ in range(bs):
            lattice_commitment.commit(pp_lat, msg)
        t1 = time.perf_counter_ns()
        lat_ops = bs / ((t1-t0)/1e9)

        # Hybrid
        t0 = time.perf_counter_ns()
        for _ in range(bs):
            hybrid_commitment.commit(pp_hyb, msg)
        t1 = time.perf_counter_ns()
        hyb_ops = bs / ((t1-t0)/1e9)

        results.append({
            'Batch_Size': bs,
            'Hash_Throughput': hash_ops,
            'Lattice_Throughput': lat_ops,
            'Hybrid_Throughput': hyb_ops
        })

    df = pd.DataFrame(results)
    df.to_csv('../tables/TABLE_03_Throughput.csv', index=False)

    df['Hyb_vs_Hash_Ratio'] = df['Hash_Throughput'] / df['Hybrid_Throughput']
    df['Hyb_vs_Lat_Ratio'] = df['Lattice_Throughput'] / df['Hybrid_Throughput']
    df[['Batch_Size', 'Hyb_vs_Hash_Ratio', 'Hyb_vs_Lat_Ratio']].to_csv('../tables/TABLE_04_Overhead.csv', index=False)

    palette = ["#1F4E79", "#2E86AB", "#A23B72"]

    # Bar chart for max batch
    max_batch = df.iloc[-1]
    plt.figure(figsize=(10, 6))
    sns.barplot(x=['Hash', 'Lattice', 'Hybrid'],
                y=[max_batch['Hash_Throughput'], max_batch['Lattice_Throughput'], max_batch['Hybrid_Throughput']],
                hue=['Hash', 'Lattice', 'Hybrid'], legend=False, palette=palette)
    plt.yscale('log')
    plt.ylabel('Throughput (ops/sec)')
    plt.title('Figure 4: Maximum Sustainable Throughput')
    plt.savefig('../figures/fig04_throughput_bar.png', bbox_inches='tight', pad_inches=0.1)
    plt.savefig('../figures/fig04_throughput_bar.pdf', bbox_inches='tight', pad_inches=0.1)
    plt.close()

    with open('../figures/fig04_throughput_bar.txt', 'w') as f:
        f.write("Figure 4: Bar chart showing maximum sustainable orders/sec for each scheme over a 1-second window on a logarithmic scale.")

    # Line plot vs batch size
    plt.figure(figsize=(10, 6))
    plt.plot(df['Batch_Size'], df['Hash_Throughput'], label='Hash', marker='o', color="#1F4E79")
    plt.plot(df['Batch_Size'], df['Lattice_Throughput'], label='Lattice', marker='s', color="#2E86AB")
    plt.plot(df['Batch_Size'], df['Hybrid_Throughput'], label='Hybrid', marker='^', color="#A23B72")
    plt.xscale('log')
    plt.yscale('log')
    plt.xlabel('Batch Size')
    plt.ylabel('Throughput (ops/sec)')
    plt.legend()
    plt.title('Figure 5: Throughput vs Batch Size')
    plt.savefig('../figures/fig05_throughput_vs_batchsize.png', bbox_inches='tight', pad_inches=0.1)
    plt.savefig('../figures/fig05_throughput_vs_batchsize.pdf', bbox_inches='tight', pad_inches=0.1)
    plt.close()

    with open('../figures/fig05_throughput_vs_batchsize.txt', 'w') as f:
        f.write("Figure 5: Line plot of throughput vs. batch size for all 3 schemes.")

    print("Exp02 completed.")
    return 2, 2

if __name__ == '__main__':
    run()
