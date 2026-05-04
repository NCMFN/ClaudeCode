import matplotlib.pyplot as plt
import matplotlib.patches as patches

# Apply global settings for high-clarity, publication-quality diagrams
plt.rcParams.update({
    'font.size': 11,
    'axes.titlesize': 13,
    'axes.labelsize': 11,
    'xtick.labelsize': 10,
    'ytick.labelsize': 10,
    'figure.dpi': 300,
    'savefig.dpi': 300
})

def create_diagram():
    # Colors for standard components based on system architecture guidelines
    COLOR_DATA = '#E6CCB2'       # Beige/orange for integration/data
    COLOR_PROC = '#A5D6A7'       # Green for processing
    COLOR_ML = '#90CAF9'         # Blue for ML
    COLOR_EVAL = '#CE93D8'       # Purple for evaluation
    COLOR_TITLE = '#333333'
    COLOR_BG = '#FFFFFF'

    fig, ax = plt.subplots(figsize=(10, 8))
    ax.set_facecolor(COLOR_BG)
    fig.patch.set_facecolor(COLOR_BG)

    # Hide axes
    ax.set_xlim(0, 10)
    ax.set_ylim(0, 10)
    ax.axis('off')

    # Title and Subtitle
    plt.text(5, 9.5, "SYSTEM ARCHITECTURE: ENVIRONMENTAL HEALTH\nIMPACT PREDICTOR PIPELINE",
             ha='center', va='center', fontweight='bold', fontsize=14, color=COLOR_TITLE)
    plt.text(5, 8.8, "A high-level overview of the end-to-end data processing and machine learning workflow.",
             ha='center', va='center', fontsize=11, color=COLOR_TITLE, style='italic')

    # Draw rounded rectangles helper
    def draw_box(x, y, width, height, text, color, text_color='black', fontsize=11, fontweight='normal'):
        box = patches.FancyBboxPatch((x, y), width, height,
                                     boxstyle="round,pad=0.2",
                                     edgecolor='black', facecolor=color, lw=1.5)
        ax.add_patch(box)
        plt.text(x + width/2, y + height/2, text,
                 ha='center', va='center', fontsize=fontsize, color=text_color, fontweight=fontweight)

    # 1. OpenAQ API and ERA5 Weather
    draw_box(1, 6.5, 2.5, 1, "OpenAQ API\nPM2.5, NO2, O3\n(fetch_openaq.py)", COLOR_DATA)
    draw_box(4, 6.5, 2.0, 1, "ERA5 Weather\n(fetch_weather.py)", COLOR_DATA)
    draw_box(6.5, 6.5, 2.5, 1, "Cardiac Events\nER Admissions\n(fetch_health.py)", COLOR_DATA)

    # 2. Alignment & Features
    draw_box(3.5, 4.5, 3.0, 1, "ALIGNMENT & FEATURES\nSpatial-Temporal Join\nPollution-Heat Index (PHI)\n(features.py)", COLOR_PROC, fontweight='bold')

    # 3. Machine Learning Models
    draw_box(1.5, 2.5, 3.0, 1, "OLS Baseline\nLinear Regression\n(train.py)", COLOR_ML)
    draw_box(5.5, 2.5, 3.0, 1, "XGBoost & Optuna\n(train.py)", COLOR_ML)

    # 4. Evaluation & Output
    draw_box(2.5, 0.5, 5.0, 1.2, "EVALUATION & OUTPUT\nMetrics (R², RMSE)\nSHAP Feature Importance\nAlert Simulation\n(evaluate.py)", COLOR_EVAL, fontweight='bold')

    # Arrows helper
    def draw_arrow(x1, y1, x2, y2):
        ax.annotate('', xy=(x2, y2), xytext=(x1, y1),
                    arrowprops=dict(arrowstyle="->", color="black", lw=2.0))

    # Data to Processing
    draw_arrow(2.25, 6.4, 4.0, 5.6)
    draw_arrow(5.0, 6.4, 5.0, 5.6)
    draw_arrow(7.75, 6.4, 6.0, 5.6)

    # Processing to Models
    draw_arrow(4.5, 4.4, 3.0, 3.6)
    draw_arrow(5.5, 4.4, 7.0, 3.6)

    # Models to Evaluation
    draw_arrow(3.0, 2.4, 4.0, 1.8)
    draw_arrow(7.0, 2.4, 6.0, 1.8)

    plt.tight_layout()
    plt.savefig("architecture.png", format='png', bbox_inches='tight')
    plt.close()

if __name__ == "__main__":
    create_diagram()
