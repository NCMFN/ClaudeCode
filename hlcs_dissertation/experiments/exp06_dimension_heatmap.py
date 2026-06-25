import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from core import hybrid_commitment
import config
from mpl_toolkits.mplot3d import Axes3D

plt.rcParams.update({'font.size': 11, 'axes.titlesize': 13, 'axes.labelsize': 11, 'xtick.labelsize': 10, 'ytick.labelsize': 10, 'figure.dpi': 300, 'savefig.dpi': 300})
sns.set_theme(style="whitegrid")

def run():
    print("Running Exp06: Dimension vs Order Load Heatmap")
    dims = [128, 256, 512, 768, 1024]
    loads = [10, 50, 100, 200, 500]
    msg = b'F'*config.MSG_BYTES

    results = []

    for n in dims:
        # Message size can be at most n bits for encoding
        # n is the dimension. we encode MSG_BYTES bytes = MSG_BYTES*8 bits
        # So we need n >= MSG_BYTES*8 = 32*8 = 256
        # If n < 256, we'll get an error "Message too long to encode"
        # So if n < 256, we must truncate the message just for this benchmark
        actual_msg = msg[:n // 8]

        pp = hybrid_commitment.setup(n, config.Q, config.SIGMA, seed=config.SEED)
        for load in loads:
            latencies = []
            for _ in range(load):
                _, _, t = hybrid_commitment.commit(pp, actual_msg)
                latencies.append(t[0] / 1e6)
            results.append({
                'Dimension': n,
                'Load': load,
                'Avg_Latency_ms': np.mean(latencies)
            })

    df = pd.DataFrame(results)
    pivot = df.pivot(index='Dimension', columns='Load', values='Avg_Latency_ms')
    pivot.to_csv('../tables/TABLE_10_Dimension_Heatmap.csv')

    plt.figure(figsize=(12, 8))
    sns.heatmap(pivot, annot=True, fmt=".3f", cmap="YlGnBu")
    plt.title('Figure 13: Average Latency by Dimension and Order Load (ms)')
    plt.savefig('../figures/fig13_dimension_heatmap.png', bbox_inches='tight', pad_inches=0.1)
    plt.savefig('../figures/fig13_dimension_heatmap.pdf', bbox_inches='tight', pad_inches=0.1)
    plt.close()

    with open('../figures/fig13_dimension_heatmap.txt', 'w') as f:
        f.write("Figure 13: Heatmap of average commit latency (ms) varying lattice dimension and order load.")

    fig = plt.figure(figsize=(10, 8))
    ax = fig.add_subplot(111, projection='3d')
    X, Y = np.meshgrid(loads, dims)
    Z = pivot.values
    surf = ax.plot_surface(X, Y, Z, cmap="YlGnBu", edgecolor='none')
    ax.set_xlabel('Load')
    ax.set_ylabel('Dimension')
    ax.set_zlabel('Latency (ms)')
    plt.title('Figure 14: 3D Surface Plot of Latency')
    fig.colorbar(surf, shrink=0.5, aspect=5)
    plt.savefig('../figures/fig14_3d_surface_latency.png', bbox_inches='tight', pad_inches=0.1)
    plt.savefig('../figures/fig14_3d_surface_latency.pdf', bbox_inches='tight', pad_inches=0.1)
    plt.close()

    with open('../figures/fig14_3d_surface_latency.txt', 'w') as f:
        f.write("Figure 14: 3D surface plot representing the relationship between lattice dimension, order load, and latency.")

    print("Exp06 completed.")
    return 1, 2

if __name__ == '__main__':
    run()
