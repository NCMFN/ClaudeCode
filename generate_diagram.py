import matplotlib.pyplot as plt
import matplotlib.patches as mpatches

plt.rcParams.update({
    'font.size': 11,
    'axes.titlesize': 13,
    'axes.labelsize': 11,
    'xtick.labelsize': 10,
    'ytick.labelsize': 10,
    'figure.dpi': 300,
    'savefig.dpi': 300
})

fig, ax = plt.subplots(figsize=(14, 16))
ax.set_xlim(0, 10)
ax.set_ylim(-2.5, 11)
ax.axis('off')

# Definitions
headers = [
    ("Data Ingestion Layer", (5, 10.5)),
    ("Data Processing Pipeline", (5, 7.5)),
    ("Model Training Layer", (5, 2.7)),
    ("Evaluation & Visualization Layer", (5, -0.2))
]

labels = [
    ("Figshare API", (1.5, 9.7)),
    ("GBIF API Queries", (3.8, 9.7)),
    ("Raster Extraction", (6.2, 9.7)),
    ("Taxonomy Validation", (8.5, 9.7)),
    ("Merge & Raster Sampling", (5, 6.6)),
    ("Imputation & Scaling", (5, 5.2)),
    ("SMOTE Oversampling", (5, 3.8)),
    ("Train & 5-Fold CV", (3.2, 2.0)),
    ("Train & 5-Fold CV", (5, 2.0)),
    ("Train", (7.3, 2.0))
]

boxes = [
    ("AmphiBIO Dataset - Traits", (1.5, 8.8)),
    ("GBIF Occurrences & IUCN\nStatus", (3.8, 8.8)),
    ("WorldClim Climate Data", (6.2, 8.8)),
    ("AmphibiaWeb Dataset", (8.5, 8.8)),
    ("Feature Engineering", (5, 5.9)),
    ("Data Splitting", (5, 4.5)),
    ("Random Forest", (3.2, 1.1)),
    ("XGBoost", (5, 1.1)),
    ("Deep Neural Network -\nKeras", (7.3, 1.1)),
    ("Feature Importance", (1.5, -1.3)),
    ("Geographic Risk Maps", (3.8, -1.3)),
    ("ROC-AUC Curves", (6.2, -1.3)),
    ("Dataset Schema &\nConfusion Matrix", (8.5, -1.3))
]

# Plotting elements
for text, pos in headers:
    ax.text(pos[0], pos[1], text, ha="center", va="center", fontsize=12, color="#000000")

label_props = dict(boxstyle="square,pad=0.3", fc="#EAEAEA", ec="none")
for text, pos in labels:
    ax.text(pos[0], pos[1], text, ha="center", va="center", bbox=label_props, fontsize=10, color="#333333")

box_props = dict(boxstyle="round,pad=0.8", fc="#F2EEFF", ec="#B4A0E5", lw=1.5)
for text, pos in boxes:
    ax.text(pos[0], pos[1], text, ha="center", va="center", bbox=box_props, fontsize=11, color="#333333")

def add_arrow(ax, start, end, rad=0.0):
    ax.annotate("",
                xy=end, xycoords='data',
                xytext=start, textcoords='data',
                arrowprops=dict(arrowstyle="->", color="#444444", lw=1.2,
                                shrinkA=18, shrinkB=18,
                                connectionstyle=f"arc3,rad={rad}"))

# 1. Ingestion -> Labels
add_arrow(ax, (5, 10.4), (1.5, 9.8), rad=0.0)
add_arrow(ax, (5, 10.4), (3.8, 9.8), rad=0.0)
add_arrow(ax, (5, 10.4), (6.2, 9.8), rad=0.0)
add_arrow(ax, (5, 10.4), (8.5, 9.8), rad=0.0)

# 2. Labels -> Top Boxes
add_arrow(ax, (1.5, 9.6), (1.5, 9.1), rad=0.0)
add_arrow(ax, (3.8, 9.6), (3.8, 9.1), rad=0.0)
add_arrow(ax, (6.2, 9.6), (6.2, 9.1), rad=0.0)
add_arrow(ax, (8.5, 9.6), (8.5, 9.1), rad=0.0)

# 3. Top Boxes -> Processing Pipeline
add_arrow(ax, (1.5, 8.5), (5, 7.6), rad=-0.1)
add_arrow(ax, (3.8, 8.5), (5, 7.6), rad=-0.05)
add_arrow(ax, (6.2, 8.5), (5, 7.6), rad=0.05)
add_arrow(ax, (8.5, 8.5), (5, 7.6), rad=0.1)

# 4. Pipeline stages
add_arrow(ax, (5, 7.4), (5, 6.7), rad=0.0)
add_arrow(ax, (5, 6.5), (5, 6.1), rad=0.0)
add_arrow(ax, (5, 5.7), (5, 5.3), rad=0.0)
add_arrow(ax, (5, 5.1), (5, 4.7), rad=0.0)
add_arrow(ax, (5, 4.3), (5, 3.9), rad=0.0)
add_arrow(ax, (5, 3.7), (5, 2.8), rad=0.0)

# 5. Model Training -> Labels
add_arrow(ax, (5, 2.6), (3.2, 2.1), rad=0.0)
add_arrow(ax, (5, 2.6), (5, 2.1), rad=0.0)
add_arrow(ax, (5, 2.6), (7.3, 2.1), rad=0.0)

# 6. Labels -> Models
add_arrow(ax, (3.2, 1.9), (3.2, 1.4), rad=0.0)
add_arrow(ax, (5, 1.9), (5, 1.4), rad=0.0)
add_arrow(ax, (7.3, 1.9), (7.3, 1.4), rad=0.0)

# 7. Models -> Evaluation
add_arrow(ax, (3.2, 0.8), (5, -0.1), rad=0.1)
add_arrow(ax, (5, 0.8), (5, -0.1), rad=0.0)
add_arrow(ax, (7.3, 0.8), (5, -0.1), rad=-0.1)

# 8. Evaluation -> Bottom Boxes
add_arrow(ax, (5, -0.3), (1.5, -1.1), rad=0.1)
add_arrow(ax, (5, -0.3), (3.8, -1.1), rad=0.05)
add_arrow(ax, (5, -0.3), (6.2, -1.1), rad=-0.05)
add_arrow(ax, (5, -0.3), (8.5, -1.1), rad=-0.1)

plt.tight_layout()
plt.savefig('AER1.png', bbox_inches='tight')
print("Saved AER1.png")
