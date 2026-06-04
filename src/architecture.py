import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import os

# Standard rcParams for clear plots
plt.rcParams.update({'font.size': 11, 'axes.titlesize': 13, 'axes.labelsize': 11, 'xtick.labelsize': 10, 'ytick.labelsize': 10, 'figure.dpi': 300, 'savefig.dpi': 300})

def draw_architecture(out_dir="results/figures"):
    os.makedirs(out_dir, exist_ok=True)

    fig, ax = plt.subplots(figsize=(12, 8))
    ax.axis('off')

    # Define colors
    color_ingestion = '#8cbfdb' # Light blue
    color_processing = '#a8e6cf' # Light green
    color_ml = '#ffd3b6' # Light orange
    color_sim = '#ffaaa5' # Light coral

    # Draw boxes
    boxes = {
        'Data Ingestion': mpatches.FancyBboxPatch((1, 6), 3, 1.5, boxstyle="round,pad=0.2", fc=color_ingestion, ec="black", lw=2),
        'Data Preprocessing': mpatches.FancyBboxPatch((5, 6), 3, 1.5, boxstyle="round,pad=0.2", fc=color_processing, ec="black", lw=2),
        'Feature Engineering': mpatches.FancyBboxPatch((9, 6), 3, 1.5, boxstyle="round,pad=0.2", fc=color_processing, ec="black", lw=2),
        'Model Training\n(XGBoost, RF, SVR)': mpatches.FancyBboxPatch((5, 3), 3, 1.5, boxstyle="round,pad=0.2", fc=color_ml, ec="black", lw=2),
        'APC Simulation\nLoop': mpatches.FancyBboxPatch((9, 3), 3, 1.5, boxstyle="round,pad=0.2", fc=color_sim, ec="black", lw=2)
    }

    for label, box in boxes.items():
        ax.add_patch(box)
        rx, ry = box.get_x() + box.get_width()/2., box.get_y() + box.get_height()/2.
        ax.text(rx, ry, label, ha='center', va='center', fontsize=12, fontweight='bold', color='black')

    # Draw arrows
    arrows = [
        # Ingestion -> Preprocessing
        ((4, 6.75), (5, 6.75)),
        # Preprocessing -> Feature Engineering
        ((8, 6.75), (9, 6.75)),
        # Feature Engineering -> Model Training
        ((10.5, 6), (10.5, 4.5)), # Down from FE to Sim, wait let's make it FE -> Model Training
        # Actually: FE -> Model Training
        ((7.5, 5.5), (6.5, 4.5)), # Diagonal from Preprocessing/FE to Training
    ]

    # Add an arrow from Feature Engineering to Model Training
    ax.annotate('', xy=(6.5, 4.5), xytext=(10.5, 6), arrowprops=dict(arrowstyle="->", lw=2, color="black"))
    # Ingestion -> Preprocessing
    ax.annotate('', xy=(5, 6.75), xytext=(4, 6.75), arrowprops=dict(arrowstyle="->", lw=2, color="black"))
    # Preprocessing -> Feature Engineering
    ax.annotate('', xy=(9, 6.75), xytext=(8, 6.75), arrowprops=dict(arrowstyle="->", lw=2, color="black"))

    # Model Training -> Simulation
    ax.annotate('', xy=(9, 3.75), xytext=(8, 3.75), arrowprops=dict(arrowstyle="->", lw=2, color="black"))

    # Feedback loop in Simulation
    ax.annotate('', xy=(10.5, 4.5), xytext=(10.5, 4.5),
                arrowprops=dict(arrowstyle="->", lw=2, color="black", connectionstyle="arc3,rad=.5"))
    ax.text(10.5, 4.9, 'Adjust Trans. Power\n(if Accuracy < 75%)', ha='center', va='center', fontsize=10, style='italic')

    plt.title("System Architecture: WSN Signal Detection & Adaptive Power Control", fontsize=16, fontweight='bold', pad=20)
    plt.tight_layout()
    plt.savefig(os.path.join(out_dir, 'system_architecture.png'), bbox_inches='tight')
    plt.close()

if __name__ == "__main__":
    draw_architecture()
