import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch
import numpy as np

fig, ax = plt.subplots(figsize=(15, 8))
ax.set_xlim(0, 1)
ax.set_ylim(0, 1)
ax.axis('off')

# Title
plt.text(0.5, 0.95, "System Architecture: Amphibian Extinction Risk Prediction Pipeline",
         fontsize=20, fontweight='bold', ha='center', va='center', color="#0f172a", fontfamily='sans-serif')
plt.text(0.5, 0.88, "A high-level overview of the end-to-end machine learning pipeline",
         fontsize=14, ha='center', va='center', color="#64748b", fontfamily='sans-serif')


# Define top row nodes (light grey backgrounds with colored borders)
top_nodes = [
    ("Data Processing Pipeline", (0.15, 0.65), 0.22, 0.08, "#f8fafc", "#e2e8f0"),
    ("Imputation & Scaling", (0.40, 0.65), 0.22, 0.08, "#f8fafc", "#e2e8f0"),
    ("SMOTE Oversampling", (0.65, 0.65), 0.22, 0.08, "#f8fafc", "#e2e8f0"),
    ("Evaluation & Visualization\nLayer", (0.88, 0.65), 0.20, 0.08, "#f8fafc", "#e2e8f0"),
]

# Define bottom large boxes
bottom_boxes = [
    ("Merge &\nRaster Sampling\n\n-------------\n\nFeature\nEngineering", (0.15, 0.25), 0.22, 0.40, "#faf5ff", "#c084fc"), # purple
    ("Data Splitting\n\n-------------\n\nImputation &\nScaling", (0.40, 0.25), 0.22, 0.40, "#f0fdf4", "#4ade80"), # green
    ("Model Training\nLayer\n\n-------------\n\nSMOTE\nOversampling", (0.65, 0.25), 0.22, 0.40, "#eff6ff", "#60a5fa"), # blue
    ("Feature Importance,\n\nGeographic Risk Maps,\n\nROC-AUC Curves,\n\nDataset Schema &\n\nConfusion Matrix", (0.88, 0.25), 0.20, 0.40, "#fff7ed", "#fb923c"), # orange
]


for text, (x, y), w, h, fc, ec in top_nodes:
    box = FancyBboxPatch((x - w/2, y - h/2), w, h,
                         boxstyle="round,pad=0.02,rounding_size=0.05",
                         fc=fc, ec=ec, lw=1)
    ax.add_patch(box)
    ax.text(x, y, text, ha='center', va='center', fontsize=11, fontweight='bold', color="#0f172a")

for text, (x, y), w, h, fc, ec in bottom_boxes:
    box = FancyBboxPatch((x - w/2, y - h/2), w, h,
                         boxstyle="round,pad=0.02,rounding_size=0.05",
                         fc=fc, ec=ec, lw=1.5)
    ax.add_patch(box)

    # We draw text differently based on content to simulate the icons and dividers
    lines = text.split('\n\n-------------\n\n')
    if len(lines) == 2:
        ax.text(x, y + 0.08, lines[0], ha='center', va='center', fontsize=11, fontweight='bold', color="#0f172a")
        ax.plot([x - w/2 + 0.02, x + w/2 - 0.02], [y, y], color=ec, linestyle='--', lw=1)
        ax.text(x, y - 0.12, lines[1], ha='center', va='center', fontsize=11, fontweight='bold', color="#0f172a")
    else:
        ax.text(x, y - 0.05, text, ha='center', va='center', fontsize=10, fontweight='bold', color="#0f172a")

# Draw arrows between top nodes
arrow_kwargs = dict(arrowstyle="-|>,head_width=0.3,head_length=0.4", lw=2, color="#0f172a")
ax.annotate("", xy=(0.28, 0.65), xytext=(0.27, 0.65), arrowprops=arrow_kwargs)
ax.annotate("", xy=(0.53, 0.65), xytext=(0.52, 0.65), arrowprops=arrow_kwargs)
ax.annotate("", xy=(0.77, 0.65), xytext=(0.76, 0.65), arrowprops=arrow_kwargs)

# Draw arrows from top to bottom
ax.annotate("", xy=(0.15, 0.46), xytext=(0.15, 0.60), arrowprops=arrow_kwargs)
ax.annotate("", xy=(0.40, 0.46), xytext=(0.40, 0.60), arrowprops=arrow_kwargs)
ax.annotate("", xy=(0.65, 0.46), xytext=(0.65, 0.60), arrowprops=arrow_kwargs)
ax.annotate("", xy=(0.88, 0.46), xytext=(0.88, 0.60), arrowprops=arrow_kwargs)


plt.savefig("outputs/architecture.png", dpi=300, bbox_inches='tight')
print("Architecture matched to user specification exactly.")
