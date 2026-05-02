import matplotlib.pyplot as plt
import matplotlib.patches as patches

def create_architecture_diagram():
    fig, ax = plt.subplots(figsize=(12, 8))
    ax.axis('off')

    # Global settings as per memory guidelines
    plt.rcParams.update({'font.size': 11, 'axes.titlesize': 13, 'axes.labelsize': 11,
                         'xtick.labelsize': 10, 'ytick.labelsize': 10,
                         'figure.dpi': 300, 'savefig.dpi': 300})

    # Define blocks
    blocks = [
        {"text": "NHIS Raw Data\n(adult22.csv)", "pos": (0.1, 0.7), "color": "#d9ead3"},
        {"text": "Data Preprocessing\n(Age 20-39 filter,\nImputation, Encoding)", "pos": (0.4, 0.7), "color": "#cfe2f3"},
        {"text": "Feature Engineering\n(Risk Scores,\nSMOTE Balancing)", "pos": (0.7, 0.7), "color": "#cfe2f3"},

        {"text": "Model Training\n(RF, XGBoost,\nOptuna Tuning)", "pos": (0.7, 0.4), "color": "#fce5cd"},
        {"text": "Evaluation &\nSHAP Analysis", "pos": (0.4, 0.4), "color": "#ead1dc"},

        {"text": "Outputs\n(Models, Metrics,\nSHAP Plots)", "pos": (0.1, 0.4), "color": "#fff2cc"}
    ]

    # Draw blocks
    for block in blocks:
        box = patches.FancyBboxPatch((block["pos"][0]-0.12, block["pos"][1]-0.08),
                                     0.24, 0.16, boxstyle="round,pad=0.02",
                                     ec="black", fc=block["color"], lw=1.5)
        ax.add_patch(box)
        ax.text(block["pos"][0], block["pos"][1], block["text"],
                ha="center", va="center", fontsize=11, fontweight='bold')

    # Draw arrows
    arrows = [
        ((0.23, 0.7), (0.27, 0.7)), # Raw -> Preprocessing
        ((0.53, 0.7), (0.57, 0.7)), # Preprocessing -> Feature Eng
        ((0.7, 0.61), (0.7, 0.49)), # Feature Eng -> Training
        ((0.57, 0.4), (0.53, 0.4)), # Training -> Eval
        ((0.27, 0.4), (0.23, 0.4))  # Eval -> Outputs
    ]

    for start, end in arrows:
        ax.annotate("", xy=end, xytext=start, arrowprops=dict(arrowstyle="->", lw=2))

    plt.title("System Architecture: Heart & Mind CVD Risk Predictor Pipeline", fontsize=14, fontweight='bold', y=0.9)

    plt.savefig('SYSTEM ARCHITECTURE.PNG', bbox_inches='tight')
    print("Saved SYSTEM ARCHITECTURE.PNG")

if __name__ == "__main__":
    create_architecture_diagram()
