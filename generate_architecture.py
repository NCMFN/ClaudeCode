import matplotlib.pyplot as plt
import matplotlib.patches as patches
import os

def create_architecture_diagram():
    fig, ax = plt.subplots(figsize=(16, 10), dpi=400)
    ax.axis('off')

    # Coordinates
    x_start = 0.05
    y_top = 0.8
    y_mid = 0.5
    y_bot = 0.2
    box_w = 0.15
    box_h = 0.1
    spacing = 0.2

    # Draw boxes
    def draw_box(x, y, text, color, bg_color):
        box = patches.FancyBboxPatch((x, y), box_w, box_h,
                                     boxstyle="round,pad=0.02,rounding_size=0.02",
                                     linewidth=2.5, edgecolor=color, facecolor=bg_color)
        ax.add_patch(box)
        ax.text(x + box_w/2, y + box_h/2, text, ha='center', va='center',
                fontsize=11, fontweight='bold', color='black')
        return x, y

    # Define nodes
    nodes = {
        'Kaggle': (x_start, y_mid, 'Kaggle Dataset\n(Open Food Facts)', '#1f77b4', '#e6f2ff'),
        'Load': (x_start + spacing, y_mid, 'Data Loading\n& Exploration', '#ff7f0e', '#fff2e6'),
        'Clean': (x_start + 2*spacing, y_mid, 'Data Cleaning\n& Imputation', '#2ca02c', '#e6ffe6'),
        'Eng': (x_start + 3*spacing, y_mid, 'Feature Eng\n(TF-IDF + Scaler)', '#d62728', '#ffe6e6'),
        'Train': (x_start + 4*spacing, y_top, 'Model Training\n(RF, XGB, MLP)', '#9467bd', '#f2e6ff'),
        'Eval': (x_start + 4*spacing, y_mid, 'Evaluation\n& Metrics', '#8c564b', '#f2ebe6'),
        'SMOTE': (x_start + 3*spacing, y_top, 'SMOTE\n(Class Imbalance)', '#e377c2', '#ffe6f2'),
        'Artifacts': (x_start + 4*spacing, y_bot, 'Artifacts\n(outputs/)', '#7f7f7f', '#ebebeb')
    }

    pos = {}
    for key, (x, y, text, color, bg_color) in nodes.items():
        pos[key] = draw_box(x, y, text, color, bg_color)

    # Draw arrows
    def draw_arrow(start_key, end_key, style='solid'):
        x1, y1 = pos[start_key][0] + box_w, pos[start_key][1] + box_h/2
        x2, y2 = pos[end_key][0], pos[end_key][1] + box_h/2
        if start_key == 'Eng' and end_key == 'Train':
            y1 += 0.02
        if start_key == 'SMOTE' and end_key == 'Train':
            x1, y1 = pos[start_key][0] + box_w, pos[start_key][1] + box_h/2
            x2, y2 = pos[end_key][0], pos[end_key][1] + box_h/2

        # Adjust for vertical/diagonal arrows
        if start_key == 'Eval' and end_key == 'SMOTE':
            x1, y1 = pos[start_key][0] + box_w/2, pos[start_key][1]
            x2, y2 = pos[end_key][0] + box_w/2, pos[end_key][1] + box_h
            ax.annotate('', xy=(x2, y2), xytext=(x1, y1),
                        arrowprops=dict(arrowstyle="->", lw=2.5, ls='dashed', color='gray', connectionstyle="arc3,rad=-0.3"))
            return

        if start_key == 'Eng' and end_key == 'Artifacts':
             x1, y1 = pos[start_key][0] + box_w/2, pos[start_key][1]
             x2, y2 = pos[end_key][0], pos[end_key][1] + box_h/2
             ax.annotate('', xy=(x2, y2), xytext=(x1, y1),
                        arrowprops=dict(arrowstyle="->", lw=2.5, color='gray', connectionstyle="angle,angleA=0,angleB=90,rad=10"))
             return

        if start_key in ['Train', 'Eval'] and end_key == 'Artifacts':
             x1, y1 = pos[start_key][0] + box_w/2, pos[start_key][1]
             x2, y2 = pos[end_key][0] + box_w/2, pos[end_key][1] + box_h
             ax.annotate('', xy=(x2, y2), xytext=(x1, y1),
                        arrowprops=dict(arrowstyle="->", lw=2.5, color='gray'))
             return

        ls = 'dashed' if style == 'dashed' else 'solid'
        ax.annotate('', xy=(x2, y2), xytext=(x1, y1),
                    arrowprops=dict(arrowstyle="->", lw=2.5, ls=ls, color='black'))

    draw_arrow('Kaggle', 'Load')
    draw_arrow('Load', 'Clean')
    draw_arrow('Clean', 'Eng')
    draw_arrow('Eng', 'Train')
    draw_arrow('Eng', 'Eval')
    draw_arrow('Train', 'Eval')
    draw_arrow('Eval', 'SMOTE', 'dashed')
    draw_arrow('SMOTE', 'Train')
    draw_arrow('Eng', 'Artifacts')
    draw_arrow('Train', 'Artifacts')
    draw_arrow('Eval', 'Artifacts')

    plt.title("NOVA Classification ML Pipeline Architecture", fontsize=18, fontweight='bold', pad=20)

    os.makedirs('outputs/run_pipeline', exist_ok=True)
    plt.savefig('outputs/run_pipeline/architecture.png', dpi=400, bbox_inches='tight')
    plt.close()

if __name__ == "__main__":
    create_architecture_diagram()
