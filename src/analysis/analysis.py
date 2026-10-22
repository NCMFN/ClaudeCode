import pandas as pd
import scipy.stats as stats
from statsmodels.stats.multicomp import pairwise_tukeyhsd
import numpy as np
import os

def run_analysis():
    df = pd.read_csv('results/tables/simulation_results.csv')
    results = []

    baseline_lt = df[df['Scenario'] == 'Baseline']['Lifetime_mins']
    fsm_lt = df[df['Scenario'] == 'EP-DePIN FSM']['Lifetime_mins']

    baseline_proofs = df[df['Scenario'] == 'Baseline']['Proofs_Submitted']
    fsm_proofs = df[df['Scenario'] == 'EP-DePIN FSM']['Proofs_Submitted']

    # 4. Shapiro-Wilk normality test on battery lifetime
    for scenario in df['Scenario'].unique():
        stat, p = stats.shapiro(df[df['Scenario'] == scenario]['Lifetime_mins'])
        results.append({'Test': 'Shapiro-Wilk', 'Comparison': scenario, 'Statistic': stat, 'P-Value': p})

    # 1. Paired t-test (or independent, since they are independent runs with same seeds)
    t_stat, p_val = stats.ttest_rel(fsm_lt.values, baseline_lt.values)
    results.append({'Test': 'Paired t-test', 'Comparison': 'EP-DePIN vs Baseline Lifetime', 'Statistic': t_stat, 'P-Value': p_val})

    # 2. One-way ANOVA
    anova_groups = [group['Lifetime_mins'].values for name, group in df.groupby('Scenario')]
    f_stat, anova_p = stats.f_oneway(*anova_groups)
    results.append({'Test': 'One-way ANOVA', 'Comparison': 'All Scenarios Lifetime', 'Statistic': f_stat, 'P-Value': anova_p})

    # Tukey HSD
    if anova_p < 0.05:
        tukey = pairwise_tukeyhsd(endog=df['Lifetime_mins'], groups=df['Scenario'], alpha=0.05)
        # Store as string for simplicity
        results.append({'Test': 'Tukey HSD', 'Comparison': 'All', 'Statistic': np.nan, 'P-Value': np.nan, 'Notes': str(tukey.summary())})

    # 3. Wilcoxon signed-rank test
    w_stat, w_p = stats.wilcoxon(fsm_proofs.values, baseline_proofs.values)
    results.append({'Test': 'Wilcoxon signed-rank', 'Comparison': 'EP-DePIN vs Baseline Proofs', 'Statistic': w_stat, 'P-Value': w_p})

    # 5. Cohen's d
    mean_diff = fsm_lt.mean() - baseline_lt.mean()
    pooled_sd = np.sqrt((fsm_lt.std()**2 + baseline_lt.std()**2) / 2)
    cohens_d = mean_diff / pooled_sd
    results.append({'Test': "Cohen's d", 'Comparison': 'EP-DePIN vs Baseline Lifetime', 'Statistic': cohens_d, 'P-Value': np.nan})

    # Save
    pd.DataFrame(results).to_csv('results/tables/statistical_tests.csv', index=False)

    print("Statistical tests completed.")

if __name__ == '__main__':
    run_analysis()
