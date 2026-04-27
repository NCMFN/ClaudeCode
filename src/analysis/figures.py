import pandas as pd
import matplotlib.pyplot as plt
import os
import logging
from datetime import datetime

# Setup
os.makedirs("results/logs", exist_ok=True)
os.makedirs("results/figures", exist_ok=True)
logging.basicConfig(
    filename="results/logs/figures.log",
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

# Global plot styling for IEEE format
plt.rcParams.update({
    'font.size': 11, 'axes.titlesize': 13, 'axes.labelsize': 11,
    'xtick.labelsize': 10, 'ytick.labelsize': 10,
    'figure.dpi': 300, 'savefig.dpi': 300,
    'legend.fontsize': 10
})

# Fixed Color Scheme
COLORS = {
    "S1_FULL": "#1D9E75",
    "S2_PROOF_ONLY": "#BA7517",
    "S3_RELAY_ONLY": "#993C1D",
    "S4_PRIMARY_ONLY": "#888780",
    "Baseline": "#1F3864"
}

def plot_soc_trajectory():
    plt.figure(figsize=(10, 5))

    # Load data
    baseline = pd.read_csv("results/tables/history_Baseline.csv")
    fsm_def = pd.read_csv("results/tables/history_FSM_Default.csv")

    # Plot Baseline
    plt.plot(baseline['time']/60, baseline['soc'],
             label='Baseline (No FSM)', color=COLORS['Baseline'], linestyle='--')

    # Plot FSM Default
    plt.plot(fsm_def['time']/60, fsm_def['soc'],
             label='FSM Default', color=COLORS['S1_FULL'])

    # Mark transitions for FSM
    transitions = fsm_def[fsm_def['state'] != fsm_def['state'].shift(1)].dropna()
    for _, row in transitions.iterrows():
        state = row['state']
        if state in COLORS:
            plt.scatter(row['time']/60, row['soc'], color=COLORS[state], s=50, zorder=5)

    plt.axhline(y=60, color='gray', linestyle=':', alpha=0.5, label='T1 (60%)')
    plt.axhline(y=35, color='gray', linestyle=':', alpha=0.5, label='T2 (35%)')
    plt.axhline(y=15, color='red', linestyle=':', alpha=0.5, label='T3 (15%)')

    plt.title('State of Charge (SoC) Trajectory over 72 Hours')
    plt.xlabel('Time (Hours)')
    plt.ylabel('State of Charge (%)')
    plt.ylim(0, 100)
    plt.xlim(0, 72)
    plt.grid(True, alpha=0.3)
    plt.legend(loc='upper right')

    plt.tight_layout()
    plt.savefig('results/figures/soc_trajectory.png')
    plt.savefig('results/figures/soc_trajectory.pdf')
    plt.close()

def plot_performance_metrics():
    df = pd.read_csv("results/tables/simulation_summary.csv")

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 5))

    # Exclude No_Blockchain for visual comparison
    df_plot = df[df['Scenario'] != 'No_Blockchain']

    # Battery Lifetime
    ax1.bar(df_plot['Scenario'], df_plot['Battery_Lifetime_hrs'], color=COLORS['Baseline'])
    ax1.set_title('Battery Lifetime by Scenario')
    ax1.set_ylabel('Lifetime (Hours)')
    ax1.tick_params(axis='x', rotation=45)
    ax1.axhline(y=72, color='red', linestyle='--', alpha=0.5, label='Max (72h)')
    ax1.legend()

    # Proof Success vs Missed
    width = 0.35
    x = range(len(df_plot))

    ax2.bar([i - width/2 for i in x], df_plot['Proof_Success'], width,
            label='Successful', color=COLORS['S1_FULL'])
    ax2.bar([i + width/2 for i in x], df_plot['Proof_Missed'], width,
            label='Missed', color=COLORS['S3_RELAY_ONLY'])

    ax2.set_title('Proof of Coverage Performance')
    ax2.set_ylabel('Number of Proofs')
    ax2.set_xticks(x)
    ax2.set_xticklabels(df_plot['Scenario'], rotation=45)
    ax2.legend()

    plt.tight_layout()
    plt.savefig('results/figures/performance_metrics.png')
    plt.savefig('results/figures/performance_metrics.pdf')
    plt.close()

def generate_figures():
    start_time = datetime.now()
    logging.info("Starting figure generation")
    print("Generating figures...")

    plot_soc_trajectory()
    plot_performance_metrics()

    end_time = datetime.now()
    logging.info(f"Figures generated in {end_time - start_time}.")
    print("Figure generation complete.")

if __name__ == "__main__":
    try:
        generate_figures()
    except Exception as e:
        logging.error(f"Figure generation failed: {str(e)}")
        raise
