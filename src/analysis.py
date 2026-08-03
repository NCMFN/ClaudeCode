import json
import pandas as pd
import numpy as np
from scipy.stats import wilcoxon

def load_results(path="outputs/results.json"):
    with open(path, "r") as f:
        return json.load(f)

def compute_wilcoxon(dbs_skr, baseline_skr):
    if len(dbs_skr) != len(baseline_skr):
        raise ValueError("Arrays must be the same length for paired test")

    diffs = dbs_skr - baseline_skr
    if np.all(diffs == 0):
        return 0.0, 1.0, 0.0

    stat, pval = wilcoxon(dbs_skr, baseline_skr, alternative='two-sided')

    diffs = diffs[diffs != 0]
    if len(diffs) == 0:
         return 0.0, 1.0, 0.0

    from scipy.stats import rankdata
    abs_diffs = np.abs(diffs)
    ranks = rankdata(abs_diffs)

    w_plus = np.sum(ranks[diffs > 0])
    w_minus = np.sum(ranks[diffs < 0])

    if w_plus + w_minus == 0:
        effect_size = 0.0
    else:
        effect_size = (w_plus - w_minus) / (w_plus + w_minus)

    return stat, pval, effect_size

def analyze_tradeoffs(results_data):
    dbs_df = pd.DataFrame(results_data["dbs"])
    large_df = pd.DataFrame(results_data["fixed_large"])
    small_df = pd.DataFrame(results_data["fixed_small"])

    tradeoffs = []

    for name, df in zip(["DBS", "Fixed-Large", "Fixed-Small"], [dbs_df, large_df, small_df]):
        mean_skr = df["skr"].mean()
        ci_skr = 1.96 * df["skr"].std() / np.sqrt(len(df))

        mean_t2k = df["t2k"].mean()
        ci_t2k = 1.96 * df["t2k"].std() / np.sqrt(len(df))

        tradeoffs.append({
            "Policy": name,
            "SKR_Mean": mean_skr,
            "SKR_CI_95": ci_skr,
            "T2K_Mean": mean_t2k,
            "T2K_CI_95": ci_t2k
        })

    return pd.DataFrame(tradeoffs)

def check_key_availability(results_data):
    availability = []

    for name, key in zip(["DBS", "Fixed-Large", "Fixed-Small"], ["dbs", "fixed_large", "fixed_small"]):
        df = pd.DataFrame(results_data[key])
        avail_percent = (df["skr"] > 0).mean() * 100
        availability.append({
            "Policy": name,
            "Availability_Percent": avail_percent
        })
    return pd.DataFrame(availability)

def generate_analysis():
    results_data = load_results()

    dbs_skr = np.array([x["skr"] for x in results_data["dbs"]])
    large_skr = np.array([x["skr"] for x in results_data["fixed_large"]])
    small_skr = np.array([x["skr"] for x in results_data["fixed_small"]])

    stat_large, pval_large, es_large = compute_wilcoxon(dbs_skr, large_skr)
    stat_small, pval_small, es_small = compute_wilcoxon(dbs_skr, small_skr)

    wilcoxon_results = pd.DataFrame([
        {"Baseline": "Fixed-Large", "W_Statistic": stat_large, "P_Value": pval_large, "Effect_Size": es_large},
        {"Baseline": "Fixed-Small", "W_Statistic": stat_small, "P_Value": pval_small, "Effect_Size": es_small}
    ])
    wilcoxon_results.to_csv("outputs/tables/wilcoxon_test_results.csv", index=False)

    tradeoffs_df = analyze_tradeoffs(results_data)
    tradeoffs_df.to_csv("outputs/tables/tradeoff_comparison.csv", index=False)

    avail_df = check_key_availability(results_data)
    avail_df.to_csv("outputs/tables/key_availability_summary.csv", index=False)

if __name__ == "__main__":
    generate_analysis()
