import matplotlib.pyplot as plt

STYLE = {
    "figure.dpi": 300, "savefig.dpi": 300,
    "font.size": 11, "axes.titlesize": 13, "axes.titleweight": "bold",
    "axes.labelsize": 11, "axes.grid": True, "grid.alpha": 0.3,
    "axes.spines.top": False, "axes.spines.right": False,
    "figure.figsize": (8, 5),
}

COLORS = {"primary": "#2E5EAA", "secondary": "#D9534F", "tertiary": "#5CB85C", "neutral": "#888888"}

def apply():
    plt.rcParams.update(STYLE)
