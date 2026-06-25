import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from core.lwe_utils import discrete_gaussian_cdf
import config

plt.rcParams.update({'font.size': 11, 'axes.titlesize': 13, 'axes.labelsize': 11, 'xtick.labelsize': 10, 'ytick.labelsize': 10, 'figure.dpi': 300, 'savefig.dpi': 300})
sns.set_theme(style="whitegrid")

def run():
    print("Running Exp07: Decryption Failure Probability")

    B_sigmas = [1, 2, 3, 4, 5, 6, 7]
    sigma = config.SIGMA
    n_fixed = 512

    results = []
    for b_sig in B_sigmas:
        B = b_sig * sigma
        p_coord = 2 * discrete_gaussian_cdf(-B, sigma)
        p_total = n_fixed * p_coord
        results.append({
            'B_sigma': b_sig,
            'P_coord': p_coord,
            'P_total': p_total,
            'Practical': "Yes" if p_total < 2**-40 else "No"
        })

    df1 = pd.DataFrame(results)
    df1.to_csv('../tables/TABLE_11_Failure_by_B.csv', index=False)

    dims = [128, 256, 512, 768, 1024]
    b_sigs = [4, 5]
    results_dim = []

    for n in dims:
        for b_sig in b_sigs:
            B = b_sig * sigma
            p_coord = 2 * discrete_gaussian_cdf(-B, sigma)
            p_total = n * p_coord
            results_dim.append({
                'Dimension': n,
                'B_sigma': b_sig,
                'P_total': p_total
            })

    df2 = pd.DataFrame(results_dim)
    df2.to_csv('../tables/TABLE_12_Failure_by_Dim.csv', index=False)

    palette = ["#1F4E79", "#2E86AB"]

    # Figure 15
    plt.figure(figsize=(10, 6))
    plt.plot(df1['B_sigma'], df1['P_total'], marker='o', color=palette[0])
    plt.yscale('log')
    plt.xlabel('Noise Bound B (in multiples of sigma)')
    plt.ylabel('Failure Probability P(fail)')
    plt.title('Figure 15: Failure Probability vs Noise Bound (n=512)')
    plt.axvline(4, color='red', linestyle='--', label='B=4σ')
    plt.axvline(5, color='orange', linestyle='--', label='B=5σ')
    plt.legend()
    plt.savefig('../figures/fig15_failure_prob_vs_bound.png', bbox_inches='tight', pad_inches=0.1)
    plt.savefig('../figures/fig15_failure_prob_vs_bound.pdf', bbox_inches='tight', pad_inches=0.1)
    plt.close()

    with open('../figures/fig15_failure_prob_vs_bound.txt', 'w') as f:
        f.write("Figure 15: Log-scale plot of decryption failure probability vs. noise bound B/σ for n=512, with annotations for practical thresholds.")

    # Heatmap
    # Generate wider range for heatmap
    b_sigs_heat = np.linspace(2, 6, 9)
    dims_heat = [128, 256, 512, 768, 1024]
    heat_data = np.zeros((len(dims_heat), len(b_sigs_heat)))

    for i, n in enumerate(dims_heat):
        for j, b_sig in enumerate(b_sigs_heat):
            B = b_sig * sigma
            heat_data[i, j] = np.log10(max(n * 2 * discrete_gaussian_cdf(-B, sigma), 1e-15))

    plt.figure(figsize=(10, 6))
    sns.heatmap(heat_data, xticklabels=np.round(b_sigs_heat, 1), yticklabels=dims_heat, cmap="rocket_r")
    plt.xlabel('B/sigma')
    plt.ylabel('Dimension n')
    plt.title('Figure 16: Log10 Failure Probability Heatmap')
    plt.savefig('../figures/fig16_failure_prob_heatmap.png', bbox_inches='tight', pad_inches=0.1)
    plt.savefig('../figures/fig16_failure_prob_heatmap.pdf', bbox_inches='tight', pad_inches=0.1)
    plt.close()

    with open('../figures/fig16_failure_prob_heatmap.txt', 'w') as f:
        f.write("Figure 16: Heatmap showing the base-10 logarithm of decryption failure probability across varying dimensions and noise bounds.")

    print("Exp07 completed.")
    return 2, 2

if __name__ == '__main__':
    run()
