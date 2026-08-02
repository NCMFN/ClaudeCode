import matplotlib.pyplot as plt

def apply_style():
    plt.style.use('seaborn-v0_8-whitegrid')
    plt.rcParams.update({
        'font.size': 12,
        'axes.titlesize': 14,
        'axes.labelsize': 12,
        'figure.figsize': (10, 6),
        'lines.linewidth': 2,
    })
