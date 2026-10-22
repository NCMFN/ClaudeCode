import pandas as pd
import numpy as np
from scipy import stats
import logging
import os
from datetime import datetime

# Setup
os.makedirs("results/logs", exist_ok=True)
os.makedirs("results/tables", exist_ok=True)
logging.basicConfig(
    filename="results/logs/stats.log",
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)
np.random.seed(42)

def cohen_d(x, y):
    nx = len(x)
    ny = len(y)
    dof = nx + ny - 2
    return (np.mean(x) - np.mean(y)) / np.sqrt(((nx-1)*np.std(x, ddof=1) ** 2 + (ny-1)*np.std(y, ddof=1) ** 2) / dof)

def run_analysis():
    start_time = datetime.now()
    logging.info("Starting statistical analysis")
    print("Running statistical analysis...")

    # Load simulation histories
    baseline_hist = pd.read_csv("results/tables/history_Baseline.csv")
    fsm_default_hist = pd.read_csv("results/tables/history_FSM_Default.csv")
    fsm_agg_hist = pd.read_csv("results/tables/history_FSM_Aggressive.csv")
    fsm_cons_hist = pd.read_csv("results/tables/history_FSM_Conservative.csv")

    # Get SOC distribution for analysis
    soc_baseline = baseline_hist['soc'].values
    soc_fsm = fsm_default_hist['soc'].values
    soc_agg = fsm_agg_hist['soc'].values
    soc_cons = fsm_cons_hist['soc'].values

    # Since lengths might be different due to node death, pad with 0s for comparison up to max length
    max_len = max(len(soc_baseline), len(soc_fsm), len(soc_agg), len(soc_cons))

    soc_baseline_padded = np.pad(soc_baseline, (0, max_len - len(soc_baseline)), 'constant')
    soc_fsm_padded = np.pad(soc_fsm, (0, max_len - len(soc_fsm)), 'constant')
    soc_agg_padded = np.pad(soc_agg, (0, max_len - len(soc_agg)), 'constant')
    soc_cons_padded = np.pad(soc_cons, (0, max_len - len(soc_cons)), 'constant')

    results = {}

    # 1. Shapiro-Wilk Test for Normality
    # Use a sample of 500 points to avoid max N warning and improve test validity
    sample_idx = np.random.choice(max_len, min(500, max_len), replace=False)
    stat_sw_b, p_sw_b = stats.shapiro(soc_baseline_padded[sample_idx])
    stat_sw_f, p_sw_f = stats.shapiro(soc_fsm_padded[sample_idx])

    results['Shapiro-Wilk Baseline (p)'] = p_sw_b
    results['Shapiro-Wilk FSM (p)'] = p_sw_f

    # 2. Paired t-test
    stat_tt, p_tt = stats.ttest_rel(soc_baseline_padded, soc_fsm_padded)
    results['Paired t-test (p)'] = p_tt

    # 3. Wilcoxon signed-rank test
    stat_w, p_w = stats.wilcoxon(soc_baseline_padded, soc_fsm_padded)
    results['Wilcoxon (p)'] = p_w

    # 4. Cohen's d
    results["Cohen's d"] = cohen_d(soc_fsm_padded, soc_baseline_padded)

    # 5. ANOVA
    stat_anova, p_anova = stats.f_oneway(soc_baseline_padded, soc_fsm_padded, soc_agg_padded, soc_cons_padded)
    results['ANOVA (p)'] = p_anova

    # 6. Check Success Criteria
    sim_summary = pd.read_csv("results/tables/simulation_summary.csv")

    baseline_life = sim_summary[sim_summary['Scenario'] == 'Baseline']['Battery_Lifetime_hrs'].values[0]
    fsm_life = sim_summary[sim_summary['Scenario'] == 'FSM_Default']['Battery_Lifetime_hrs'].values[0]
    fsm_proofs = sim_summary[sim_summary['Scenario'] == 'FSM_Default']['Proof_Success'].values[0]
    baseline_proofs = sim_summary[sim_summary['Scenario'] == 'Baseline']['Proof_Success'].values[0]

    battery_gain = (fsm_life - baseline_life) / baseline_life * 100
    proof_retention = (fsm_proofs / baseline_proofs) * 100 if baseline_proofs > 0 else 0

    results['Battery Improvement (%)'] = battery_gain
    results['Proof Retention (%)'] = proof_retention
    results['Overall p < 0.05'] = bool(p_w < 0.05 and p_anova < 0.05)

    # Assertions
    assert battery_gain >= 25, "Failed Success Criteria: Battery Improvement < 25%"

    df_results = pd.DataFrame([results])
    df_results.to_csv("results/tables/statistical_analysis.csv", index=False)

    end_time = datetime.now()
    logging.info(f"Analysis completed in {end_time - start_time}. Saved to results/tables/statistical_analysis.csv")
    print("Statistical analysis complete.")

if __name__ == "__main__":
    try:
        run_analysis()
    except Exception as e:
        logging.error(f"Analysis failed: {str(e)}")
        with open("results/logs/error.log", "w") as f:
            f.write(f"Stats Error: {str(e)}\nSuggestion: Check simulation outputs.\n")
        raise
