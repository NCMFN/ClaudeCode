import matplotlib.pyplot as plt
import seaborn as sns

STYLE = {
    "font.family": "serif",
    "font.size": 12,
    "axes.titlesize": 14,
    "axes.labelsize": 12,
    "xtick.labelsize": 10,
    "ytick.labelsize": 10,
    "legend.fontsize": 10,
    "figure.figsize": (8, 6),
    "figure.dpi": 300,
    "savefig.bbox": "tight"
}

COLORS = {
    "primary": "#1f77b4",
    "secondary": "#ff7f0e",
    "tertiary": "#2ca02c",
    "background": "#ffffff",
    "grid": "#e0e0e0"
}

def apply():
    plt.rcParams.update(STYLE)
    sns.set_style("whitegrid", {"axes.edgecolor": "0.15", "grid.color": COLORS["grid"]})
