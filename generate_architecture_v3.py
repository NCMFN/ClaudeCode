import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, Ellipse, Rectangle, PathPatch
from matplotlib.path import Path
import matplotlib.patches as patches

def add_pill(ax, xy, width, height, text, edgecolor, fillcolor):
    box = FancyBboxPatch((xy[0]-width/2, xy[1]-height/2), width, height,
                         boxstyle="round,pad=0.2,rounding_size=0.5",
                         fc=fillcolor, ec=edgecolor, lw=1.5)
    ax.add_patch(box)
    ax.text(xy[0], xy[1], text, ha='center', va='center', fontsize=11, fontweight='bold', color='black')

def add_large_box(ax, xy, width, height, edgecolor, fillcolor):
    box = FancyBboxPatch((xy[0]-width/2, xy[1]-height/2), width, height,
                         boxstyle="round,pad=0.2,rounding_size=0.8",
                         fc=fillcolor, ec=edgecolor, lw=1.5)
    ax.add_patch(box)

def draw_arrow(ax, xy_from, xy_to):
    ax.annotate("", xy=xy_to, xytext=xy_from,
                arrowprops=dict(arrowstyle="-|>,head_width=0.15,head_length=0.3", lw=1.5, color="black"))

def create_architecture():
    plt.rcParams.update({'font.size': 11, 'axes.titlesize': 13, 'axes.labelsize': 11,
                         'xtick.labelsize': 10, 'ytick.labelsize': 10,
                         'figure.dpi': 300, 'savefig.dpi': 300,
                         'font.family': 'sans-serif'})

    fig, ax = plt.subplots(figsize=(16, 9))
    ax.set_xlim(0, 16)
    ax.set_ylim(0, 9)
    ax.axis('off')

    # Colors
    c_purp = '#A855F7'
    c_purp_light = '#FAF5FF'
    c_green = '#22C55E'
    c_green_light = '#F0FDF4'
    c_blue = '#3B82F6'
    c_blue_light = '#EFF6FF'
    c_orange = '#F97316'
    c_orange_light = '#FFF7ED'
    c_bg = '#F8FAFC'

    # Title
    ax.text(8, 8.5, "System Architecture: Pollution-Heat Index ML Pipeline",
            ha='center', va='center', fontsize=20, fontweight='bold', color='#0F172A')
    ax.text(8, 8.1, "phi_cardiac/ complete pipeline representation",
            ha='center', va='center', fontsize=14, color='#64748B')

    # Columns x-coordinates
    xs = [2.5, 6.16, 9.83, 13.5]

    # 2. Top Pills
    pill_y = 7.0
    pill_w = 3.2
    pill_h = 0.8
    add_pill(ax, (xs[0], pill_y), pill_w, pill_h, "Data Ingestion", c_purp, c_bg)
    add_pill(ax, (xs[1], pill_y), pill_w, pill_h, "Alignment & Features", c_green, c_bg)
    add_pill(ax, (xs[2], pill_y), pill_w, pill_h, "Model Training", c_blue, c_bg)
    add_pill(ax, (xs[3], pill_y), pill_w, pill_h, "Evaluation", c_orange, c_bg)

    # Top Arrows (Horizontal)
    draw_arrow(ax, (xs[0]+pill_w/2 + 0.1, pill_y), (xs[1]-pill_w/2 - 0.1, pill_y))
    draw_arrow(ax, (xs[1]+pill_w/2 + 0.1, pill_y), (xs[2]-pill_w/2 - 0.1, pill_y))
    draw_arrow(ax, (xs[2]+pill_w/2 + 0.1, pill_y), (xs[3]-pill_w/2 - 0.1, pill_y))

    # Vertical Arrows
    box_top = 5.8
    for x in xs:
        draw_arrow(ax, (x, pill_y - pill_h/2 - 0.1), (x, box_top + 0.1))

    # 3. Bottom Large Boxes
    box_y = 3.0
    box_w = 3.4
    box_h = 5.4
    add_large_box(ax, (xs[0], box_y), box_w, box_h, c_purp, c_purp_light)
    add_large_box(ax, (xs[1], box_y), box_w, box_h, c_green, c_green_light)
    add_large_box(ax, (xs[2], box_y), box_w, box_h, c_blue, c_blue_light)
    add_large_box(ax, (xs[3], box_y), box_w, box_h, c_orange, c_orange_light)

    # 4. Box Contents
    # Box 1: Data Ingestion
    ax.text(xs[0], 5.3, "fetch_openaq.py", ha='center', va='center', fontweight='bold', fontsize=11, color='#1E293B')
    ax.text(xs[0], 4.9, "• API query PM2.5, NO2, O3\n• Raw CSVs per city", ha='center', va='center', fontsize=9)
    ax.plot([xs[0]-1.5, xs[0]+1.5], [4.4, 4.4], color=c_purp, ls='--', lw=1, alpha=0.5)

    ax.text(xs[0], 3.9, "fetch_era5.py", ha='center', va='center', fontweight='bold', fontsize=11, color='#1E293B')
    ax.text(xs[0], 3.4, "• cdsapi netCDF fetch\n• Temp, RH, Wind Speed\n• Feels Like Temp calc", ha='center', va='center', fontsize=9)
    ax.plot([xs[0]-1.5, xs[0]+1.5], [2.8, 2.8], color=c_purp, ls='--', lw=1, alpha=0.5)

    ax.text(xs[0], 2.3, "fetch_health.py", ha='center', va='center', fontweight='bold', fontsize=11, color='#1E293B')
    ax.text(xs[0], 1.8, "• Target Variable Data\n• Cardiac ER Admissions", ha='center', va='center', fontsize=9)

    # Box 2: Alignment & Features
    ax.text(xs[1], 5.3, "align.py", ha='center', va='center', fontweight='bold', fontsize=11, color='#1E293B')
    ax.text(xs[1], 4.7, "• Spatial-Temporal Left Join\n• 24h, 48h, 72h Lags\n• Seasonal Z-Scores\n• Missing Data Imputation", ha='center', va='center', fontsize=9)
    ax.plot([xs[1]-1.5, xs[1]+1.5], [4.0, 4.0], color=c_green, ls='--', lw=1, alpha=0.5)

    ax.text(xs[1], 3.5, "features.py", ha='center', va='center', fontweight='bold', fontsize=11, color='#1E293B')
    ax.text(xs[1], 2.6, "• PHI Formulation\n  (PM2.5 × Temp Interaction)\n• Heatwave & Day Flags\n• 3-day Rolling Means\n• Strict Temporal Split\n• log1p Target Transform", ha='center', va='center', fontsize=9)

    # Box 3: Model Training
    ax.text(xs[2], 5.3, "train.py", ha='center', va='center', fontweight='bold', fontsize=11, color='#1E293B')
    ax.text(xs[2], 4.5, "Model Architecture", ha='center', va='center', fontweight='bold', fontsize=10, color='#475569')
    ax.text(xs[2], 3.9, "• M1: OLS Baseline (Temp)\n• M2: OLS Separated\n• M3: XGBoost (All + PHI)\n• M4: XGBoost (Lags only)", ha='center', va='center', fontsize=9)
    ax.plot([xs[2]-1.5, xs[2]+1.5], [3.3, 3.3], color=c_blue, ls='--', lw=1, alpha=0.5)

    ax.text(xs[2], 2.8, "Optimization", ha='center', va='center', fontweight='bold', fontsize=10, color='#475569')
    ax.text(xs[2], 2.1, "• Optuna (50 Trials)\n• TimeSeriesSplit CV (k=5)\n• Output: xgb_phi_best.joblib", ha='center', va='center', fontsize=9)

    # Box 4: Evaluation
    ax.text(xs[3], 5.3, "evaluate.py", ha='center', va='center', fontweight='bold', fontsize=11, color='#1E293B')
    ax.text(xs[3], 4.7, "Metrics", ha='center', va='center', fontweight='bold', fontsize=10, color='#475569')
    ax.text(xs[3], 4.2, "• Inverse-transformed RMSE\n• R² Comparison Chart\n• MAE per model", ha='center', va='center', fontsize=9)
    ax.plot([xs[3]-1.5, xs[3]+1.5], [3.7, 3.7], color=c_orange, ls='--', lw=1, alpha=0.5)

    ax.text(xs[3], 3.2, "Explainability", ha='center', va='center', fontweight='bold', fontsize=10, color='#475569')
    ax.text(xs[3], 2.7, "• SHAP Feature Importance\n• PHI Interaction Plots", ha='center', va='center', fontsize=9)
    ax.plot([xs[3]-1.5, xs[3]+1.5], [2.2, 2.2], color=c_orange, ls='--', lw=1, alpha=0.5)

    ax.text(xs[3], 1.7, "Actionability", ha='center', va='center', fontweight='bold', fontsize=10, color='#475569')
    ax.text(xs[3], 1.0, "• PHI Alert Simulation (>95th)\n• Alert Performance Curve\n  (Precision/Recall/Lead Time)", ha='center', va='center', fontsize=9)

    plt.tight_layout()
    plt.savefig('SYSTEM ARCHITECTURE.PNG', bbox_inches='tight')

if __name__ == "__main__":
    create_architecture()
