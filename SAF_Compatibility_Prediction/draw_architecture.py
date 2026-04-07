import matplotlib.pyplot as plt
import matplotlib.patches as patches

fig, ax = plt.subplots(figsize=(12, 14))
ax.axis('off')
fig.patch.set_facecolor('white')

# Function to draw a rectangle (Process)
def draw_rect(ax, x, y, w, h, text, color='#add8e6'):
    rect = patches.Rectangle((x - w/2, y - h/2), w, h, linewidth=1.5, edgecolor='black', facecolor=color)
    ax.add_patch(rect)
    ax.text(x, y, text, ha='center', va='center', fontsize=10, fontweight='bold', wrap=True)

# Function to draw an ellipse (Start/End)
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

# Function to draw a diamond (Decision)
def draw_diamond(ax, x, y, w, h, text, color='#ffe4b5'):
    points = [[x, y + h/2], [x + w/2, y], [x, y - h/2], [x - w/2, y]]
    poly = patches.Polygon(points, closed=True, linewidth=1.5, edgecolor='black', facecolor=color)
    ax.add_patch(poly)
    ax.text(x, y, text, ha='center', va='center', fontsize=9, fontweight='bold')

# Arrow drawing
def draw_arrow(ax, start, end, label=None, label_pos=0.5, label_offset=(0, 0)):
    ax.annotate('', xy=end, xytext=start, arrowprops=dict(arrowstyle='->', lw=2, color='black'))
    if label:
        x_label = start[0] + (end[0] - start[0]) * label_pos + label_offset[0]
        y_label = start[1] + (end[1] - start[1]) * label_pos + label_offset[1]
        ax.text(x_label, y_label, label, ha='center', va='center', fontsize=9, fontweight='bold', color='red', bbox=dict(facecolor='white', edgecolor='none', alpha=0.8, pad=0))

# Custom arrow path (for feedback loops)
def draw_path_arrow(ax, points, label=None, label_idx=0, label_offset=(0,0)):
    for i in range(len(points)-1):
        if i == len(points) - 2:
            draw_arrow(ax, points[i], points[i+1])
        else:
            ax.plot([points[i][0], points[i+1][0]], [points[i][1], points[i+1][1]], lw=2, color='black')

    if label:
        p1 = points[label_idx]
        p2 = points[label_idx+1]
        x_label = (p1[0] + p2[0]) / 2 + label_offset[0]
        y_label = (p1[1] + p2[1]) / 2 + label_offset[1]
        ax.text(x_label, y_label, label, ha='center', va='center', fontsize=9, fontweight='bold', color='red', bbox=dict(facecolor='white', edgecolor='none', alpha=0.8, pad=0))

# Element Coordinates
center_x = 0.45

y_start = 0.95
y_input = 0.88
y_preproc = 0.81
y_balance = 0.74
y_train = 0.67
y_eval = 0.60
y_dec1 = 0.50 # Performance Decision
y_tune = 0.50 # Hyperparameter tuning
y_interp = 0.38
y_dec2 = 0.28 # Interpretability Decision
y_deploy = 0.17
y_end = 0.08

# Draw elements
draw_ellipse(ax, center_x, y_start, 0.2, 0.04, "Start", '#98fb98')
draw_parallelogram(ax, center_x, y_input, 0.4, 0.05, "Input: SAF Dataset\n(Chemical/Physical Props)", '#fffacd')
draw_rect(ax, center_x, y_preproc, 0.4, 0.05, "Data Preprocessing\n(Imputation & Scaling)", '#add8e6')
draw_rect(ax, center_x, y_balance, 0.4, 0.05, "Class Balancing\n(SMOTE)", '#add8e6')

draw_rect(ax, center_x, y_train, 0.4, 0.05, "Model Training\n(LogReg, RF, XGBoost, NN)", '#e6e6fa')
draw_rect(ax, center_x, y_eval, 0.4, 0.05, "Model Evaluation\n(Accuracy, AUC, F1)", '#ffd700')

draw_diamond(ax, center_x, y_dec1, 0.3, 0.08, "Is Performance\nAcceptable?", '#ffe4b5')
draw_rect(ax, 0.85, y_dec1, 0.25, 0.05, "Hyperparameter\nTuning / Feature Eng", '#dda0dd')

draw_rect(ax, center_x, y_interp, 0.4, 0.05, "SHAP Interpretability\nAnalysis", '#ffb6c1')

draw_diamond(ax, center_x, y_dec2, 0.3, 0.08, "Does Model Explanation\nMake Physical Sense?", '#ffe4b5')
draw_rect(ax, 0.1, y_dec2, 0.18, 0.05, "Expert Review &\nData Revision", '#dda0dd')

draw_parallelogram(ax, center_x, y_deploy, 0.4, 0.05, "Deploy Model via\nStreamlit API", '#fffacd')
draw_ellipse(ax, center_x, y_end, 0.2, 0.04, "End", '#98fb98')

# Draw Main Flow Lines
draw_arrow(ax, (center_x, y_start-0.02), (center_x, y_input+0.025))
draw_arrow(ax, (center_x, y_input-0.025), (center_x, y_preproc+0.025))
draw_arrow(ax, (center_x, y_preproc-0.025), (center_x, y_balance+0.025))
draw_arrow(ax, (center_x, y_balance-0.025), (center_x, y_train+0.025))
draw_arrow(ax, (center_x, y_train-0.025), (center_x, y_eval+0.025))
draw_arrow(ax, (center_x, y_eval-0.025), (center_x, y_dec1+0.04))

# Decision 1 Flow (Performance)
draw_arrow(ax, (center_x, y_dec1-0.04), (center_x, y_interp+0.025), label="Yes", label_pos=0.3, label_offset=(-0.04, 0))
draw_arrow(ax, (center_x+0.15, y_dec1), (0.725, y_dec1), label="No", label_pos=0.5, label_offset=(0, 0.02))

# Feedback Loop 1
draw_path_arrow(ax, [(0.85, y_dec1+0.025), (0.85, y_train), (center_x+0.2, y_train)])

# Decision 2 Flow (Interpretability)
draw_arrow(ax, (center_x, y_interp-0.025), (center_x, y_dec2+0.04))
draw_arrow(ax, (center_x, y_dec2-0.04), (center_x, y_deploy+0.025), label="Yes", label_pos=0.3, label_offset=(-0.04, 0))
draw_arrow(ax, (center_x-0.15, y_dec2), (0.19, y_dec2), label="No", label_pos=0.5, label_offset=(0, 0.02))

# Feedback Loop 2 (Back to Preprocessing)
draw_path_arrow(ax, [(0.1, y_dec2+0.025), (0.1, y_preproc), (center_x-0.2, y_preproc)])

draw_arrow(ax, (center_x, y_deploy-0.025), (center_x, y_end+0.02))

plt.title('Iterative Flowchart for SAF Compatibility Prediction', fontsize=16, fontweight='bold', y=1.0)
plt.tight_layout()
plt.savefig('SAF_Compatibility_Prediction/images/system_architecture.png', dpi=300)
print("Closed-loop flowchart image generated successfully.")
