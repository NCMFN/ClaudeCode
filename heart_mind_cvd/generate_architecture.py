import matplotlib.pyplot as plt
import matplotlib.patches as patches
import os

def draw_pill(ax, center, width, height, text, ec_color, fc_color):
    box = patches.FancyBboxPatch((center[0]-width/2, center[1]-height/2),
                                 width, height, boxstyle="round,pad=0.2,rounding_size=0.5",
                                 ec=ec_color, fc=fc_color, lw=1.5, zorder=2)
    ax.add_patch(box)
    ax.text(center[0], center[1], text, ha="center", va="center", fontsize=10, fontweight='bold', zorder=3)

def draw_main_box(ax, center, width, height, texts, ec_color, fc_color):
    box = patches.FancyBboxPatch((center[0]-width/2, center[1]-height/2),
                                 width, height, boxstyle="round,pad=0.05,rounding_size=0.3",
                                 ec=ec_color, fc=fc_color, lw=1.5, zorder=2)
    ax.add_patch(box)

    # Simple lines instead of icons to separate sections
    ax.plot([center[0]-width*0.4, center[0]+width*0.4], [center[1]+0.5, center[1]+0.5],
            color=ec_color, linestyle=':', lw=2, zorder=3, alpha=0.5)
    ax.plot([center[0]-width*0.4, center[0]+width*0.4], [center[1]-0.5, center[1]-0.5],
            color=ec_color, linestyle=':', lw=2, zorder=3, alpha=0.5)

    # Text placement
    ax.text(center[0], center[1]+1.5, texts[0], ha="center", va="center", fontsize=9, fontweight='bold', zorder=3)
    ax.text(center[0], center[1], texts[1], ha="center", va="center", fontsize=9, fontweight='bold', zorder=3)
    ax.text(center[0], center[1]-1.5, texts[2], ha="center", va="center", fontsize=9, fontweight='bold', zorder=3)

def create_architecture_diagram():
    fig, ax = plt.subplots(figsize=(14, 8))
    ax.axis('off')
    ax.set_xlim(0, 16)
    ax.set_ylim(0, 10)

    # Global settings as per memory guidelines
    plt.rcParams.update({'font.size': 11, 'axes.titlesize': 13, 'axes.labelsize': 11,
                         'xtick.labelsize': 10, 'ytick.labelsize': 10,
                         'figure.dpi': 300, 'savefig.dpi': 300})

    # Titles
    ax.text(8, 9.5, "System Architecture: Heart & Mind CVD Risk Predictor Pipeline",
            ha="center", va="center", fontsize=16, fontweight='bold')
    ax.text(8, 9.0, "A high-level overview of the end-to-end machine learning pipeline",
            ha="center", va="center", fontsize=12, color="dimgray")

    # Colors matching the image: Purple, Green, Blue, Orange
    # Lighter facecolors, darker edgecolors
    colors = [
        {"ec": "#a64d79", "fc": "#f4cccc"}, # Modified slightly to match purple-ish hue, actually the reference has:
        # Col 1: Purple
        {"ec": "#8e7cc3", "fc": "#f3eafa"},
        # Col 2: Green
        {"ec": "#6aa84f", "fc": "#eaf5e9"},
        # Col 3: Blue
        {"ec": "#3c78d8", "fc": "#eaf1f8"},
        # Col 4: Orange
        {"ec": "#e69138", "fc": "#fcecd9"}
    ]
    colors = colors[1:] # Take the 4 colors

    # Top Pills
    pill_y = 6.5
    pill_width = 3.2
    pill_height = 0.5
    centers_x = [2.5, 6.1, 9.7, 13.3]

    pill_texts = [
        "Data Processing Pipeline",
        "Feature Engineering",
        "Data Splitting & SMOTE",
        "Evaluation & Visualization"
    ]

    for i in range(4):
        draw_pill(ax, (centers_x[i], pill_y), pill_width, pill_height, pill_texts[i], colors[i]["ec"], colors[i]["fc"])

    # Arrows between pills
    for i in range(3):
        start = (centers_x[i] + pill_width/2 + 0.2, pill_y)
        end = (centers_x[i+1] - pill_width/2 - 0.2, pill_y)
        ax.annotate("", xy=end, xytext=start, arrowprops=dict(arrowstyle="-|>", lw=2, color="black"))

    # Arrows down
    for i in range(4):
        start = (centers_x[i], pill_y - pill_height/2 - 0.2)
        end = (centers_x[i], 4.5)
        ax.annotate("", xy=end, xytext=start, arrowprops=dict(arrowstyle="-|>", lw=2, color="black"))

    # Main Boxes
    box_y = 2.5
    box_width = 3.2
    box_height = 3.8

    box_contents = [
        [
            "NHIS 2022 CSV",
            "Age 20-39 Filter\nBinary Target Def",
            "Handle Missing Vals\nCategorical Encoding"
        ],
        [
            "Metabolic Risk\nScore",
            "Mental Health\nBurden Score",
            "One-Hot Encoding\n(Race, Education)"
        ],
        [
            "70/15/15 Split\n(Train/Val/Test)",
            "Stratified K-Fold",
            "SMOTE Oversampling\n(Training Data)"
        ],
        [
            "Model Training\n(RF, XGBoost)",
            "Optuna Tuning\n(Val AUC)",
            "Metrics, ROC Curves,\nSHAP Analysis"
        ]
    ]

    for i in range(4):
        draw_main_box(ax, (centers_x[i], box_y), box_width, box_height, box_contents[i], colors[i]["ec"], colors[i]["fc"])

    output_dir = 'heart_mind_cvd/outputs/figures/'
    os.makedirs(output_dir, exist_ok=True)
    out_path = os.path.join(output_dir, 'system_architecture.png')
    plt.savefig(out_path, bbox_inches='tight')
    print(f"Saved {out_path}")

if __name__ == "__main__":
    create_architecture_diagram()
