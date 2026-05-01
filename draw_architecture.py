import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch

fig, ax = plt.subplots(figsize=(12, 10))
ax.set_xlim(0, 1)
ax.set_ylim(0, 1)
ax.axis('off')

# Title
plt.text(0.5, 0.95, "System Architecture: Amphibian Extinction Risk Prediction Pipeline",
         fontsize=16, fontweight='bold', ha='center', va='center', color="#2e3440")

nodes = [
    # text, (x, y), width, height, facecolor
    ("Stage 1: Data Ingestion & Integration\n(AmphiBIO, IUCN, GBIF, WorldClim)",
     (0.5, 0.82), 0.6, 0.08, "#eef0f4"),

    ("Stage 2: Target Variable Construction\n(IUCN Risk Categories: LC to CR)",
     (0.5, 0.69), 0.6, 0.08, "#e1f4e5"),

    ("Stage 3: Feature Engineering\n(Grid-cell Occupancy, Spatial Data, Imputation)",
     (0.5, 0.56), 0.6, 0.08, "#dcedf8"),

    ("Stage 4: Preprocessing\n(Spatial Cross-Validation, Scaling)",
     (0.5, 0.43), 0.6, 0.08, "#fdf4d6"),

    ("Stage 5a: Neural Network\n(TensorFlow/Keras)",
     (0.2, 0.28), 0.28, 0.08, "#f4dbd9"),

    ("Stage 5b: Random Forest\n(Ensemble 1)",
     (0.5, 0.28), 0.28, 0.08, "#f4dbd9"),

    ("Stage 5c: XGBoost\n(Ensemble 2)",
     (0.8, 0.28), 0.28, 0.08, "#f4dbd9"),

    ("Stage 6 & 7: Evaluation & Insights\n(Metrics, Spatial Bias, DD Predictions)",
     (0.5, 0.13), 0.6, 0.08, "#e6dff2"),
]

for text, (x, y), w, h, fc in nodes:
    # draw box
    box = FancyBboxPatch((x - w/2, y - h/2), w, h,
                         boxstyle="round,pad=0.02,rounding_size=0.03",
                         fc=fc, ec="#3b4252", lw=2.5)
    ax.add_patch(box)

    # split text for bolding the first line
    lines = text.split('\n')

    ax.text(x, y + 0.012, lines[0], ha='center', va='center', fontsize=12, fontweight='bold', color="#2e3440")
    if len(lines) > 1:
        ax.text(x, y - 0.015, lines[1], ha='center', va='center', fontsize=11, fontweight='bold', color="#3b4252")

# Draw arrows
arrow_kwargs = dict(arrowstyle="-|>,head_width=0.4,head_length=0.6", lw=1.5, color="#3b4252")

# Vertical arrows
ax.annotate("", xy=(0.5, 0.78), xytext=(0.5, 0.73), arrowprops=arrow_kwargs)
ax.annotate("", xy=(0.5, 0.65), xytext=(0.5, 0.60), arrowprops=arrow_kwargs)
ax.annotate("", xy=(0.5, 0.52), xytext=(0.5, 0.47), arrowprops=arrow_kwargs)

# 4 -> 5
ax.annotate("", xy=(0.2, 0.32), xytext=(0.5, 0.39), arrowprops=arrow_kwargs)
ax.annotate("", xy=(0.5, 0.32), xytext=(0.5, 0.39), arrowprops=arrow_kwargs)
ax.annotate("", xy=(0.8, 0.32), xytext=(0.5, 0.39), arrowprops=arrow_kwargs)

# 5 -> 6
ax.annotate("", xy=(0.5, 0.17), xytext=(0.2, 0.24), arrowprops=arrow_kwargs)
ax.annotate("", xy=(0.5, 0.17), xytext=(0.5, 0.24), arrowprops=arrow_kwargs)
ax.annotate("", xy=(0.5, 0.17), xytext=(0.8, 0.24), arrowprops=arrow_kwargs)

plt.savefig("outputs/architecture.png", dpi=300, bbox_inches='tight')
print("Architecture updated.")
