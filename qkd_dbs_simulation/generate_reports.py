import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path
import json

from simulate import load_config
from data_ingest import ingest_data
from dbs_policy import get_block_size_dbs, get_block_size_fixed_large, get_block_size_fixed_small
from qber_synth import generate_qber_series
from key_rate import compute_skr_per_block

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

    generated_files = []

    # ==========================
    # TABLES (at least 10)
    # ==========================

    # 1. Descriptive Statistics
    desc_stats = df.describe()
    desc_stats.to_csv(tables_dir / "01_descriptive_statistics.csv")
    generated_files.append(tables_dir / "01_descriptive_statistics.csv")

    # 2. Data Quality Report
    quality_report = pd.DataFrame({
        'nulls': df.isnull().sum(),
        'dtypes': df.dtypes,
        'unique_values': df.nunique()
    })
    quality_report.to_csv(tables_dir / "02_data_quality_report.csv")
    generated_files.append(tables_dir / "02_data_quality_report.csv")

    # 3. Correlation Matrix Table
    corr_matrix = df.corr()
    corr_matrix.to_csv(tables_dir / "03_correlation_matrix.csv")
    generated_files.append(tables_dir / "03_correlation_matrix.csv")

    # 4. SKR Policy Comparison Summary
    skr_summary = df[['skr_dbs', 'skr_large', 'skr_small']].agg(['mean', 'median', 'std', 'min', 'max']).T
    skr_summary.to_csv(tables_dir / "04_skr_policy_comparison.csv")
    generated_files.append(tables_dir / "04_skr_policy_comparison.csv")

    # 5. T2K Policy Comparison Summary
    t2k_summary = df[['t2k_dbs', 't2k_large', 't2k_small']].agg(['mean', 'median', 'std', 'min', 'max']).T
    t2k_summary.to_csv(tables_dir / "05_t2k_policy_comparison.csv")
    generated_files.append(tables_dir / "05_t2k_policy_comparison.csv")

    # 6. High Latency vs Low Latency Aggregations
    df['latency_regime'] = np.where(df['rtt_ms'] > config['rtt_threshold_ms'], 'High', 'Low')
    regime_agg = df.groupby('latency_regime')[['skr_dbs', 'skr_large', 'skr_small', 't2k_dbs', 't2k_large', 't2k_small']].mean()
    regime_agg.to_csv(tables_dir / "06_metrics_by_latency_regime.csv")
    generated_files.append(tables_dir / "06_metrics_by_latency_regime.csv")

    # 7. QBER Bins Aggregation
    df['qber_bin'] = pd.cut(df['qber'], bins=5)
    qber_agg = df.groupby('qber_bin')[['skr_dbs', 'skr_large', 'skr_small']].mean()
    qber_agg.to_csv(tables_dir / "07_skr_by_qber_bins.csv")
    generated_files.append(tables_dir / "07_skr_by_qber_bins.csv")

    # 8. Top 10 Best SKR performing blocks under DBS
    top_10_skr = df.nlargest(10, 'skr_dbs')
    top_10_skr.to_csv(tables_dir / "08_top_10_blocks_skr_dbs.csv", index=False)
    generated_files.append(tables_dir / "08_top_10_blocks_skr_dbs.csv")

    # 9. Top 10 Worst SKR performing blocks under DBS
    worst_10_skr = df.nsmallest(10, 'skr_dbs')
    worst_10_skr.to_csv(tables_dir / "09_worst_10_blocks_skr_dbs.csv", index=False)
    generated_files.append(tables_dir / "09_worst_10_blocks_skr_dbs.csv")

    # 10. Key Availability Summary Table
    avail_dbs = (df['skr_dbs'] > 0).mean() * 100
    avail_large = (df['skr_large'] > 0).mean() * 100
    avail_small = (df['skr_small'] > 0).mean() * 100
    df_avail = pd.DataFrame([
        {"Policy": "DBS", "Availability (%)": avail_dbs},
        {"Policy": "Fixed-Large", "Availability (%)": avail_large},
        {"Policy": "Fixed-Small", "Availability (%)": avail_small}
    ])
    df_avail.to_csv(tables_dir / "10_key_availability_summary.csv", index=False)
    generated_files.append(tables_dir / "10_key_availability_summary.csv")

    # ==========================
    # FIGURES (at least 10)
    # ==========================

    # 1. RTT Distribution
    plt.figure(figsize=(8, 5))
    sns.histplot(df['rtt_ms'], bins=50, kde=True)
    plt.title("Distribution of Network Latency (RTT)")
    plt.xlabel("RTT (ms)")
    plt.ylabel("Frequency")
    plt.axvline(config['rtt_threshold_ms'], color='r', linestyle='--', label='DBS Threshold')
    plt.legend()
    plt.tight_layout()
    plt.savefig(figures_dir / "01_rtt_distribution.png", dpi=300)
    plt.close()
    generated_files.append(figures_dir / "01_rtt_distribution.png")

    # 2. QBER Distribution
    plt.figure(figsize=(8, 5))
    sns.histplot(df['qber'], bins=50, kde=True, color='purple')
    plt.title("Distribution of Synthetic QBER")
    plt.xlabel("Quantum Bit Error Rate (QBER)")
    plt.ylabel("Frequency")
    plt.tight_layout()
    plt.savefig(figures_dir / "02_qber_distribution.png", dpi=300)
    plt.close()
    generated_files.append(figures_dir / "02_qber_distribution.png")

    # 3. Correlation Heatmap
    plt.figure(figsize=(10, 8))
    sns.heatmap(corr_matrix, annot=False, cmap='coolwarm', center=0)
    plt.title("Correlation Heatmap of Pipeline Variables")
    plt.tight_layout()
    plt.savefig(figures_dir / "03_correlation_heatmap.png", dpi=300)
    plt.close()
    generated_files.append(figures_dir / "03_correlation_heatmap.png")

    # 4. SKR Distribution Comparison
    plt.figure(figsize=(8, 5))
    sns.kdeplot(df['skr_dbs'], label='DBS', fill=True, alpha=0.3)
    sns.kdeplot(df['skr_large'], label='Fixed Large', fill=True, alpha=0.3)
    sns.kdeplot(df['skr_small'], label='Fixed Small', fill=True, alpha=0.3)
    plt.title("Distribution of Secure Key Rates (SKR)")
    plt.xlabel("SKR (bits/block)")
    plt.ylabel("Density")
    plt.legend()
    plt.tight_layout()
    plt.savefig(figures_dir / "04_skr_distribution_comparison.png", dpi=300)
    plt.close()
    generated_files.append(figures_dir / "04_skr_distribution_comparison.png")

    # 5. T2K Distribution Comparison
    plt.figure(figsize=(8, 5))
    sns.kdeplot(df['t2k_dbs'], label='DBS', fill=True, alpha=0.3)
    sns.kdeplot(df['t2k_large'], label='Fixed Large', fill=True, alpha=0.3)
    sns.kdeplot(df['t2k_small'], label='Fixed Small', fill=True, alpha=0.3)
    plt.title("Distribution of Time-to-Key (T2K)")
    plt.xlabel("Time-to-Key (proxy units)")
    plt.ylabel("Density")
    plt.legend()
    plt.tight_layout()
    plt.savefig(figures_dir / "05_t2k_distribution_comparison.png", dpi=300)
    plt.close()
    generated_files.append(figures_dir / "05_t2k_distribution_comparison.png")

    # 6. RTT vs SKR DBS Scatter
    plt.figure(figsize=(8, 5))
    plt.scatter(df['rtt_ms'], df['skr_dbs'], alpha=0.1, color='blue', s=2)
    plt.title("RTT vs SKR under DBS Policy")
    plt.xlabel("RTT (ms)")
    plt.ylabel("SKR (bits/block)")
    plt.axvline(config['rtt_threshold_ms'], color='r', linestyle='--', label='Threshold')
    plt.legend()
    plt.tight_layout()
    plt.savefig(figures_dir / "06_rtt_vs_skr_dbs_scatter.png", dpi=300)
    plt.close()
    generated_files.append(figures_dir / "06_rtt_vs_skr_dbs_scatter.png")

    # 7. QBER vs SKR DBS Scatter
    plt.figure(figsize=(8, 5))
    plt.scatter(df['qber'], df['skr_dbs'], alpha=0.1, color='green', s=2)
    plt.title("QBER vs SKR under DBS Policy")
    plt.xlabel("QBER")
    plt.ylabel("SKR (bits/block)")
    plt.tight_layout()
    plt.savefig(figures_dir / "07_qber_vs_skr_dbs_scatter.png", dpi=300)
    plt.close()
    generated_files.append(figures_dir / "07_qber_vs_skr_dbs_scatter.png")

    # 8. SKR by Latency Regime Barplot
    plt.figure(figsize=(8, 5))
    skr_means = regime_agg[['skr_dbs', 'skr_large', 'skr_small']].reset_index()
    skr_melted = skr_means.melt(id_vars='latency_regime', var_name='Policy', value_name='Mean_SKR')
    sns.barplot(data=skr_melted, x='latency_regime', y='Mean_SKR', hue='Policy')
    plt.title("Mean SKR by Latency Regime")
    plt.xlabel("Latency Regime")
    plt.ylabel("Mean SKR (bits/block)")
    plt.tight_layout()
    plt.savefig(figures_dir / "08_skr_by_latency_regime_bar.png", dpi=300)
    plt.close()
    generated_files.append(figures_dir / "08_skr_by_latency_regime_bar.png")

    # 9. T2K by Latency Regime Barplot
    plt.figure(figsize=(8, 5))
    t2k_means = regime_agg[['t2k_dbs', 't2k_large', 't2k_small']].reset_index()
    t2k_melted = t2k_means.melt(id_vars='latency_regime', var_name='Policy', value_name='Mean_T2K')
    sns.barplot(data=t2k_melted, x='latency_regime', y='Mean_T2K', hue='Policy')
    plt.title("Mean T2K by Latency Regime")
    plt.xlabel("Latency Regime")
    plt.ylabel("Mean T2K (proxy units)")
    plt.tight_layout()
    plt.savefig(figures_dir / "09_t2k_by_latency_regime_bar.png", dpi=300)
    plt.close()
    generated_files.append(figures_dir / "09_t2k_by_latency_regime_bar.png")

    # 10. Temporal Trend of SKR (Moving Average)
    plt.figure(figsize=(10, 5))
    plot_df = df.iloc[:2000].copy() # Plotting first 2000 blocks to avoid overcrowding
    plot_df['skr_dbs_ma'] = plot_df['skr_dbs'].rolling(50).mean()
    plot_df['skr_large_ma'] = plot_df['skr_large'].rolling(50).mean()
    plot_df['skr_small_ma'] = plot_df['skr_small'].rolling(50).mean()

    plt.plot(plot_df['block_id'], plot_df['skr_dbs_ma'], label='DBS (50-block MA)')
    plt.plot(plot_df['block_id'], plot_df['skr_large_ma'], label='Fixed Large (MA)', alpha=0.7)
    plt.plot(plot_df['block_id'], plot_df['skr_small_ma'], label='Fixed Small (MA)', alpha=0.7)

    plt.title("Moving Average of SKR over Time (First 2000 Blocks)")
    plt.xlabel("Block ID")
    plt.ylabel("SKR (bits/block)")
    plt.legend()
    plt.tight_layout()
    plt.savefig(figures_dir / "10_skr_temporal_trend_ma.png", dpi=300)
    plt.close()
    generated_files.append(figures_dir / "10_skr_temporal_trend_ma.png")

    print("\nGenerated Reporting Files:")
    for f in generated_files:
        print(f" - {f}")

    print("\nSuccessfully generated 10 figures and 10 tables in outputs/figures/ and outputs/tables/")

if __name__ == "__main__":
    main()
