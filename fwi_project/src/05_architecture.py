import matplotlib.pyplot as plt
import matplotlib.patches as patches
import os

OUTPUT_DIR = os.path.join(os.path.dirname(__file__), '..', 'outputs')

def draw_architecture():
    print("Designing system architecture diagram...")
    fig, ax = plt.subplots(figsize=(12, 8), dpi=400)
    ax.axis('off')

    # Define styles
    box_style = "round,pad=0.3"

    def add_box(ax, x, y, width, height, text, color):
        p = patches.FancyBboxPatch(
            (x, y), width, height, boxstyle=box_style,
            ec="black", fc=color, lw=2.5
        )
        ax.add_patch(p)
        ax.text(x + width/2, y + height/2, text, ha='center', va='center',
                fontsize=11, fontweight='bold', wrap=True)

    def add_arrow(ax, x_start, y_start, x_end, y_end):
        ax.annotate("", xy=(x_end, y_end), xycoords='data',
                    xytext=(x_start, y_start), textcoords='data',
                    arrowprops=dict(arrowstyle="->", color="black", lw=2.5))

    def add_feedback_arrow(ax, x_start, y_start, x_end, y_end):
        ax.annotate("", xy=(x_end, y_end), xycoords='data',
                    xytext=(x_start, y_start), textcoords='data',
                    arrowprops=dict(arrowstyle="->", color="gray", lw=2.5, ls='dashed'))

    # Layer 1: Data Sources
    add_box(ax, 0.1, 0.8, 0.2, 0.1, "gridMET (OPeNDAP)\nMeteorology\n(Temp, RH, Wind, Precip)", "#D0E8F2")
    add_box(ax, 0.4, 0.8, 0.2, 0.1, "MTBS / FAMWEB\nHistorical Fire\nPerimeters", "#D0E8F2")

    # Layer 2: Preprocessing
    add_box(ax, 0.25, 0.6, 0.2, 0.1, "Feature Engineering\n(KBDI proxy, RH deficit,\nWind shear proxy)", "#FAD02C")

    # Layer 3: Modeling
    add_box(ax, 0.1, 0.4, 0.2, 0.1, "XGBoost Regressor\nFWI Prediction", "#FFAEBC")
    add_box(ax, 0.4, 0.4, 0.2, 0.1, "Random Forest / LR\nBaselines", "#E8C1D6")

    # Layer 4: Outputs
    add_box(ax, 0.1, 0.2, 0.2, 0.1, "Geospatial Heatmap\n(Cartopy)", "#A0E8AF")
    add_box(ax, 0.4, 0.2, 0.2, 0.1, "SHAP Feature\nImportance", "#A0E8AF")
    add_box(ax, 0.7, 0.2, 0.2, 0.1, "Validation\n(Blow-up Hits)", "#A0E8AF")

    # Arrows Data -> Preprocess
    add_arrow(ax, 0.2, 0.8, 0.35, 0.7)
    add_arrow(ax, 0.5, 0.8, 0.35, 0.7)

    # Arrows Preprocess -> Modeling
    add_arrow(ax, 0.35, 0.6, 0.2, 0.5)
    add_arrow(ax, 0.35, 0.6, 0.5, 0.5)

    # Arrows Modeling -> Outputs
    add_arrow(ax, 0.2, 0.4, 0.2, 0.3)
    add_arrow(ax, 0.2, 0.4, 0.5, 0.3)
    add_arrow(ax, 0.2, 0.4, 0.8, 0.3)

    # Feedback loop
    add_feedback_arrow(ax, 0.8, 0.3, 0.5, 0.5)

    plt.title("FWI Prediction System Architecture", fontsize=16, fontweight='bold', pad=20)
    plt.xlim(0, 1)
    plt.ylim(0, 1)

    out_path = os.path.join(OUTPUT_DIR, "system_architecture.png")
    plt.savefig(out_path, dpi=400, bbox_inches='tight')
    plt.close()
    print(f"Saved system architecture diagram to {out_path}")

if __name__ == "__main__":
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    draw_architecture()
