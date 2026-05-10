import matplotlib.pyplot as plt
import matplotlib.patches as patches
import os

# Set global matplotlib parameters for high quality
plt.rcParams.update({'font.size': 11, 'axes.titlesize': 13, 'axes.labelsize': 11, 'xtick.labelsize': 10, 'ytick.labelsize': 10, 'figure.dpi': 300, 'savefig.dpi': 300})

def draw_architecture():
    fig, ax = plt.subplots(figsize=(12, 6))
    ax.axis('off')

    # Define styles for boxes
    box_style = "round,pad=0.5"

    colors = {
        'data': '#E1D5E7',    # Light purple
        'process': '#D5E8D4', # Light green
        'model': '#DAE8FC',   # Light blue
        'api': '#FFE6CC'      # Light orange
    }

    edge_colors = {
        'data': '#9673A6',
        'process': '#82B366',
        'model': '#6C8EBF',
        'api': '#D79B00'
    }

    # Define positions and labels
    nodes = {
        'Raw Data': (1, 3, 'data', "Data Ingestion\nOpenML / NASA MDP"),
        'Preprocess': (4, 3, 'process', "Target Engineering\nMethods A, B, C"),
        'EDA': (4, 1.5, 'process', "EDA & Feature Selection\nRFE, Mutal Info"),
        'Training': (7, 3, 'model', "Model Training\nRF, XGBoost, CV"),
        'Evaluation': (7, 1.5, 'model', "Evaluation\nCross-Domain, SHAP"),
        'API': (10, 3, 'api', "FastAPI Service\nPredict Decomposition")
    }

    boxes = {}
    for key, (x, y, type_name, label) in nodes.items():
        box = patches.FancyBboxPatch((x-1, y-0.5), 2, 1, boxstyle=box_style,
                                     facecolor=colors[type_name], edgecolor=edge_colors[type_name],
                                     linewidth=2)
        ax.add_patch(box)
        ax.text(x, y, label, ha='center', va='center', fontsize=11, fontweight='bold', color='#333333')
        boxes[key] = (x, y)

    # Draw arrows
    arrows = [
        ('Raw Data', 'Preprocess'),
        ('Preprocess', 'EDA'),
        ('Preprocess', 'Training'),
        ('EDA', 'Training'),
        ('Training', 'Evaluation'),
        ('Training', 'API')
    ]

    for start, end in arrows:
        x_start, y_start = boxes[start]
        x_end, y_end = boxes[end]

        if x_start == x_end:
            # Vertical arrow
            ax.annotate('', xy=(x_end, y_end+0.5 if y_start < y_end else y_end-0.5),
                        xytext=(x_start, y_start-0.5 if y_start < y_end else y_start+0.5),
                        arrowprops=dict(arrowstyle="->", color='#666666', lw=2))
        else:
            # Horizontal or diagonal arrow
            ax.annotate('', xy=(x_end-1, y_end),
                        xytext=(x_start+1, y_start),
                        arrowprops=dict(arrowstyle="->", color='#666666', lw=2, connectionstyle="arc3,rad=0.1" if y_start != y_end else "arc3,rad=0"))

    plt.title("Decomposition Predictor System Architecture", fontsize=16, fontweight='bold', pad=20)
    plt.tight_layout()

    # Save to current working directory (which will be repository root when moved)
    out_path = 'system_architecture.png'
    plt.savefig(out_path, bbox_inches='tight')
    plt.close()

if __name__ == "__main__":
    draw_architecture()
