import matplotlib.pyplot as plt
import matplotlib.patches as patches
import os

# Set global matplotlib parameters for high quality
plt.rcParams.update({'font.size': 11, 'axes.titlesize': 13, 'axes.labelsize': 11, 'xtick.labelsize': 10, 'ytick.labelsize': 10, 'figure.dpi': 300, 'savefig.dpi': 300})

def draw_architecture():
    fig, ax = plt.subplots(figsize=(12, 6))
    ax.axis('off')

    # Set explicit axis limits so patches are actually visible!
    ax.set_xlim(0, 13)
    ax.set_ylim(0, 5)

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
        'Raw Data': (1.5, 3, 'data', "Data Ingestion\nOpenML / NASA MDP"),
        'Preprocess': (4.5, 3, 'process', "Target Engineering\nMethods A, B, C"),
        'EDA': (4.5, 1.5, 'process', "EDA & Feature Selection\nRFE, Mutal Info"),
        'Training': (8, 3, 'model', "Model Training\nRF, XGBoost, CV"),
        'Evaluation': (8, 1.5, 'model', "Evaluation\nCross-Domain, SHAP"),
        'API': (11.5, 3, 'api', "FastAPI Service\nPredict Decomposition")
    }

    boxes = {}
    for key, (x, y, type_name, label) in nodes.items():
        # A bit of manual width adjustments
        width = 2.2
        height = 1.0

        box = patches.FancyBboxPatch((x - width/2, y - height/2), width, height, boxstyle=box_style,
                                     facecolor=colors[type_name], edgecolor=edge_colors[type_name],
                                     linewidth=2)
        ax.add_patch(box)
        ax.text(x, y, label, ha='center', va='center', fontsize=11, fontweight='bold', color='#333333')
        boxes[key] = (x, y, width, height)

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
        x1, y1, w1, h1 = boxes[start]
        x2, y2, w2, h2 = boxes[end]

        # Calculate intersection points on the border of the boxes
        if x1 == x2:
            # Vertical
            start_point = (x1, y1 - h1/2 if y1 > y2 else y1 + h1/2)
            end_point = (x2, y2 + h2/2 if y1 > y2 else y2 - h2/2)
            connection_style = "arc3,rad=0"
        elif y1 == y2:
            # Horizontal
            start_point = (x1 + w1/2 if x1 < x2 else x1 - w1/2, y1)
            end_point = (x2 - w2/2 if x1 < x2 else x2 + w2/2, y2)
            connection_style = "arc3,rad=0"
        else:
            # Diagonal/curved
            start_point = (x1 + w1/2 if x1 < x2 else x1 - w1/2, y1)
            end_point = (x2, y2 + h2/2 if y1 < y2 else y2 - h2/2)
            connection_style = "arc3,rad=-0.2" if y1 < y2 else "arc3,rad=0.2"

        ax.annotate('', xy=end_point,
                    xytext=start_point,
                    arrowprops=dict(arrowstyle="->", color='#666666', lw=2, connectionstyle=connection_style))

    plt.title("Decomposition Predictor System Architecture", fontsize=16, fontweight='bold', pad=20)
    plt.tight_layout()

    # Save to current working directory (which will be repository root when moved)
    out_path = 'system_architecture.png'
    plt.savefig(out_path, bbox_inches='tight')
    plt.close()

if __name__ == "__main__":
    draw_architecture()
