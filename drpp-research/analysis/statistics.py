import sys
import os
import pandas as pd
import numpy as np
from scipy.stats import norm, chi2_contingency

# Add parent dir to path to import config
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import config

def wilson_score_interval(p: float, n: int, z: float = 1.96) -> tuple:
    """
    Computes the Wilson score interval for a proportion.

    Args:
        p (float): Proportion of successes.
        n (int): Number of trials.
        z (float): z-score for the confidence level (default 1.96 for 95% CI).

    Returns:
        tuple: (lower_bound, upper_bound)
    """
    if pd.isna(p) or n == 0:
        return (None, None)

    denominator = 1 + z**2 / n
    center = p + z**2 / (2 * n)
    spread = z * np.sqrt(p * (1 - p) / n + z**2 / (4 * n**2))

    lower = (center - spread) / denominator
    upper = (center + spread) / denominator

    return (lower, upper)

def run_analysis():
    """
    Analyzes raw simulation results.
    """
    results_path = os.path.join(config.OUTPUT_DIR, "results", "raw_results.csv")
    if not os.path.exists(results_path):
        print(f"Error: Could not find {results_path}")
        return

    df = pd.read_csv(results_path)
    analysis_data = []

    total_k_values = len(config.K_VALUES)
    valid_k_values = 0

    for k in config.K_VALUES:
        for model in ["DRPP", "Traditional", "Collusion"]:
            subset = df[(df["k"] == k) & (df["model"] == model)]
            if subset.empty:
                continue

            p = subset["success_rate"].values[0]
            n = subset["n_trials"].values[0]

            ci_lower, ci_upper = wilson_score_interval(p, n)

            theo_bound = None
            within_bound = None

            if model == "DRPP":
                theo_bound = 2.0 ** -k
                # Check if p matches theo_bound within tolerance (e.g. 2%)
                tolerance = 0.02
                within_bound = abs(p - theo_bound) <= tolerance
                if within_bound:
                    valid_k_values += 1

            analysis_data.append({
                "k": k,
                "model": model,
                "mean_prob": p,
                "ci_lower": ci_lower,
                "ci_upper": ci_upper,
                "theoretical_bound": theo_bound,
                "within_bound": within_bound
            })

        # Chi-squared test comparing DRPP vs Traditional
        drpp_subset = df[(df["k"] == k) & (df["model"] == "DRPP")]
        trad_subset = df[(df["k"] == k) & (df["model"] == "Traditional")]

        if not drpp_subset.empty and not trad_subset.empty:
            p_drpp = drpp_subset["success_rate"].values[0]
            p_trad = trad_subset["success_rate"].values[0]
            n_trials = drpp_subset["n_trials"].values[0]

            obs_drpp = [int(p_drpp * n_trials), n_trials - int(p_drpp * n_trials)]
            obs_trad = [int(p_trad * n_trials), n_trials - int(p_trad * n_trials)]

            # Contingency table
            table = [obs_drpp, obs_trad]
            chi2, p_val, dof, expected = chi2_contingency(table)
            # We don't store chi-squared in the main table per task, but it is computed

    df_analysis = pd.DataFrame(analysis_data)

    out_path = os.path.join(config.OUTPUT_DIR, "results", "analysis_report.csv")
    df_analysis.to_csv(out_path, index=False)

    print(f"Analysis saved to {out_path}")
    print(f"Simulation confirmed theorem for {valid_k_values} out of {total_k_values} k-values ({valid_k_values/total_k_values*100:.1f}%)")

if __name__ == "__main__":
    run_analysis()
