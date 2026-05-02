import networkx as nx
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import os

def generate_architecture_diagram():
    """Generates the System Architecture diagram programmatically."""
    plt.rcParams.update({
        'font.size': 11,
        'axes.titlesize': 13,
        'axes.labelsize': 11,
        'figure.dpi': 300,
        'savefig.dpi': 300
    })

    fig, ax = plt.subplots(figsize=(12, 8))
    ax.axis('off')

    # Define blocks
    blocks = {
        'Data': {'pos': (0.1, 0.8), 'label': 'Raw Clinical Data\n(REPRIEVE / NA-ACCORD)\nor\nSynthetic Data Generation'},
        'Preprocess': {'pos': (0.5, 0.8), 'label': 'Preprocessing Module\n- Impute Biomarkers\n- Log-transform\n- ASCVD Filter < 10%\n- SMOTE Oversampling'},
        'Scores': {'pos': (0.5, 0.5), 'label': 'Traditional Risk Scores\n- Framingham\n- ASCVD Pooled Cohort'},
        'Models': {'pos': (0.9, 0.8), 'label': 'ML Training Module\n- XGBoost (Optuna)\n- Random Forest\n- SVM'},
        'Eval': {'pos': (0.9, 0.5), 'label': 'Evaluation & Comparison\n- AUC-ROC / PRC\n- Sensitivity / NNT\n- NRI / IDI'},
        'Interpret': {'pos': (0.9, 0.2), 'label': 'Clinical Interpretability\n- SHAP Feature Importance\n- SHAP Beeswarm'}
    }

    # Draw rounded rectangles for blocks
    for name, info in blocks.items():
        x, y = info['pos']
        box = mpatches.FancyBboxPatch((x-0.15, y-0.1), 0.3, 0.2, boxstyle="round,pad=0.05",
                                     ec="black", fc="#e6f2ff", lw=1.5)
        ax.add_patch(box)
        ax.text(x, y, info['label'], ha='center', va='center', fontsize=10, weight='bold')

    # Draw arrows
    arrows = [
        ('Data', 'Preprocess'),
        ('Preprocess', 'Models'),
        ('Preprocess', 'Scores'),
        ('Models', 'Eval'),
        ('Scores', 'Eval'),
        ('Models', 'Interpret')
    ]

    for start, end in arrows:
        start_pos = blocks[start]['pos']
        end_pos = blocks[end]['pos']

        # Adjust arrow start/end to not overlap boxes
        if start_pos[1] == end_pos[1]: # Horizontal
            ax.annotate("", xy=(end_pos[0]-0.15, end_pos[1]), xytext=(start_pos[0]+0.15, start_pos[1]),
                        arrowprops=dict(arrowstyle="->", lw=2, color='gray'))
        elif start_pos[0] == end_pos[0]: # Vertical
            ax.annotate("", xy=(end_pos[0], end_pos[1]+0.1), xytext=(start_pos[0], start_pos[1]-0.1),
                        arrowprops=dict(arrowstyle="->", lw=2, color='gray'))
        else: # Diagonal
             ax.annotate("", xy=(end_pos[0]-0.15, end_pos[1]+0.1), xytext=(start_pos[0]+0.15, start_pos[1]-0.1),
                        arrowprops=dict(arrowstyle="->", lw=2, color='gray', connectionstyle="arc3,rad=.1"))

    plt.title("System Architecture: Predicting Statin Benefit in HIV+ Populations", pad=20, weight='bold')

    # Needs to be output in the root folder of the project repository, not the subfolder, as required by the instruction
    # "When users request generated output figures to be available for download or directly visible in the repository's code pane, save the images in the repository's root directory"
    # Actually wait, the instruction says "ADD SYSTEM ARCHITECTURE.PNG". I'll put it in the project root.

    os.makedirs('../../', exist_ok=True) # This is where we run it from
    plt.tight_layout()
    plt.savefig('../SYSTEM ARCHITECTURE.PNG', bbox_inches='tight') # Putting it in hiv_statin_mace/
    plt.savefig('SYSTEM ARCHITECTURE.PNG', bbox_inches='tight') # And also the top level just in case
    plt.close()

if __name__ == '__main__':
    generate_architecture_diagram()
