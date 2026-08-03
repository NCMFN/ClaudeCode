import json
import os
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from reporting import plot_style

def load_data():
    with open("outputs/results.json", "r") as f:
        results = json.load(f)
    with open("src/config.json", "r") as f:
        config = json.load(f)
    rtt_series = pd.read_csv("data/rtt_time_series.csv")
    return results, config, rtt_series

def generate_tables(results, config):
    print("Generating tables...")
    os.makedirs("outputs/tables", exist_ok=True)

    config_df = pd.DataFrame(list(config.items()), columns=["Parameter", "Value"])
    config_df["Source_Citation"] = "Illustrative Config"
    config_df.loc[config_df["Parameter"] == "error_correction_efficiency_f", "Source_Citation"] = "Standard BB84 cascade assumption"
    config_df.to_csv("outputs/tables/config_constants_used.csv", index=False)

    dbs_df = pd.DataFrame(results["dbs"])
    qber_stats = dbs_df["qber"].describe().reset_index()
    qber_stats.to_csv("outputs/tables/qber_summary_stats.csv", index=False)

    bs_summary = dbs_df["block_size"].value_counts(normalize=True).reset_index()
    bs_summary.columns = ["Block_Size", "Percentage"]
    bs_summary["Percentage"] = bs_summary["Percentage"] * 100
    bs_summary.to_csv("outputs/tables/block_size_selection_summary.csv", index=False)

    failures = []
    for policy, key in zip(["DBS", "Fixed-Large", "Fixed-Small"], ["dbs", "fixed_large", "fixed_small"]):
        df = pd.DataFrame(results[key])
        failures.append({
            "Policy": policy,
            "Failures": df["failure"].sum(),
            "Failure_Rate_Percent": df["failure"].mean() * 100
        })
    pd.DataFrame(failures).to_csv("outputs/tables/key_generation_failure_summary.csv", index=False)

    percentiles = []
    for policy, key in zip(["DBS", "Fixed-Large", "Fixed-Small"], ["dbs", "fixed_large", "fixed_small"]):
        df = pd.DataFrame(results[key])
        p = np.percentile(df["skr"], [5, 25, 50, 75, 95])
        percentiles.append({
            "Policy": policy,
            "p5": p[0], "p25": p[1], "Median": p[2], "p75": p[3], "p95": p[4]
        })
    pd.DataFrame(percentiles).to_csv("outputs/tables/skr_percentiles_by_policy.csv", index=False)

    t2k_percentiles = []
    for policy, key in zip(["DBS", "Fixed-Large", "Fixed-Small"], ["dbs", "fixed_large", "fixed_small"]):
        df = pd.DataFrame(results[key])
        p = np.percentile(df["t2k"], [5, 25, 50, 75, 95])
        t2k_percentiles.append({
            "Policy": policy,
            "p5": p[0], "p25": p[1], "Median": p[2], "p75": p[3], "p95": p[4]
        })
    pd.DataFrame(t2k_percentiles).to_csv("outputs/tables/t2k_percentiles_by_policy.csv", index=False)

def generate_figures(results, rtt_series):
    print("Generating figures...")
    os.makedirs("outputs/figures", exist_ok=True)
    plot_style.apply()

    dbs_df = pd.DataFrame(results["dbs"])
    large_df = pd.DataFrame(results["fixed_large"])
    small_df = pd.DataFrame(results["fixed_small"])

    dbs_df["Policy"] = "DBS"
    large_df["Policy"] = "Fixed-Large"
    small_df["Policy"] = "Fixed-Small"
    combined_df = pd.concat([dbs_df, large_df, small_df])

    plt.figure()
    plt.plot(pd.to_datetime(rtt_series['timestamp']), rtt_series['rtt_ms'], color=plot_style.COLORS["primary"], alpha=0.7)
    plt.title("RTT Trace Over Time")
    plt.xlabel("Time")
    plt.ylabel("RTT (ms)")
    plt.xticks(rotation=45)
    plt.savefig("outputs/figures/latency_trend.png")
    plt.close()

    tradeoff_df = pd.read_csv("outputs/tables/tradeoff_comparison.csv")
    plt.figure()
    sns.scatterplot(data=tradeoff_df, x="T2K_Mean", y="SKR_Mean", hue="Policy", s=100)
    plt.title("SKR vs T2K Trade-off")
    plt.xlabel("Mean T2K")
    plt.ylabel("Mean SKR")
    plt.savefig("outputs/figures/tradeoff_comparison.png")
    plt.close()

    plt.figure()
    sns.violinplot(data=combined_df, x="Policy", y="skr")
    plt.title("SKR Distribution by Policy")
    plt.savefig("outputs/figures/skr_distribution_by_policy.png")
    plt.close()

    avail_df = pd.read_csv("outputs/tables/key_availability_summary.csv")
    plt.figure()
    sns.barplot(data=avail_df, x="Policy", y="Availability_Percent")
    plt.title("Key Availability (%) by Policy")
    plt.ylim(0, 105)
    plt.savefig("outputs/figures/key_availability_percent_by_policy.png")
    plt.close()

    plt.figure()
    sns.boxplot(data=combined_df, x="Policy", y="t2k")
    plt.title("T2K Distribution by Policy")
    plt.savefig("outputs/figures/t2k_distribution_by_policy.png")
    plt.close()

    plt.figure()
    subset = dbs_df.head(200)
    plt.step(subset.index, subset["block_size"], where="post", color=plot_style.COLORS["secondary"])
    plt.title("DBS Block Size Selection (Subset)")
    plt.xlabel("Block Index")
    plt.ylabel("Block Size (bits)")
    plt.savefig("outputs/figures/block_size_selection_over_time.png")
    plt.close()

    plt.figure()
    sns.histplot(dbs_df["qber"], bins=20, color=plot_style.COLORS["tertiary"])
    plt.title("Distribution of Synthetic QBER")
    plt.xlabel("QBER")
    plt.savefig("outputs/figures/qber_distribution.png")
    plt.close()

    fail_df = pd.read_csv("outputs/tables/key_generation_failure_summary.csv")
    plt.figure()
    sns.barplot(data=fail_df, x="Policy", y="Failure_Rate_Percent")
    plt.title("Key Generation Failure Rate (%)")
    plt.savefig("outputs/figures/key_generation_failure_rate_by_policy.png")
    plt.close()

    wilcox_df = pd.read_csv("outputs/tables/wilcoxon_test_results.csv")
    plt.figure()
    sns.barplot(data=wilcox_df, x="Baseline", y="Effect_Size")
    plt.title("Effect Size: DBS vs Baseline")
    plt.ylabel("Rank-Biserial Correlation")
    plt.savefig("outputs/figures/wilcoxon_effect_size_comparison.png")
    plt.close()

    plt.figure()
    sns.scatterplot(data=combined_df.sample(min(3000, len(combined_df))), x="rtt_ms", y="skr", hue="Policy", alpha=0.5)
    plt.title("SKR vs RTT Scatter")
    plt.xlabel("RTT (ms)")
    plt.ylabel("SKR")
    plt.savefig("outputs/figures/skr_vs_rtt_scatter.png")
    plt.close()

def write_manifests():
    source_manifest = {
        "figures": [
            {"file": "latency_trend.png", "source": "data/rtt_time_series.csv"},
            {"file": "tradeoff_comparison.png", "source": "outputs/tables/tradeoff_comparison.csv"},
            {"file": "skr_distribution_by_policy.png", "source": "outputs/results.json (all policies)"},
            {"file": "key_availability_percent_by_policy.png", "source": "outputs/tables/key_availability_summary.csv"},
            {"file": "t2k_distribution_by_policy.png", "source": "outputs/results.json (all policies)"},
            {"file": "block_size_selection_over_time.png", "source": "outputs/results.json (dbs)"},
            {"file": "qber_distribution.png", "source": "outputs/results.json (dbs.qber)"},
            {"file": "key_generation_failure_rate_by_policy.png", "source": "outputs/tables/key_generation_failure_summary.csv"},
            {"file": "wilcoxon_effect_size_comparison.png", "source": "outputs/tables/wilcoxon_test_results.csv"},
            {"file": "skr_vs_rtt_scatter.png", "source": "outputs/results.json (all policies)"}
        ],
        "tables": [
            {"file": "tradeoff_comparison.csv", "source": "outputs/results.json (analysis.py)"},
            {"file": "key_availability_summary.csv", "source": "outputs/results.json (analysis.py)"},
            {"file": "wilcoxon_test_results.csv", "source": "outputs/results.json (analysis.py)"},
            {"file": "config_constants_used.csv", "source": "src/config.json"},
            {"file": "rtt_source_manifest.csv", "source": "data_ingest.py"},
            {"file": "qber_summary_stats.csv", "source": "outputs/results.json (dbs.qber)"},
            {"file": "block_size_selection_summary.csv", "source": "outputs/results.json (dbs.block_size)"},
            {"file": "key_generation_failure_summary.csv", "source": "outputs/results.json (failure field)"},
            {"file": "skr_percentiles_by_policy.csv", "source": "outputs/results.json (skr field)"},
            {"file": "t2k_percentiles_by_policy.csv", "source": "outputs/results.json (t2k field)"}
        ]
    }
    with open("outputs/source_manifest.json", "w") as f:
        json.dump(source_manifest, f, indent=4)

    paper_assets = []
    for f in source_manifest["figures"]:
        paper_assets.append({"asset_type": "figure", "filename": f["file"], "source": f["source"]})
    for t in source_manifest["tables"]:
        paper_assets.append({"asset_type": "table", "filename": t["file"], "source": t["source"]})
    pd.DataFrame(paper_assets).to_csv("outputs/paper_assets_manifest.csv", index=False)

def write_report():
    with open("outputs/report.md", "w") as f:
        f.write("# Dynamic Post-Processing Block-Sizer (DBS) for Time-Constrained QKD\n\n")
        f.write("## Methodology\n")
        f.write("This simulation evaluates a Dynamic Block-Sizer (DBS) policy against fixed block-size baselines (Fixed-Large and Fixed-Small). ")
        f.write("The SKR model implements a finite-size-corrected pedagogical approximation from Tomamichel et al. (2012).\n\n")
        f.write("## Config Constants\n")
        f.write("Constants are listed in `outputs/tables/config_constants_used.csv`.\n\n")
        f.write("## Results Summary\n")
        f.write("For numerical tradeoffs and statistical significance, please refer to `outputs/tables/tradeoff_comparison.csv` and `outputs/tables/wilcoxon_test_results.csv`.\n")
        f.write("Generated figures and tables are located in `outputs/figures/` and `outputs/tables/`.\n")

if __name__ == "__main__":
    results, config, rtt_series = load_data()
    generate_tables(results, config)
    generate_figures(results, rtt_series)
    write_manifests()
    write_report()
    print("Generated 10 figures and 10 tables successfully.")
