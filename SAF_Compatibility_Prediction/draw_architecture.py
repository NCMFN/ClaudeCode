import matplotlib.pyplot as plt
import matplotlib.patches as patches

fig, ax = plt.subplots(figsize=(10, 12))
ax.axis('off')

fig.patch.set_facecolor('white')

# Function to draw a rectangle
def draw_rect(ax, x, y, w, h, text, color='#add8e6'):
    rect = patches.Rectangle((x - w/2, y - h/2), w, h, linewidth=1.5, edgecolor='black', facecolor=color)
    ax.add_patch(rect)
    ax.text(x, y, text, ha='center', va='center', fontsize=10, fontweight='bold', wrap=True)

# Function to draw an ellipse
def draw_ellipse(ax, x, y, w, h, text, color='#ffb6c1'):
    ellipse = patches.Ellipse((x, y), w, h, linewidth=1.5, edgecolor='black', facecolor=color)
    ax.add_patch(ellipse)
    ax.text(x, y, text, ha='center', va='center', fontsize=10, fontweight='bold')

# Function to draw a parallelogram (Input/Output)
def draw_parallelogram(ax, x, y, w, h, text, color='#fffacd'):
    points = [[x - w/2 + 0.1*w, y - h/2], [x + w/2 + 0.1*w, y - h/2],
              [x + w/2 - 0.1*w, y + h/2], [x - w/2 - 0.1*w, y + h/2]]
    poly = patches.Polygon(points, closed=True, linewidth=1.5, edgecolor='black', facecolor=color)
    ax.add_patch(poly)
    ax.text(x, y, text, ha='center', va='center', fontsize=10, fontweight='bold')

def draw_diamond(ax, x, y, w, h, text, color='#ffe4b5'):
    points = [[x, y + h/2], [x + w/2, y], [x, y - h/2], [x - w/2, y]]
    poly = patches.Polygon(points, closed=True, linewidth=1.5, edgecolor='black', facecolor=color)
    ax.add_patch(poly)
    ax.text(x, y, text, ha='center', va='center', fontsize=9, fontweight='bold')

# Arrow drawing
def draw_arrow(ax, start, end):
    ax.annotate('', xy=end, xytext=start, arrowprops=dict(arrowstyle='->', lw=2, color='black'))

# Draw elements
draw_ellipse(ax, 0.5, 0.95, 0.2, 0.05, "Start", '#98fb98')
draw_parallelogram(ax, 0.5, 0.85, 0.4, 0.06, "Input: Raw Dataset\n(SAF Features)", '#fffacd')
draw_rect(ax, 0.5, 0.75, 0.4, 0.06, "Data Preprocessing\n(Missing Values, Standardization)", '#add8e6')
draw_rect(ax, 0.5, 0.65, 0.4, 0.06, "Train-Test Split & SMOTE\n(Class Balancing)", '#add8e6')

draw_diamond(ax, 0.5, 0.50, 0.4, 0.12, "Model Training\n(LogReg, RF, XGBoost, NN)", '#ffe4b5')

draw_rect(ax, 0.5, 0.35, 0.4, 0.06, "Hyperparameter Tuning\n(GridSearchCV on XGBoost)", '#dda0dd')
draw_rect(ax, 0.5, 0.25, 0.4, 0.06, "Model Evaluation &\nSHAP Interpretation", '#ffb6c1')
draw_parallelogram(ax, 0.5, 0.15, 0.4, 0.06, "Output: Prediction via\nStreamlit App", '#fffacd')
draw_ellipse(ax, 0.5, 0.05, 0.2, 0.05, "End", '#98fb98')

# Draw lines
draw_arrow(ax, (0.5, 0.925), (0.5, 0.88))
draw_arrow(ax, (0.5, 0.82), (0.5, 0.78))
draw_arrow(ax, (0.5, 0.72), (0.5, 0.68))
draw_arrow(ax, (0.5, 0.62), (0.5, 0.56))
draw_arrow(ax, (0.5, 0.44), (0.5, 0.38))
draw_arrow(ax, (0.5, 0.32), (0.5, 0.28))
draw_arrow(ax, (0.5, 0.22), (0.5, 0.18))
draw_arrow(ax, (0.5, 0.12), (0.5, 0.075))

plt.title('Algorithm Flowchart for SAF Compatibility Prediction', fontsize=14, fontweight='bold', y=1.0)
plt.tight_layout()
plt.savefig('SAF_Compatibility_Prediction/images/system_architecture.png', dpi=300)
print("Flowchart image generated.")
