import matplotlib.pyplot as plt
import matplotlib.patches as patches

# Global settings for clarity
plt.rcParams.update({
    'font.size': 11, 'axes.titlesize': 13, 'axes.labelsize': 11,
    'xtick.labelsize': 10, 'ytick.labelsize': 10, 'figure.dpi': 300, 'savefig.dpi': 300
})

def draw_rounded_rect(ax, xy, width, height, color, label):
    # Soft colors
    box = patches.FancyBboxPatch(
        xy, width, height,
        boxstyle="round,pad=0.1",
        ec="black", fc=color, lw=1.5
    )
    ax.add_patch(box)
    ax.text(xy[0] + width / 2, xy[1] + height / 2, label,
            ha='center', va='center', fontsize=12, fontweight='bold', color='black')

def main():
    fig, ax = plt.subplots(figsize=(12, 8))

    # Colors
    c_data = '#F5DEB3' # Beige/orange for integration/data
    c_process = '#A8D5BA' # Green for processing
    c_ml = '#A4C8F0' # Blue for ML
    c_eval = '#D0B0E0' # Purple for evaluation

    # Data Sources
    draw_rounded_rect(ax, (0.5, 6), 2.5, 1, c_data, "AIS Trajectories\n(Kaggle)")
    draw_rounded_rect(ax, (0.5, 4.5), 2.5, 1, c_data, "Global Bathymetry\n(GEBCO)")
    draw_rounded_rect(ax, (0.5, 3), 2.5, 1, c_data, "Validation AIS\n(NOAA)")

    # Processing
    draw_rounded_rect(ax, (4, 5.25), 2.5, 1.5, c_process, "Phase 1 & 2\nData Cleaning &\nFeature Eng.")

    # ML Models
    draw_rounded_rect(ax, (7.5, 5.25), 2.5, 1.5, c_ml, "Phase 3\nRegression Models\n(RF, XGB, MLP)")

    # Anomaly Detection
    draw_rounded_rect(ax, (4, 2.5), 2.5, 1.5, c_eval, "Phase 4\nAnomaly Framework\n(Threshold > 2*MAE)")

    # Validation & Mapping
    draw_rounded_rect(ax, (7.5, 2.5), 2.5, 1.5, c_eval, "Phase 5\nNOAA Validation\n& Folium Mapping")

    # Arrows (Simple straight arrows to avoid Bezier curve errors)
    # Data to Processing
    ax.annotate('', xy=(4, 6), xytext=(3, 6.5), arrowprops=dict(facecolor='black', width=2, headwidth=8))
    ax.annotate('', xy=(4, 5.5), xytext=(3, 5), arrowprops=dict(facecolor='black', width=2, headwidth=8))

    # NOAA to Phase 5
    ax.annotate('', xy=(7.5, 3.25), xytext=(3, 3.5), arrowprops=dict(facecolor='black', width=2, headwidth=8))

    # Processing to ML
    ax.annotate('', xy=(7.5, 6), xytext=(6.5, 6), arrowprops=dict(facecolor='black', width=2, headwidth=8))

    # ML to Anomaly Framework
    ax.annotate('', xy=(5.25, 4), xytext=(8.75, 5.25), arrowprops=dict(facecolor='black', width=2, headwidth=8))

    # Anomaly Framework to Phase 5
    ax.annotate('', xy=(7.5, 3.25), xytext=(6.5, 3.25), arrowprops=dict(facecolor='black', width=2, headwidth=8))

    # Formatting
    ax.set_xlim(0, 11)
    ax.set_ylim(1.5, 8)
    ax.axis('off')

    plt.title("Integrated Border & Maritime Security System Architecture", fontsize=16, fontweight='bold', y=0.95)
    plt.tight_layout()
    plt.savefig("system_architecture.png")
    plt.close()

if __name__ == "__main__":
    main()
