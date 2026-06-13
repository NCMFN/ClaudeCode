import sys
import os
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import config

def plot_figure3():
    results_path = os.path.join(config.OUTPUT_DIR, "results", "analysis_report.csv")
    if not os.path.exists(results_path):
        return

    df = pd.read_csv(results_path)
    k_values = config.K_VALUES

    drpp_probs = []
    col_probs = []
    trad_probs = []

    for k in k_values:
        d_val = df[(df["k"] == k) & (df["model"] == "DRPP")]["mean_prob"].values
        drpp_probs.append(d_val[0] * 100 if len(d_val) > 0 and pd.notna(d_val[0]) else np.nan)

        c_val = df[(df["k"] == k) & (df["model"] == "Collusion")]["mean_prob"].values
        # Mask out values not in paper for plot consistency
        if k in [1, 2, 4, 6, 8, 12] and len(c_val) > 0 and pd.notna(c_val[0]):
            col_probs.append(c_val[0] * 100)
        else:
            col_probs.append(np.nan)

        t_val = df[(df["k"] == k) & (df["model"] == "Traditional")]["mean_prob"].values
        trad_probs.append(t_val[0] * 100 if len(t_val) > 0 and pd.notna(t_val[0]) else np.nan)

    plt.style.use('seaborn-v0_8-whitegrid')
    plt.rcParams.update({
        'font.family': config.FONT_FAMILY,
        'font.size': config.FONT_SIZE,
        'figure.figsize': config.FIGURE_SIZE,
        'figure.dpi': config.FIGURE_DPI,
        'savefig.dpi': config.FIGURE_DPI
    })

    fig, ax = plt.subplots()

    ax.plot(k_values, drpp_probs, label="DRPP", color="blue", linestyle="-", marker="o")

    k_col = [k for i, k in enumerate(k_values) if not np.isnan(col_probs[i])]
    col_probs_valid = [p for p in col_probs if not np.isnan(p)]
    ax.plot(k_col, col_probs_valid, label="Collusion", color="red", linestyle="--", marker="s")

    ax.plot(k_values, trad_probs, label="Traditional", color="black", linestyle=":", marker="")

    k_theo = np.linspace(min(k_values), max(k_values), 100)
    theo_probs = (2.0 ** -k_theo) * 100
    ax.plot(k_theo, theo_probs, label=r"Theoretical Bound ($2^{-k}$)", color="grey", linestyle="--", alpha=0.7)

    ax.set_yscale('log')
    ax.set_ylim([1e-4, 1e2])
    ax.set_xlabel("Challenge Size (bits)")
    ax.set_ylabel("Attack Success Probability (%)")
    ax.set_xticks(k_values)
    ax.grid(True, which="major", axis="y", linestyle="-", alpha=0.7)
    ax.grid(True, which="minor", axis="y", linestyle=":", alpha=0.4)
    ax.legend(loc="lower left")

    os.makedirs(os.path.join(config.OUTPUT_DIR, "figures"), exist_ok=True)
    png_path = os.path.join(config.OUTPUT_DIR, "figures", "figure3_attack_probability.png")
    pdf_path = os.path.join(config.OUTPUT_DIR, "figures", "figure3_attack_probability.pdf")

    plt.tight_layout()
    plt.savefig(png_path)
    plt.savefig(pdf_path)
    plt.close()

if __name__ == "__main__":
    plot_figure3()
