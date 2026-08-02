with open("README.md", "r") as f:
    content = f.read()

content += """
## Dynamic Post-Processing Block-Sizer (DBS) Simulation
The pipeline generates a set of reports and figures detailing the simulation results:

### Figures
- `outputs/figures/01_rtt_distribution.png`: Histogram of the RTT latency distribution.
- `outputs/figures/02_qber_distribution.png`: Histogram of synthetic QBER.
- `outputs/figures/03_correlation_heatmap.png`: Heatmap showing correlation between RTT, QBER, SKR, and T2K.
- `outputs/figures/04_skr_distribution_comparison.png`: KDE plot comparing SKR distributions across policies.
- `outputs/figures/05_t2k_distribution_comparison.png`: KDE plot comparing T2K distributions across policies.
- `outputs/figures/06_rtt_vs_skr_dbs_scatter.png`: Scatter plot showing SKR under DBS against RTT.
- `outputs/figures/07_qber_vs_skr_dbs_scatter.png`: Scatter plot showing SKR under DBS against QBER.
- `outputs/figures/08_skr_by_latency_regime_bar.png`: Bar plot comparing mean SKR across policies in high/low latency regimes.
- `outputs/figures/09_t2k_by_latency_regime_bar.png`: Bar plot comparing mean T2K across policies in high/low latency regimes.
- `outputs/figures/10_skr_temporal_trend_ma.png`: Moving average trend line of SKR over time.

### Tables
- `outputs/tables/01_descriptive_statistics.csv`: Summary statistics for numeric variables.
- `outputs/tables/02_data_quality_report.csv`: Data quality metrics including null counts and distinct values.
- `outputs/tables/03_correlation_matrix.csv`: Full correlation matrix for numeric columns.
- `outputs/tables/04_skr_policy_comparison.csv`: Summary statistics comparing SKR for DBS, Large, and Small policies.
- `outputs/tables/05_t2k_policy_comparison.csv`: Summary statistics comparing T2K for DBS, Large, and Small policies.
- `outputs/tables/06_metrics_by_latency_regime.csv`: Mean SKR and T2K grouped by high/low latency regimes.
- `outputs/tables/07_skr_by_qber_bins.csv`: Mean SKR across different binned ranges of QBER.
- `outputs/tables/08_top_10_blocks_skr_dbs.csv`: The top 10 best-performing blocks by SKR under DBS.
- `outputs/tables/09_worst_10_blocks_skr_dbs.csv`: The 10 worst-performing blocks by SKR under DBS.
- `outputs/tables/10_key_availability_summary.csv`: Percentage of blocks with SKR > 0 across policies.
"""
with open("README.md", "w") as f:
    f.write(content)
