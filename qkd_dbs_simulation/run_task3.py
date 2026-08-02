import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path
import json
import yaml

from simulate import load_config
from data_ingest import ingest_data

def main():
    config = load_config()
    out_dir = Path("outputs")
    figures_dir = out_dir / "figures"
    tables_dir = out_dir / "tables"

    figures_dir.mkdir(parents=True, exist_ok=True)
    tables_dir.mkdir(parents=True, exist_ok=True)

    # Reload the simulation data to generate comprehensive reporting
    rtt_series = ingest_data()

    # We will run a fresh simulation if needed, or just recreate the dataframe
    from simulate import simulate
    df = simulate(rtt_series, config)

    # Set shared style
    plt.style.use('seaborn-v0_8-whitegrid')
    sns.set_context("paper", font_scale=1.2)

    # ==========================
    # FIGURES
    # ==========================

    # 1. latency_trend.png
    plt.figure(figsize=(10, 5))
    plot_len = min(len(df), 1000)
    plt.plot(df['block_id'][:plot_len], df['rtt_ms'][:plot_len], label='RTT (ms)', linewidth=1.5)
    plt.axhline(config["rtt_threshold_ms"], color='red', linestyle='--', label='DBS Threshold')
    plt.xlabel("Block Index")
    plt.ylabel("RTT (ms)")
    plt.title("Observed Network Latency Trend (Shared Style)")
    plt.legend()
    plt.tight_layout()
    plt.savefig(figures_dir / "latency_trend.png", dpi=300)
    plt.close()

    # 2. tradeoff_comparison.png
    policies = ['DBS', 'Fixed-Large', 'Fixed-Small']
    skr_means = [df['skr_dbs'].mean(), df['skr_large'].mean(), df['skr_small'].mean()]
    skr_stds = [df['skr_dbs'].std(), df['skr_large'].std(), df['skr_small'].std()]
    t2k_means = [df['t2k_dbs'].mean(), df['t2k_large'].mean(), df['t2k_small'].mean()]
    t2k_stds = [df['t2k_dbs'].std(), df['t2k_large'].std(), df['t2k_small'].std()]

    plt.figure(figsize=(8, 6))
    plt.errorbar(t2k_means, skr_means, xerr=t2k_stds, yerr=skr_stds, fmt='o', capsize=5, markersize=10,
                 color='purple', ecolor='gray')
    for i, p in enumerate(policies):
        plt.annotate(p, (t2k_means[i], skr_means[i]), xytext=(5, 5), textcoords='offset points')
    plt.xlabel("Mean Time-to-Key (proxy units)")
    plt.ylabel("Mean Secure Key Rate")
    plt.title("Trade-off: SKR vs Time-to-Key (Shared Style)")
    plt.grid(True, linestyle=':', alpha=0.7)
    plt.tight_layout()
    plt.savefig(figures_dir / "tradeoff_comparison.png", dpi=300)
    plt.close()

    # 3. skr_distribution_by_policy.png
    plt.figure(figsize=(8, 6))
    skr_melted = df[['skr_dbs', 'skr_large', 'skr_small']].rename(columns={
        'skr_dbs': 'DBS', 'skr_large': 'Fixed-Large', 'skr_small': 'Fixed-Small'
    }).melt(var_name='Policy', value_name='SKR')
    sns.violinplot(x='Policy', y='SKR', data=skr_melted, palette='Set2')
    plt.title("SKR Distribution by Policy")
    plt.ylabel("Secure Key Rate (bits/block)")
    plt.tight_layout()
    plt.savefig(figures_dir / "skr_distribution_by_policy.png", dpi=300)
    plt.close()

    # 4. key_availability_percent_by_policy.png
    avail_dbs = (df['skr_dbs'] > 0).mean() * 100
    avail_large = (df['skr_large'] > 0).mean() * 100
    avail_small = (df['skr_small'] > 0).mean() * 100
    df_avail = pd.DataFrame([
        {"Policy": "DBS", "Availability (%)": avail_dbs},
        {"Policy": "Fixed-Large", "Availability (%)": avail_large},
        {"Policy": "Fixed-Small", "Availability (%)": avail_small}
    ])

    plt.figure(figsize=(8, 5))
    sns.barplot(x='Policy', y='Availability (%)', data=df_avail, palette='Set2')
    plt.title("Key Availability Percent by Policy")
    plt.ylabel("Blocks with R(N) > 0 (%)")
    plt.ylim(0, 105)
    plt.tight_layout()
    plt.savefig(figures_dir / "key_availability_percent_by_policy.png", dpi=300)
    plt.close()

    # ==========================
    # TABLES
    # ==========================
    n = len(df)

    # 1. tradeoff_comparison.csv
    tradeoff_data = []
    for i, p in enumerate(policies):
        tradeoff_data.append({
            "Policy": p,
            "SKR_Mean": skr_means[i],
            "SKR_CI_95": 1.96 * skr_stds[i]/np.sqrt(n),
            "T2K_Mean": t2k_means[i],
            "T2K_CI_95": 1.96 * t2k_stds[i]/np.sqrt(n)
        })
    pd.DataFrame(tradeoff_data).to_csv(tables_dir / "tradeoff_comparison.csv", index=False)

    # 2. key_availability_summary.csv
    df_avail.to_csv(tables_dir / "key_availability_summary.csv", index=False)

    # 3. wilcoxon_test_results.csv
    from scipy.stats import wilcoxon
    stat_t2k_large, p_t2k_large = wilcoxon(df['t2k_dbs'], df['t2k_large'])
    stat_skr_large, p_skr_large = wilcoxon(df['skr_dbs'], df['skr_large'])
    w_max = n * (n + 1) / 2
    r_t2k_large = 1 - (2 * stat_t2k_large / w_max)
    r_skr_large = 1 - (2 * stat_skr_large / w_max)

    stat_t2k_small, p_t2k_small = wilcoxon(df['t2k_dbs'], df['t2k_small'])
    stat_skr_small, p_skr_small = wilcoxon(df['skr_dbs'], df['skr_small'])
    r_t2k_small = 1 - (2 * stat_t2k_small / w_max)
    r_skr_small = 1 - (2 * stat_skr_small / w_max)

    wilcoxon_data = [
        {"Comparison": "DBS vs Fixed-Large", "Metric": "SKR", "W": stat_skr_large, "p_value": p_skr_large, "effect_size_r": r_skr_large},
        {"Comparison": "DBS vs Fixed-Large", "Metric": "T2K", "W": stat_t2k_large, "p_value": p_t2k_large, "effect_size_r": r_t2k_large},
        {"Comparison": "DBS vs Fixed-Small", "Metric": "SKR", "W": stat_skr_small, "p_value": p_skr_small, "effect_size_r": r_skr_small},
        {"Comparison": "DBS vs Fixed-Small", "Metric": "T2K", "W": stat_t2k_small, "p_value": p_t2k_small, "effect_size_r": r_t2k_small}
    ]
    pd.DataFrame(wilcoxon_data).to_csv(tables_dir / "wilcoxon_test_results.csv", index=False)

    # 4. config_constants_used.csv
    config_rows = [
        {"constant": "rtt_threshold_ms", "value": config["rtt_threshold_ms"], "source_citation": "Configured threshold for latency regimes"},
        {"constant": "block_size_high_latency_bits", "value": config["block_size_high_latency_bits"], "source_citation": "Configured block size for high latency"},
        {"constant": "block_size_low_latency_bits", "value": config["block_size_low_latency_bits"], "source_citation": "Configured block size for low latency"},
        {"constant": "qber_range", "value": str(config["qber_range"]), "source_citation": "Synthetic generation uniform range"},
        {"constant": "error_correction_efficiency_f", "value": config["error_correction_efficiency_f"], "source_citation": "Brassard & Salvail (1994) or standard LDPC efficiency references (e.g., Elkouss et al. 2009)"},
        {"constant": "epsilon_security", "value": config["epsilon_security"], "source_citation": "ε used in finite-size correction term"},
        {"constant": "random_seed", "value": config["random_seed"], "source_citation": "Fixed random seed for reproducibility"},
        {"constant": "rtt_data_source", "value": config["rtt_data_source"], "source_citation": "Primary data source identifier"},
        {"constant": "n_simulation_runs", "value": config["n_simulation_runs"], "source_citation": "Simulation runs for reproducibility gate"},
        {"constant": "c1", "value": config["c1"], "source_citation": "Time-to-Key proxy metric illustrative constant"},
        {"constant": "c2", "value": config["c2"], "source_citation": "Time-to-Key proxy metric illustrative constant"}
    ]
    pd.DataFrame(config_rows).to_csv(tables_dir / "config_constants_used.csv", index=False)

if __name__ == "__main__":
    main()
