import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import scipy.stats as stats
from core import hybrid_commitment
import config

plt.rcParams.update({'font.size': 11, 'axes.titlesize': 13, 'axes.labelsize': 11, 'xtick.labelsize': 10, 'ytick.labelsize': 10, 'figure.dpi': 300, 'savefig.dpi': 300})
sns.set_theme(style="whitegrid")

def run(n_trials=10000):
    print(f"Running Exp04: Latency Distribution Analysis ({n_trials} trials)")
    msg = b'D'*config.MSG_BYTES
    pp = hybrid_commitment.setup(config.N, config.Q, config.SIGMA, seed=config.SEED)

    latencies = []
    for _ in range(n_trials):
        _, _, t = hybrid_commitment.commit(pp, msg)
        latencies.append(t[0] / 1e6)

    data = np.array(latencies)

    # Fit distributions
    dists = {
        'Log-normal': stats.lognorm,
        'Weibull': stats.weibull_min,
        'Gamma': stats.gamma,
        'Normal': stats.norm
    }

    results = []
    best_dist = None
    best_ks = float('inf')
    best_params = None
    best_name = ""

    for name, dist in dists.items():
        # Fit
        params = dist.fit(data)
        # KS Test
        D, p = stats.kstest(data, dist.name, args=params)
        results.append({
            'Distribution': name,
            'Params': str(params),
            'KS_Stat': D,
            'p_value': p
        })

        if D < best_ks:
            best_ks = D
            best_dist = dist
            best_params = params
            best_name = name

    df_res = pd.DataFrame(results)
    df_res.to_csv('../tables/TABLE_08_Distribution_Fits.csv', index=False)

    palette = ["#1F4E79", "#2E86AB", "#A23B72", "#F18F01", "#C73E1D"]

    # Histogram
    plt.figure(figsize=(10, 6))
    sns.histplot(data, bins=50, stat='density', alpha=0.5, color=palette[0], label='Data')
    x = np.linspace(min(data), max(data), 100)
    for name, dist in dists.items():
        params = dist.fit(data)
        pdf = dist.pdf(x, *params)
        plt.plot(x, pdf, label=name)
    plt.xlabel('Latency (ms)')
    plt.ylabel('Density')
    plt.title('Figure 10: Latency Histogram with Fitted Distributions')
    plt.legend()
    plt.savefig('../figures/fig10_latency_histogram_fitted.png', bbox_inches='tight', pad_inches=0.1)
    plt.savefig('../figures/fig10_latency_histogram_fitted.pdf', bbox_inches='tight', pad_inches=0.1)
    plt.close()

    with open('../figures/fig10_latency_histogram_fitted.txt', 'w') as f:
        f.write("Figure 10: Histogram of latency distribution overlaid with fitted parametric distributions (Log-normal, Weibull, Gamma, Normal).")

    # QQ Plot
    plt.figure(figsize=(10, 6))
    stats.probplot(data, dist=best_dist, sparams=best_params, plot=plt)
    plt.title(f'Figure 11: Q-Q Plot ({best_name})')
    plt.savefig('../figures/fig11_qq_plot.png', bbox_inches='tight', pad_inches=0.1)
    plt.savefig('../figures/fig11_qq_plot.pdf', bbox_inches='tight', pad_inches=0.1)
    plt.close()

    with open('../figures/fig11_qq_plot.txt', 'w') as f:
        f.write(f"Figure 11: Quantile-Quantile (Q-Q) plot of latency data against the best-fit distribution ({best_name}).")

    print("Exp04 completed.")
    return 2, 1

if __name__ == '__main__':
    run()
