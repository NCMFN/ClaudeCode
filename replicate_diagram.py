import matplotlib.pyplot as plt
import matplotlib.patches as patches

# Global settings as per memory
plt.rcParams.update({
    'font.size': 11,
    'axes.titlesize': 13,
    'axes.labelsize': 11,
    'xtick.labelsize': 10,
    'ytick.labelsize': 10,
    'figure.dpi': 300,
    'savefig.dpi': 300
})

fig, ax = plt.subplots(figsize=(14, 8))
ax.set_xlim(0, 14)
ax.set_ylim(0, 8)
ax.axis('off')

# Ensure white background
fig.patch.set_facecolor('white')
ax.set_facecolor('white')

# Define specific colors according to memory conventions
# Blue for ML, Green for processing, Purple for evaluation, Beige/orange for integration
colors = {
    'processing': '#D5E8D4', # Light green
    'ml': '#DAE8FC',         # Light blue
    'evaluation': '#E1D5E7', # Light purple
    'integration': '#FFE6CC' # Beige/Orange
}

edge_colors = {
    'processing': '#82B366',
    'ml': '#6C8EBF',
    'evaluation': '#9673A6',
    'integration': '#D79B00'
}

def draw_box(x, y, w, h, text, color_type, fontsize=11):
    box = patches.FancyBboxPatch((x, y), w, h,
                                 boxstyle="round,pad=0.1,rounding_size=0.15",
                                 facecolor=colors[color_type],
                                 edgecolor=edge_colors[color_type],
                                 linewidth=2)
    ax.add_patch(box)
    ax.text(x + w/2, y + h/2, text, ha='center', va='center', fontsize=fontsize, fontweight='bold', wrap=True)

def draw_arrow(x1, y1, x2, y2):
    ax.annotate("", xy=(x2, y2), xytext=(x1, y1),
                arrowprops=dict(arrowstyle="->", color="black", lw=2, shrinkA=0, shrinkB=0))

# Title extracted from image OCR
ax.text(7, 7.5, "System Architecture: Heart & Mind CVD Risk Predictor Pipeline",
        ha='center', va='center', fontsize=16, fontweight='bold')
ax.text(7, 7.1, "A high-level overview of the end-to-end CVD risk predictor machine learning pipeline",
        ha='center', va='center', fontsize=12, style='italic')

w, h = 2.6, 1.2

# Level 1: Data Acquisition -> Feature Engineering -> Model Development -> Evaluation
y_top = 5.0
draw_box(0.5, y_top, w, h, "Data Acquisition &\nPreparation Pipeline", 'processing')
draw_box(4.0, y_top, w, h, "Feature Engineering &\nImputation", 'processing')
draw_box(7.5, y_top, w, h, "Model Development &\nOptimization", 'ml')
draw_box(11.0, y_top, w, h, "Evaluation &\nOutput Layer", 'evaluation')

# Arrows connecting Level 1
draw_arrow(3.1, y_top+0.6, 4.0, y_top+0.6)
draw_arrow(6.6, y_top+0.6, 7.5, y_top+0.6)
draw_arrow(10.1, y_top+0.6, 11.0, y_top+0.6)

# Sub-components branching from Model Development & Evaluation
y_mid = 3.0
draw_box(7.5, y_mid, w, h, "Model Training\n(RF, XGBoost,\nOptuna Tuning)", 'ml')
draw_box(11.0, y_mid, w, h, "Outputs\n(Models, Metrics,\nSHAP Plots)", 'integration')

# Arrows connecting to sub-components
draw_arrow(8.8, y_top, 8.8, y_mid+h)
draw_arrow(12.3, y_top, 12.3, y_mid+h)

# Additional XGBoost Evaluation box branching from Model Training
y_low = 1.0
draw_box(9.25, y_low, w+1.0, h, "XGBoost Evaluation &\nSHAP Analysis", 'evaluation')

# Arrows to and from XGBoost box
draw_arrow(8.8, y_mid, 8.8, y_low+h)
draw_arrow(10.25, y_low+h, 12.3, y_mid)

plt.tight_layout()
plt.savefig('architecture_diagram.png', bbox_inches='tight')
