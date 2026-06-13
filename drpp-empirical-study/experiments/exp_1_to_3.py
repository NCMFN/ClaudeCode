import os
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src')))

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from drpp_core import run_monte_carlo_drpp

# Global plotting params for clarity
plt.rcParams.update({'font.size': 11, 'axes.titlesize': 13, 'axes.labelsize': 11, 'xtick.labelsize': 10, 'ytick.labelsize': 10, 'figure.dpi': 300, 'savefig.dpi': 300})

def save_table(df: pd.DataFrame, filename_base: str, caption: str):
    """Saves a dataframe to CSV, Tex, and Markdown."""
    df.to_csv(f'tables/{filename_base}.csv', index=False)
    with open(f'tables/{filename_base}.tex', 'w') as f:
        f.write(f"% {caption}\n")
        f.write(df.to_latex(index=False))
    with open(f'tables/{filename_base}.md', 'w') as f:
        f.write(f"**{caption}**\n\n")
        f.write(df.to_markdown(index=False))

def save_figure(fig, filename: str, caption: str):
    """Saves a figure to PNG and SVG, and saves caption."""
    fig.savefig(f'figures/{filename}.png', bbox_inches='tight')
    fig.savefig(f'figures/{filename}.svg', bbox_inches='tight')
    with open(f'figures/{filename}_caption.txt', 'w') as f:
        f.write(caption)

def exp_A():
    print("Running Experiment A: Theoretical vs Simulated P_attack")
    trials = 10000
    k_range = range(1, 21)
    results = []

    np.random.seed(42)
    for k in k_range:
        sim_p = run_monte_carlo_drpp(k, trials, "single")
        theo_p = 2**(-k)

        # 95% CI for binomial proportion
        ci = 1.96 * np.sqrt((sim_p * (1 - sim_p)) / trials)

        results.append({
            'k': k,
            'Theoretical_P_attack': theo_p,
            'Simulated_P_attack': sim_p,
            'Simulated_CI_95': ci
        })

    df = pd.DataFrame(results)
    df.to_csv('data/expA_results.csv', index=False)
    save_table(df, 'T1', 'Extended attack probability table, k=1-20, theoretical vs. simulated mean ± 95% CI')

    fig, ax = plt.subplots(figsize=(8, 6))
    ax.plot(df['k'], df['Theoretical_P_attack'], label='Theoretical (2^-k)', marker='o')
    ax.errorbar(df['k'], df['Simulated_P_attack'], yerr=df['Simulated_CI_95'], label='Simulated (10k trials)', fmt='x')
    ax.set_yscale('log')
    ax.set_xlabel('Challenge Size k (bits)')
    ax.set_ylabel('Attack Probability (Log Scale)')
    ax.set_title('DRPP Theoretical vs. Simulated Attack Probability')
    ax.legend()
    ax.grid(True, which="both", ls="-", alpha=0.2)
    save_figure(fig, 'F1_theoretical_vs_simulated', 'F1: Theoretical vs. simulated attack probability vs. k (log-y), k=1–20. Shows tight empirical alignment with 2^-k.')
    plt.close(fig)

def exp_B():
    print("Running Experiment B: Collusion Attack Success")
    trials = 5000
    k_range = range(1, 17)
    n_colluders = [2, 3, 4, 5, 6, 8, 10]

    results = []
    np.random.seed(42)
    for k in k_range:
        for n in n_colluders:
            sim_p = run_monte_carlo_drpp(k, trials, "collusion", n_colluders=n)
            results.append({'k': k, 'n_colluders': n, 'Simulated_P_attack': sim_p})

    df = pd.DataFrame(results)
    df.to_csv('data/expB_results.csv', index=False)
    save_table(df, 'T2', 'Collusion attack probability table, n=2-10 × k=1-16')

    fig, ax = plt.subplots(figsize=(10, 6))
    sns.lineplot(data=df, x='k', y='Simulated_P_attack', hue='n_colluders', marker='o', palette='viridis', ax=ax)
    ax.set_yscale('log')
    ax.set_xlabel('Challenge Size k (bits)')
    ax.set_ylabel('Attack Probability (Log Scale)')
    ax.set_title('Collusion Attack Probability by Number of Colluders')
    ax.grid(True, which="both", ls="-", alpha=0.2)
    save_figure(fig, 'F2_collusion_probability', 'F2: Collusion attack probability vs. k for n=2..10. As n increases, probability scales up linearly but decays exponentially with k.')
    plt.close(fig)

def exp_C():
    print("Running Experiment C: Traditional Baseline Sensitivity")
    trials = 10000
    p_deception_range = np.arange(0.1, 0.65, 0.05)

    results = []
    np.random.seed(42)
    for p in p_deception_range:
        sim_p = run_monte_carlo_drpp(10, trials, "baseline", success_probability=p)
        results.append({'Ambient_Deception_Prob': p, 'Simulated_Attack_Success': sim_p})

    df = pd.DataFrame(results)
    df.to_csv('data/expC_results.csv', index=False)
    save_table(df, 'T3', 'Traditional baseline sensitivity table (deception probability sweep)')

    # Also create F3 comparing DRPP (k=1..16), Collusion (n=2), Traditional (p=0.34)
    k_range = range(1, 17)
    comp_results = []
    np.random.seed(42)
    for k in k_range:
        drpp_p = run_monte_carlo_drpp(k, trials, "single")
        col_p = run_monte_carlo_drpp(k, trials, "collusion", n_colluders=2)
        trad_p = run_monte_carlo_drpp(k, trials, "baseline", success_probability=0.34)
        comp_results.append({'k': k, 'DRPP': drpp_p, 'Collusion_n2': col_p, 'Traditional_0.34': trad_p})

    df_comp = pd.DataFrame(comp_results)

    fig, ax = plt.subplots(figsize=(8, 6))
    ax.plot(df_comp['k'], df_comp['DRPP'], label='DRPP (Single Guess)', marker='o', color='#1F3864')
    ax.plot(df_comp['k'], df_comp['Collusion_n2'], label='Collusion (n=2)', marker='s', color='#BA7517')
    ax.plot(df_comp['k'], df_comp['Traditional_0.34'], label='Traditional (~34%)', linestyle='--', color='#993C1D')
    ax.set_yscale('log')
    ax.set_xlabel('Challenge Size k (bits)')
    ax.set_ylabel('Attack Probability (Log Scale)')
    ax.set_title('Recreated Comparison: DRPP vs Collusion vs Traditional')
    ax.legend()
    ax.grid(True, which="both", ls="-", alpha=0.2)
    save_figure(fig, 'F3_comparison', 'F3: Recreated comparison: DRPP vs. collusion vs. traditional, full k range. Shows that DRPP quickly outperforms the fixed ~34% baseline.')
    plt.close(fig)

if __name__ == "__main__":
    os.makedirs('data', exist_ok=True)
    os.makedirs('figures', exist_ok=True)
    os.makedirs('tables', exist_ok=True)
    exp_A()
    exp_B()
    exp_C()
