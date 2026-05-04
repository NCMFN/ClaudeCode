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

def draw_db_icon(ax, xy, color):
    # stacked ellipses
    x, y = xy
    w, h = 1.0, 0.3
    for i in range(3):
        e = Ellipse((x, y + i*0.25), w, h, ec=color, fc='none', lw=2)
        ax.add_patch(e)
        if i < 2:
            ax.plot([x-w/2, x-w/2], [y+i*0.25, y+(i+1)*0.25], color=color, lw=2)
            ax.plot([x+w/2, x+w/2], [y+i*0.25, y+(i+1)*0.25], color=color, lw=2)

def draw_grid_icon(ax, xy, color):
    x, y = xy
    w, h = 0.8, 0.8
    r = Rectangle((x-w/2, y-h/2), w, h, ec=color, fc='none', lw=2)
    ax.add_patch(r)
    ax.plot([x-w/2, x+w/2], [y-h/6, y-h/6], color=color, lw=2)
    ax.plot([x-w/2, x+w/2], [y+h/6, y+h/6], color=color, lw=2)
    ax.plot([x-w/6, x-w/6], [y-h/2, y+h/2], color=color, lw=2)
    ax.plot([x+w/6, x+w/6], [y-h/2, y+h/2], color=color, lw=2)

def draw_brain_icon(ax, xy, color):
    x, y = xy
    c1 = Ellipse((x-0.2, y), 0.5, 0.6, ec=color, fc='none', lw=2)
    c2 = Ellipse((x+0.2, y), 0.5, 0.6, ec=color, fc='none', lw=2)
    ax.add_patch(c1)
    ax.add_patch(c2)
    ax.plot([x, x], [y-0.2, y+0.2], color=color, lw=2)

def draw_chart_icon(ax, xy, color):
    x, y = xy
    ax.plot([x-0.4, x-0.4, x+0.4], [y+0.4, y-0.4, y-0.4], color=color, lw=2)
    ax.plot([x-0.3, x-0.1, x+0.1, x+0.3], [y-0.2, y+0.1, y-0.1, y+0.3], color=color, lw=2, marker='o', markersize=3)

def create_architecture():
    plt.rcParams.update({'font.size': 11, 'axes.titlesize': 13, 'axes.labelsize': 11,
                         'xtick.labelsize': 10, 'ytick.labelsize': 10,
                         'figure.dpi': 300, 'savefig.dpi': 300,
                         'font.family': 'sans-serif'})

    fig, ax = plt.subplots(figsize=(16, 9))
    ax.set_xlim(0, 16)
    ax.set_ylim(0, 9)
    ax.axis('off')

    # Colors (mimicking the image)
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
    ax.text(8, 8.1, "A high-level overview of the end-to-end machine learning pipeline",
            ha='center', va='center', fontsize=14, color='#64748B')

    # Columns x-coordinates
    xs = [2.5, 6.16, 9.83, 13.5]

    # 1. Top Icons
    draw_db_icon(ax, (xs[0], 7.0), c_purp)
    draw_grid_icon(ax, (xs[1], 7.0), c_green)
    draw_brain_icon(ax, (xs[2], 7.0), c_blue)
    draw_chart_icon(ax, (xs[3], 7.0), c_orange)

    # 2. Top Pills
    pill_y = 5.8
    pill_w = 3.2
    pill_h = 0.8
    add_pill(ax, (xs[0], pill_y), pill_w, pill_h, "Data Ingestion Pipeline", c_purp, c_bg)
    add_pill(ax, (xs[1], pill_y), pill_w, pill_h, "Alignment & Features", c_green, c_bg)
    add_pill(ax, (xs[2], pill_y), pill_w, pill_h, "Model Training Layer", c_blue, c_bg)
    add_pill(ax, (xs[3], pill_y), pill_w, pill_h, "Evaluation & Output", c_orange, c_bg)

    # Top Arrows (Horizontal)
    draw_arrow(ax, (xs[0]+pill_w/2 + 0.1, pill_y), (xs[1]-pill_w/2 - 0.1, pill_y))
    draw_arrow(ax, (xs[1]+pill_w/2 + 0.1, pill_y), (xs[2]-pill_w/2 - 0.1, pill_y))
    draw_arrow(ax, (xs[2]+pill_w/2 + 0.1, pill_y), (xs[3]-pill_w/2 - 0.1, pill_y))

    # Vertical Arrows
    box_top = 4.5
    for x in xs:
        draw_arrow(ax, (x, pill_y - pill_h/2 - 0.1), (x, box_top + 0.1))

    # 3. Bottom Large Boxes
    box_y = 2.4
    box_w = 3.4
    box_h = 4.2
    add_large_box(ax, (xs[0], box_y), box_w, box_h, c_purp, c_purp_light)
    add_large_box(ax, (xs[1], box_y), box_w, box_h, c_green, c_green_light)
    add_large_box(ax, (xs[2], box_y), box_w, box_h, c_blue, c_blue_light)
    add_large_box(ax, (xs[3], box_y), box_w, box_h, c_orange, c_orange_light)

    # 4. Box Contents
    # Box 1: Data
    draw_db_icon(ax, (xs[0], 3.8), c_purp)
    ax.text(xs[0], 3.2, "OpenAQ Data\n(PM2.5, NO2, O3)", ha='center', va='center', fontweight='bold', fontsize=10)
    ax.plot([xs[0]-1, xs[0]+1], [2.7, 2.7], color=c_purp, ls='--', lw=1, alpha=0.5)
    draw_db_icon(ax, (xs[0], 2.2), c_purp)
    ax.text(xs[0], 1.6, "ERA5 Weather\n(Temp, Humidity, Wind)", ha='center', va='center', fontweight='bold', fontsize=10)
    ax.text(xs[0], 0.8, "Cardiac ER Data\n(MIMIC-IV / CDC)", ha='center', va='center', fontweight='bold', fontsize=10)

    # Box 2: Alignment & Features
    draw_grid_icon(ax, (xs[1], 3.8), c_green)
    ax.text(xs[1], 3.2, "Spatial-Temporal Join", ha='center', va='center', fontweight='bold', fontsize=10)
    ax.text(xs[1], 2.7, "Interpolation & Lags", ha='center', va='center', fontweight='bold', fontsize=10)
    ax.plot([xs[1]-1, xs[1]+1], [2.3, 2.3], color=c_green, ls='--', lw=1, alpha=0.5)
    ax.text(xs[1], 1.8, "PHI Formulation", ha='center', va='center', fontweight='bold', fontsize=10)
    ax.text(xs[1], 1.3, "Seasonal Z-Scores", ha='center', va='center', fontweight='bold', fontsize=10)
    ax.text(xs[1], 0.8, "Heatwave Flags", ha='center', va='center', fontweight='bold', fontsize=10)

    # Box 3: Model Training
    draw_brain_icon(ax, (xs[2], 3.8), c_blue)
    ax.text(xs[2], 3.2, "Linear OLS Baseline", ha='center', va='center', fontweight='bold', fontsize=10)
    ax.text(xs[2], 2.7, "OLS w/ Separated Features", ha='center', va='center', fontweight='bold', fontsize=10)
    ax.plot([xs[2]-1, xs[2]+1], [2.3, 2.3], color=c_blue, ls='--', lw=1, alpha=0.5)
    draw_brain_icon(ax, (xs[2], 1.8), c_blue)
    ax.text(xs[2], 1.2, "XGBoost Regressors\n(Optuna Tuning)", ha='center', va='center', fontweight='bold', fontsize=10)
    ax.text(xs[2], 0.6, "TimeSeries CV Split", ha='center', va='center', fontweight='bold', fontsize=10)

    # Box 4: Evaluation
    draw_chart_icon(ax, (xs[3], 3.8), c_orange)
    ax.text(xs[3], 3.0, "Model Comparison\n(R², RMSE, MAE)", ha='center', va='center', fontweight='bold', fontsize=10)
    ax.text(xs[3], 2.2, "SHAP Explainability\n(Feature & Interaction)", ha='center', va='center', fontweight='bold', fontsize=10)
    ax.text(xs[3], 1.4, "PHI Alert Thresholds\n(Alert Simulation)", ha='center', va='center', fontweight='bold', fontsize=10)
    ax.text(xs[3], 0.6, "Performance Curves", ha='center', va='center', fontweight='bold', fontsize=10)

    plt.tight_layout()
    plt.savefig('SYSTEM ARCHITECTURE.PNG', bbox_inches='tight')

if __name__ == "__main__":
    create_architecture()
