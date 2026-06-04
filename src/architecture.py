import matplotlib.pyplot as plt
import matplotlib.patches as patches
import os

# Standard rcParams for clear plots
plt.rcParams.update({'font.size': 11, 'axes.titlesize': 13, 'axes.labelsize': 11, 'xtick.labelsize': 10, 'ytick.labelsize': 10, 'figure.dpi': 300, 'savefig.dpi': 300})

def draw_architecture(out_dir="results/figures"):
    os.makedirs(out_dir, exist_ok=True)

    # Create figure
    fig, ax = plt.subplots(figsize=(14, 8))

    # Set axis limits and turn off axes
    ax.set_xlim(0, 14)
    ax.set_ylim(0, 8)
    ax.axis('off')

    # Define colors matching the palette conventions
    c_blue = '#8cbfdb'    # ML / Data
    c_green = '#a8e6cf'   # Processing
    c_orange = '#ffd3b6'  # Integration
    c_purple = '#cbaacb'  # Evaluation

    # Draw boxes
    # Data Ingestion
    ax.add_patch(patches.FancyBboxPatch((0.5, 5.5), 2.5, 1.2, boxstyle="round,pad=0.1,rounding_size=0.1", fc=c_blue, ec="black", lw=2))
    ax.text(1.75, 6.1, "Data Ingestion\n(Kaggle WSN Datasets)", ha='center', va='center', fontweight='bold')

    # Preprocessing
    ax.add_patch(patches.FancyBboxPatch((4.0, 5.5), 2.5, 1.2, boxstyle="round,pad=0.1,rounding_size=0.1", fc=c_green, ec="black", lw=2))
    ax.text(5.25, 6.1, "Data Preprocessing\n(Missing, Outliers, Scale)", ha='center', va='center', fontweight='bold')

    # Feature Engineering
    ax.add_patch(patches.FancyBboxPatch((7.5, 5.5), 2.5, 1.2, boxstyle="round,pad=0.1,rounding_size=0.1", fc=c_green, ec="black", lw=2))
    ax.text(8.75, 6.1, "Feature Engineering\n(ENR, SDF, Noise Smooth)", ha='center', va='center', fontweight='bold')

    # Model Training
    ax.add_patch(patches.FancyBboxPatch((11.0, 5.5), 2.5, 1.2, boxstyle="round,pad=0.1,rounding_size=0.1", fc=c_blue, ec="black", lw=2))
    ax.text(12.25, 6.1, "Model Training\n(XGBoost, RF, SVR)", ha='center', va='center', fontweight='bold')

    # Evaluation
    ax.add_patch(patches.FancyBboxPatch((11.0, 2.5), 2.5, 1.2, boxstyle="round,pad=0.1,rounding_size=0.1", fc=c_purple, ec="black", lw=2))
    ax.text(12.25, 3.1, "Evaluation & SHAP\n(Feature Importances)", ha='center', va='center', fontweight='bold')

    # APC Simulation
    ax.add_patch(patches.FancyBboxPatch((5.75, 2.5), 3.5, 1.2, boxstyle="round,pad=0.1,rounding_size=0.1", fc=c_orange, ec="black", lw=2))
    ax.text(7.5, 3.1, "APC Simulation Loop\n(Trigger +10% Power if Acc < 75%)", ha='center', va='center', fontweight='bold')

    # Draw arrows (Flow)
    arrow_props = dict(facecolor='black', edgecolor='black', width=2, headwidth=10, shrink=0.0)

    # Ingestion -> Preprocessing
    ax.annotate("", xy=(4.0, 6.1), xytext=(3.0, 6.1), arrowprops=arrow_props)

    # Preprocessing -> Feature Engineering
    ax.annotate("", xy=(7.5, 6.1), xytext=(6.5, 6.1), arrowprops=arrow_props)

    # Feature Engineering -> Training
    ax.annotate("", xy=(11.0, 6.1), xytext=(10.0, 6.1), arrowprops=arrow_props)

    # Training -> Evaluation
    ax.annotate("", xy=(12.25, 3.7), xytext=(12.25, 5.5), arrowprops=arrow_props)

    # Training -> APC Simulation
    # Arrow from Model Training to APC Simulation
    ax.annotate("", xy=(9.25, 3.1), xytext=(11.0, 5.5), arrowprops=dict(facecolor='black', edgecolor='black', width=2, headwidth=10, shrink=0.0, connectionstyle="arc3,rad=-0.2"))

    # Feedback loop in Simulation (Internal feedback for the loop)
    ax.annotate("", xy=(7.5, 3.7), xytext=(7.5, 2.5), arrowprops=dict(facecolor='black', edgecolor='black', width=2, headwidth=10, shrink=0.0, connectionstyle="arc3,rad=1.5"))
    ax.text(7.5, 4.2, "Modulate Power & Re-evaluate", ha='center', va='center', fontweight='bold', color='darkred')

    plt.title("System Architecture: WSN Signal Detection Accuracy & APC Pipeline", fontsize=16, fontweight='bold')
    plt.savefig(os.path.join(out_dir, 'system_architecture.png'), bbox_inches='tight')
    plt.close()

if __name__ == "__main__":
    draw_architecture()
