import sys
import os
import numpy as np
import matplotlib.pyplot as plt

# Add parent dir to path to import config
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import config

def plot_security_bound():
    """
    Plots Equation 5 from the paper: Adv_total = Adv_crypto + Adv_physical
    """
    k_values = np.linspace(1, 20, 100)

    adv_crypto = 2.0 ** -k_values
    adv_physical_levels = [0.01, 0.05, 0.10, 0.20]

    plt.style.use('seaborn-v0_8-whitegrid')
    plt.rcParams.update({
        'font.family': config.FONT_FAMILY,
        'font.size': config.FONT_SIZE,
        'figure.figsize': config.FIGURE_SIZE,
        'figure.dpi': config.FIGURE_DPI,
        'savefig.dpi': config.FIGURE_DPI
    })

    fig, ax = plt.subplots()

    # Plot adv_crypto
    ax.plot(k_values, adv_crypto, label=r"Adv$_{crypto} = 2^{-k}$", color="black", linestyle="--", linewidth=2)

    # Plot Adv_total for varying Adv_physical
    colors = ["blue", "green", "orange", "purple"]

    for i, adv_phys in enumerate(adv_physical_levels):
        adv_total = adv_crypto + adv_phys
        ax.plot(k_values, adv_total, label=r"Adv$_{total}$ (Adv$_{phys}$=" + f"{adv_phys})", color=colors[i], linestyle="-")

    # Shade region where Adv_total > 0.05
    # The requirement is to shade the entire region > 0.05 in light red.
    ax.axhspan(0.05, 2.0, facecolor='red', alpha=0.1, label='Insecure Zone (>0.05)')

    # Formatting
    ax.set_yscale('log')
    ax.set_ylim([1e-4, 2e0])
    ax.set_xlim([1, 20])
    ax.set_xlabel("Challenge Size (bits), $k$")
    ax.set_ylabel("Total Advantage (Probability)")
    ax.set_title("Side-Channel Security Bound")

    # X-ticks
    ax.set_xticks(np.arange(2, 21, 2))

    # Grid
    ax.grid(True, which="major", axis="both", linestyle="-", alpha=0.7)

    # Legend
    # Move legend outside or to an optimal position
    ax.legend(loc="lower left", fontsize=8)

    # Save
    os.makedirs(os.path.join(config.OUTPUT_DIR, "figures"), exist_ok=True)

    png_path = os.path.join(config.OUTPUT_DIR, "figures", "security_bound.png")

    plt.tight_layout()
    plt.savefig(png_path)
    plt.close()

    print(f"Saved Security Bound Plot to {png_path}")

if __name__ == "__main__":
    plot_security_bound()
