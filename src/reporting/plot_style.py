import matplotlib.pyplot as plt
STYLE = {
    'primary': '#2E5EAA',
    'secondary': '#D9534F',
    'tertiary': '#5CB85C',
    'quaternary': '#F0AD4E',
    'background': '#F8F9FA',
    'text': '#333333',
    'grid': '#E5E5E5'
}
COLORS = STYLE
def apply():
    plt.rcParams.update({
        'figure.facecolor': STYLE['background'],
        'axes.facecolor': STYLE['background'],
        'axes.edgecolor': STYLE['text'],
        'axes.labelcolor': STYLE['text'],
        'text.color': STYLE['text'],
        'xtick.color': STYLE['text'],
        'ytick.color': STYLE['text'],
        'grid.color': STYLE['grid'],
        'font.family': 'sans-serif',
        'font.size': 12,
        'axes.titlesize': 14,
        'axes.labelsize': 12,
        'lines.linewidth': 2.0,
        'figure.dpi': 300,
        'savefig.bbox': 'tight',
        'savefig.dpi': 300
    })
