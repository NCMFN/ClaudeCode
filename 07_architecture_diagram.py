import matplotlib.pyplot as plt
import matplotlib.patches as patches

def draw_architecture():
    fig, ax = plt.subplots(figsize=(14, 10), dpi=400)
    ax.set_xlim(0, 100)
    ax.set_ylim(0, 100)
    ax.axis('off')

    plt.title("End-to-End ML Framework: Soil Nutrient Forecasting", fontsize=18, fontweight='bold', pad=20)

    # Styling params
    box_style = "round,pad=0.5"

    def add_block(x, y, w, h, text, color, text_color='black'):
        fancy_box = patches.FancyBboxPatch((x, y), w, h, boxstyle=box_style,
                                           linewidth=2.5, edgecolor='black', facecolor=color)
        ax.add_patch(fancy_box)
        ax.text(x + w/2, y + h/2, text, ha='center', va='center',
                fontsize=11, fontweight='bold', color=text_color, wrap=True)

    def draw_arrow(x1, y1, x2, y2, label=""):
        ax.annotate("", xy=(x2, y2), xytext=(x1, y1),
                    arrowprops=dict(arrowstyle="->", lw=2.5, color='black'))
        if label:
            # Adjust label position slightly above the line
            mx, my = (x1+x2)/2, (y1+y2)/2
            ax.text(mx, my + 1.5, label, ha='center', fontsize=9, fontweight='bold',
                    bbox=dict(facecolor='white', edgecolor='none', alpha=0.8))

    # Phase 1: Data Acquisition (Left)
    add_block(5, 75, 20, 15, "Earth Microbiome Project\n(EMP FTP / Zenodo)\n- 16S rRNA Sequences\n- EMP Mapping metadata", '#E8F5E9')
    add_block(5, 55, 20, 15, "NEON Soil Microbe Data\n(REST API)\n- Soil Chemical Properties\n- Ground Truth Labels", '#E8F5E9')

    # Phase 2: Preprocessing & Engineering (Center-Left)
    add_block(35, 65, 20, 25, "Feature Engineering\n\n1. Filter Soil Samples\n2. Extract BIOM Matrix\n3. CLR Transformation\n4. PCA Reduction (150 comp)\n5. Alpha Diversity (Shannon,\nSimpson, Observed)", '#FFF9C4')

    # Data Fusion (NEON Merge)
    add_block(35, 45, 20, 12, "Data Integration\n\nProximity & Seasonal Merge\n(EMP abundance ⇄ NEON soil)", '#FFE0B2')

    # Phase 3: Model Development (Center-Right)
    add_block(65, 65, 20, 25, "Model Development\n\n- Random Forest Regressor\n- Gradient Boosting\n- Ridge Regression\n\n*Spatial Block Cross-Val\n*Target: Total Nitrogen", '#E1F5FE')

    # Phase 4: Output & Evaluation (Right)
    add_block(65, 45, 20, 12, "Model Evaluation\n\nRMSE, MAE, R2\n95% Prediction Intervals", '#F3E5F5')

    add_block(65, 25, 20, 12, "Reporting\n\nKaggle-structured\nJupyter Notebook", '#FCE4EC')

    # Flow arrows
    # EMP -> Feature Engineering
    draw_arrow(25, 82.5, 35, 82.5)
    # NEON -> Data Integration
    draw_arrow(25, 62.5, 35, 51)

    # Feature Engineering -> Data Integration
    draw_arrow(45, 65, 45, 57)

    # Data Integration -> Model Dev
    draw_arrow(55, 51, 65, 65, "Joined Matrix (X, y)")

    # Model Dev -> Evaluation
    draw_arrow(75, 65, 75, 57)

    # Evaluation -> Reporting
    draw_arrow(75, 45, 75, 37)

    plt.tight_layout()
    plt.savefig('system_architecture.png', dpi=400)
    plt.close()
    print("Architecture diagram generated as 'system_architecture.png'")

if __name__ == "__main__":
    draw_architecture()
