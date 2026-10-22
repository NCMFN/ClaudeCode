import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

# Global settings for matplotlib
plt.rcParams.update({'font.size': 11, 'axes.titlesize': 13, 'axes.labelsize': 11, 'xtick.labelsize': 10, 'ytick.labelsize': 10, 'figure.dpi': 300, 'savefig.dpi': 300})

COLORS = {
    'S1_FULL': '#1D9E75',
    'S2_PROOF_ONLY': '#BA7517',
    'S3_RELAY_ONLY': '#993C1D',
    'S4_PRIMARY_ONLY': '#888780',
    'Baseline': '#1F3864'
}

def plot_all():
    df = pd.read_csv('results/tables/simulation_results.csv')
    summary = pd.read_csv('results/tables/simulation_summary.csv')

    # Fig 1: Battery lifetime
    plt.figure(figsize=(10, 6))
    scenarios = summary['Scenario']
    means = summary['Lifetime_mins_mean']
    stds = summary['Lifetime_mins_std']

    # Custom colors
    bar_colors = [COLORS['Baseline'] if s == 'Baseline' else COLORS['S1_FULL'] for s in scenarios]

    plt.bar(scenarios, means, yerr=stds, capsize=5, color=bar_colors)
    plt.title('Figure 1: Battery Lifetime per Scenario')
    plt.ylabel('Minutes until depletion')
    plt.xlabel('Scenario')
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.savefig('results/figures/battery_lifetime_comparison.png')
    plt.savefig('results/figures/battery_lifetime_comparison.pdf')
    plt.close()

    # Fig 4: Proof submissions
    plt.figure(figsize=(10, 6))
    proof_means = summary['Proofs_Submitted_mean']
    proof_stds = summary['Proofs_Submitted_std']
    plt.bar(scenarios, proof_means, yerr=proof_stds, capsize=5, color=bar_colors)
    plt.title('Figure 4: Proof Submissions per Scenario')
    plt.ylabel('Proof count (mean)')
    plt.xlabel('Scenario')
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.savefig('results/figures/proof_submissions.png')
    plt.savefig('results/figures/proof_submissions.pdf')
    plt.close()

    # Fig 5: State time distribution
    # Filter only EP-DePIN variants
    ep_variants = df[df['Scenario'].str.contains('EP-DePIN')].groupby('Scenario').mean().reset_index()

    fig, ax = plt.subplots(figsize=(10, 6))
    bottom = np.zeros(len(ep_variants))

    for state in ['S1_Time', 'S2_Time', 'S3_Time', 'S4_Time']:
        state_key = state.replace('_Time', '')
        if state_key == 'S1': state_key = 'S1_FULL'
        elif state_key == 'S2': state_key = 'S2_PROOF_ONLY'
        elif state_key == 'S3': state_key = 'S3_RELAY_ONLY'
        elif state_key == 'S4': state_key = 'S4_PRIMARY_ONLY'

        values = ep_variants[state].values
        # Convert to percentage
        totals = ep_variants[['S1_Time', 'S2_Time', 'S3_Time', 'S4_Time']].sum(axis=1).values
        percentages = (values / totals) * 100

        ax.bar(ep_variants['Scenario'], percentages, bottom=bottom, label=state_key, color=COLORS[state_key])
        bottom += percentages

    ax.set_title('Figure 5: State Time Distribution')
    ax.set_ylabel('% time in state')
    ax.set_xlabel('Scenario')
    ax.legend(title='Active state')
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.savefig('results/figures/state_time_distribution.png')
    plt.savefig('results/figures/state_time_distribution.pdf')
    plt.close()

if __name__ == '__main__':
    plot_all()
