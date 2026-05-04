import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch
import matplotlib.patches as patches

def draw_rounded_rect(ax, xy, width, height, text, facecolor, edgecolor, title_size=12, text_size=10, details=None):
    # Create main box
    box = FancyBboxPatch(xy, width, height,
                         boxstyle="round,pad=0.1",
                         fc=facecolor, ec=edgecolor, lw=2)
    ax.add_patch(box)

    # Add title
    ax.text(xy[0] + width/2, xy[1] + height - 0.3, text,
            ha='center', va='center', fontweight='bold', fontsize=title_size)

    # Add details if any
    if details:
        for i, detail in enumerate(details):
            ax.text(xy[0] + width/2, xy[1] + height - 0.7 - i*0.3, detail,
                    ha='center', va='center', fontsize=text_size)
    return box

def create_architecture():
    # Setup global plot styling based on memory requirements
    plt.rcParams.update({'font.size': 11, 'axes.titlesize': 13, 'axes.labelsize': 11,
                         'xtick.labelsize': 10, 'ytick.labelsize': 10,
                         'figure.dpi': 300, 'savefig.dpi': 300})

    fig, ax = plt.subplots(figsize=(14, 10))
    ax.set_xlim(0, 14)
    ax.set_ylim(0, 10)
    ax.axis('off')

    # Colors
    c_source = '#E8F4F8' # Light blue
    c_edge = '#1F3864'   # Navy
    c_process = '#F4F1DE' # Off white/beige
    c_edge_proc = '#BA7517' # Bronze
    c_model = '#E8F5E9'  # Light green
    c_edge_model = '#1D9E75' # Green
    c_output = '#FFF3E0' # Light orange
    c_edge_out = '#993C1D' # Rust

    # 1. Data Sources (Top row)
    draw_rounded_rect(ax, (1, 7.5), 3, 1.5, "Air Quality Data", c_source, c_edge,
                      details=["OpenAQ v3 API", "PM2.5, NO2, O3", "(fetch_openaq.py)"])

    draw_rounded_rect(ax, (5.5, 7.5), 3, 1.5, "Meteorological Data", c_source, c_edge,
                      details=["Copernicus CDS (ERA5)", "Temp, Humidity, Wind", "(fetch_era5.py)"])

    draw_rounded_rect(ax, (10, 7.5), 3, 1.5, "Health Data", c_source, c_edge,
                      details=["MIMIC-IV / CDC", "Cardiac ER Admissions", "(fetch_health.py)"])

    # 2. Processing (Middle row)
    draw_rounded_rect(ax, (3.25, 4.5), 3, 1.5, "Data Alignment", c_process, c_edge_proc,
                      details=["Spatial & Temporal Join", "Interpolation, Lags", "(align.py)"])

    draw_rounded_rect(ax, (7.75, 4.5), 3, 1.5, "Feature Engineering", c_process, c_edge_proc,
                      details=["PHI Formulation", "Z-Scores, Heatwaves", "(features.py)"])

    # 3. Modeling & Evaluation (Bottom row)
    draw_rounded_rect(ax, (2, 1), 3.5, 2, "Model Training", c_model, c_edge_model,
                      details=["Linear OLS Baseline", "XGBoost Regressors", "Optuna Tuning", "TimeSeries CV", "(train.py)"])

    draw_rounded_rect(ax, (8.5, 1), 3.5, 2, "Evaluation & Output", c_output, c_edge_out,
                      details=["R², RMSE, MAE", "SHAP Explainability", "Alert Thresholds", "Output Metrics & Plots", "(evaluate.py)"])

    # Draw arrows
    # Source to Alignment
    ax.annotate("", xy=(4.75, 6), xytext=(2.5, 7.5), arrowprops=dict(arrowstyle="->", lw=2, color=c_edge))
    ax.annotate("", xy=(4.75, 6), xytext=(7, 7.5), arrowprops=dict(arrowstyle="->", lw=2, color=c_edge))
    ax.annotate("", xy=(4.75, 6), xytext=(11.5, 7.5), arrowprops=dict(arrowstyle="->", lw=2, color=c_edge))

    # Alignment to Features
    ax.annotate("", xy=(7.75, 5.25), xytext=(6.25, 5.25), arrowprops=dict(arrowstyle="->", lw=2, color=c_edge_proc))

    # Features to Model
    ax.annotate("", xy=(3.75, 3), xytext=(9.25, 4.5), arrowprops=dict(arrowstyle="->", lw=2, color=c_edge_proc))

    # Model to Eval
    ax.annotate("", xy=(8.5, 2), xytext=(5.5, 2), arrowprops=dict(arrowstyle="->", lw=2, color=c_edge_model))

    plt.title("System Architecture: Pollution-Heat Index ML Pipeline", fontsize=16, fontweight='bold', pad=20)
    plt.tight_layout()
    plt.savefig('SYSTEM ARCHITECTURE.PNG')

if __name__ == "__main__":
    create_architecture()
