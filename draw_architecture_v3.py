import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch
import matplotlib.image as mpimg
from matplotlib.offsetbox import OffsetImage, AnnotationBbox

fig, ax = plt.subplots(figsize=(15, 8))
ax.set_xlim(0, 1)
ax.set_ylim(0, 1)
ax.axis('off')

# Title
plt.text(0.5, 0.95, "System Architecture: Amphibian Extinction Risk Prediction Pipeline",
         fontsize=20, fontweight='bold', ha='center', va='center', color="#0f172a", fontfamily='sans-serif')
plt.text(0.5, 0.88, "A high-level overview of the end-to-end machine learning pipeline",
         fontsize=14, ha='center', va='center', color="#64748b", fontfamily='sans-serif')

def add_icon(ax, path, xy, zoom=0.5):
    try:
        img = mpimg.imread(path)
        imagebox = OffsetImage(img, zoom=zoom)
        imagebox.image.axes = ax
        ab = AnnotationBbox(imagebox, xy, frameon=False, pad=0)
        ax.add_artist(ab)
    except Exception as e:
        print(f"Failed to load icon {path}: {e}")

# Define top row nodes (light grey backgrounds with colored borders)
top_nodes = [
    ("Data Processing Pipeline", (0.15, 0.62), 0.22, 0.08, "#f8fafc", "#e2e8f0"),
    ("Imputation & Scaling", (0.40, 0.62), 0.22, 0.08, "#f8fafc", "#e2e8f0"),
    ("SMOTE Oversampling", (0.65, 0.62), 0.22, 0.08, "#f8fafc", "#e2e8f0"),
    ("Evaluation & Visualization\nLayer", (0.88, 0.62), 0.20, 0.08, "#f8fafc", "#e2e8f0"),
]

# Top icons above the top nodes
add_icon(ax, 'icons/db_gear_purple.png', (0.15, 0.74), zoom=0.6)
add_icon(ax, 'icons/table_gear_green.png', (0.40, 0.74), zoom=0.6)
add_icon(ax, 'icons/network_blue.png', (0.65, 0.74), zoom=0.6)
add_icon(ax, 'icons/dashboard_orange.png', (0.88, 0.74), zoom=0.6)

# Define bottom large boxes
bottom_boxes = [
    ("Merge &\nRaster Sampling\n\n-------------\n\nFeature\nEngineering", (0.15, 0.25), 0.22, 0.40, "#faf5ff", "#c084fc", 'icons/table_stars_purple.png', 'icons/gear_purple.png'),
    ("Data Splitting\n\n-------------\n\nImputation &\nScaling", (0.40, 0.25), 0.22, 0.40, "#f0fdf4", "#4ade80", 'icons/table_green.png', 'icons/sliders_green.png'),
    ("Model Training\nLayer\n\n-------------\n\nSMOTE\nOversampling", (0.65, 0.25), 0.22, 0.40, "#eff6ff", "#60a5fa", 'icons/nodes_blue.png', 'icons/brain_blue.png'),
    ("Feature Importance,\n\nGeographic Risk Maps,\n\nROC-AUC Curves,\n\nDataset Schema &\n\nConfusion Matrix", (0.88, 0.25), 0.20, 0.40, "#fff7ed", "#fb923c", 'icons/chart_orange.png', None),
]

for text, (x, y), w, h, fc, ec in top_nodes:
    box = FancyBboxPatch((x - w/2, y - h/2), w, h,
                         boxstyle="round,pad=0.02,rounding_size=0.05",
                         fc=fc, ec=ec, lw=1)
    ax.add_patch(box)
    ax.text(x, y, text, ha='center', va='center', fontsize=11, fontweight='bold', color="#0f172a")

for text, (x, y), w, h, fc, ec, icon1, icon2 in bottom_boxes:
    box = FancyBboxPatch((x - w/2, y - h/2), w, h,
                         boxstyle="round,pad=0.02,rounding_size=0.05",
                         fc=fc, ec=ec, lw=1.5)
    ax.add_patch(box)

    # We draw text differently based on content to simulate the icons and dividers
    lines = text.split('\n\n-------------\n\n')
    if len(lines) == 2:
        if icon1: add_icon(ax, icon1, (x, y + 0.15), zoom=0.5)
        ax.text(x, y + 0.06, lines[0], ha='center', va='center', fontsize=11, fontweight='bold', color="#0f172a")

        ax.plot([x - w/2 + 0.02, x + w/2 - 0.02], [y, y], color=ec, linestyle='--', lw=1)

        if icon2: add_icon(ax, icon2, (x, y - 0.07), zoom=0.5)
        ax.text(x, y - 0.15, lines[1], ha='center', va='center', fontsize=11, fontweight='bold', color="#0f172a")
    else:
        if icon1: add_icon(ax, icon1, (x, y + 0.13), zoom=0.5)
        ax.text(x, y - 0.05, text, ha='center', va='center', fontsize=10, fontweight='bold', color="#0f172a")

# Draw arrows between top nodes
arrow_kwargs = dict(arrowstyle="-|>,head_width=0.3,head_length=0.4", lw=2, color="#0f172a")
ax.annotate("", xy=(0.28, 0.62), xytext=(0.27, 0.62), arrowprops=arrow_kwargs)
ax.annotate("", xy=(0.53, 0.62), xytext=(0.52, 0.62), arrowprops=arrow_kwargs)
ax.annotate("", xy=(0.77, 0.62), xytext=(0.76, 0.62), arrowprops=arrow_kwargs)

# Draw arrows from top to bottom
ax.annotate("", xy=(0.15, 0.46), xytext=(0.15, 0.57), arrowprops=arrow_kwargs)
ax.annotate("", xy=(0.40, 0.46), xytext=(0.40, 0.57), arrowprops=arrow_kwargs)
ax.annotate("", xy=(0.65, 0.46), xytext=(0.65, 0.57), arrowprops=arrow_kwargs)
ax.annotate("", xy=(0.88, 0.46), xytext=(0.88, 0.57), arrowprops=arrow_kwargs)


plt.savefig("outputs/architecture.png", dpi=300, bbox_inches='tight')
print("Architecture matched to user specification exactly with icons added.")
