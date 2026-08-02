import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from scipy.stats import wilcoxon, norm
from pathlib import Path
import json

def analyze_and_export(df_results, config):
    out_dir = Path("outputs")
    out_dir.mkdir(exist_ok=True)

    plt.figure(figsize=(10, 5))
    plot_len = min(len(df_results), 1000)
    plt.plot(df_results['block_id'][:plot_len], df_results['rtt_ms'][:plot_len], label='RTT (ms)')
    plt.axhline(config["rtt_threshold_ms"], color='r', linestyle='--', label='DBS Threshold')
    plt.xlabel("Block Index")
    plt.ylabel("RTT (ms)")
    plt.title("Observed Network Latency Trend")
    plt.legend()
    plt.tight_layout()
    plt.savefig(out_dir / "latency_trend.png", dpi=300)
    plt.close()

    avail_dbs = (df_results['skr_dbs'] > 0).mean() * 100
    avail_large = (df_results['skr_large'] > 0).mean() * 100
    avail_small = (df_results['skr_small'] > 0).mean() * 100

    df_avail = pd.DataFrame([
        {"Policy": "DBS", "Availability (%)": avail_dbs},
        {"Policy": "Fixed-Large", "Availability (%)": avail_large},
        {"Policy": "Fixed-Small", "Availability (%)": avail_small}
    ])
    df_avail.to_csv(out_dir / "key_availability_summary.csv", index=False)

    policies = ['DBS', 'Fixed-Large', 'Fixed-Small']
    skr_means = [df_results['skr_dbs'].mean(), df_results['skr_large'].mean(), df_results['skr_small'].mean()]
    skr_stds = [df_results['skr_dbs'].std(), df_results['skr_large'].std(), df_results['skr_small'].std()]
    t2k_means = [df_results['t2k_dbs'].mean(), df_results['t2k_large'].mean(), df_results['t2k_small'].mean()]
    t2k_stds = [df_results['t2k_dbs'].std(), df_results['t2k_large'].std(), df_results['t2k_small'].std()]

    plt.figure(figsize=(8, 6))
    plt.errorbar(t2k_means, skr_means, xerr=t2k_stds, yerr=skr_stds, fmt='o', capsize=5, markersize=10)
    for i, p in enumerate(policies):
        plt.annotate(p, (t2k_means[i], skr_means[i]), xytext=(5, 5), textcoords='offset points')
    plt.xlabel("Mean Time-to-Key (proxy units)")
    plt.ylabel("Mean Secure Key Rate")
    plt.title("Trade-off: SKR vs Time-to-Key")
    plt.grid(True)
    plt.tight_layout()
    plt.savefig(out_dir / "tradeoff_comparison.png", dpi=300)
    plt.close()

    stat_t2k_large, p_t2k_large = wilcoxon(df_results['t2k_dbs'], df_results['t2k_large'])
    stat_skr_large, p_skr_large = wilcoxon(df_results['skr_dbs'], df_results['skr_large'])
    n = len(df_results)
    w_max = n * (n + 1) / 2
    r_t2k_large = 1 - (2 * stat_t2k_large / w_max)
    r_skr_large = 1 - (2 * stat_skr_large / w_max)

    stat_t2k_small, p_t2k_small = wilcoxon(df_results['t2k_dbs'], df_results['t2k_small'])
    stat_skr_small, p_skr_small = wilcoxon(df_results['skr_dbs'], df_results['skr_small'])
    r_t2k_small = 1 - (2 * stat_t2k_small / w_max)
    r_skr_small = 1 - (2 * stat_skr_small / w_max)

    stats_results = {
        "DBS_vs_Large": {
            "T2K": {"W": stat_t2k_large, "p_value": p_t2k_large, "effect_size_r": r_t2k_large},
            "SKR": {"W": stat_skr_large, "p_value": p_skr_large, "effect_size_r": r_skr_large},
        },
        "DBS_vs_Small": {
            "T2K": {"W": stat_t2k_small, "p_value": p_t2k_small, "effect_size_r": r_t2k_small},
            "SKR": {"W": stat_skr_small, "p_value": p_skr_small, "effect_size_r": r_skr_small},
        }
    }

    results_json = {
        "SKR_Means": {"DBS": skr_means[0], "Fixed_Large": skr_means[1], "Fixed_Small": skr_means[2]},
        "T2K_Means": {"DBS": t2k_means[0], "Fixed_Large": t2k_means[1], "Fixed_Small": t2k_means[2]},
        "SKR_CIs_95": {
            "DBS": 1.96 * skr_stds[0]/np.sqrt(n),
            "Fixed_Large": 1.96 * skr_stds[1]/np.sqrt(n),
            "Fixed_Small": 1.96 * skr_stds[2]/np.sqrt(n)
        },
        "T2K_CIs_95": {
            "DBS": 1.96 * t2k_stds[0]/np.sqrt(n),
            "Fixed_Large": 1.96 * t2k_stds[1]/np.sqrt(n),
            "Fixed_Small": 1.96 * t2k_stds[2]/np.sqrt(n)
        },
        "Statistics": stats_results
    }

    with open(out_dir / "results.json", "w") as f:
        json.dump(results_json, f, indent=4)

    return results_json
