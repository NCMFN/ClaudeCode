import matplotlib.pyplot as plt
import matplotlib.patches as patches

fig, ax = plt.subplots(figsize=(12, 8))
ax.axis('off')

# Set background
fig.patch.set_facecolor('#f4f4f9')

# Define boxes
boxes = [
    # Data Layer
    {'x': 0.1, 'y': 0.8, 'w': 0.25, 'h': 0.1, 'text': 'Data Generation & Collection\n(SAF Chemical & Physical Props)', 'color': '#add8e6'},
    {'x': 0.4, 'y': 0.8, 'w': 0.2, 'h': 0.1, 'text': 'Data Preprocessing\n(Imputation & Standard Scaling)', 'color': '#add8e6'},
    {'x': 0.65, 'y': 0.8, 'w': 0.2, 'h': 0.1, 'text': 'Class Balancing\n(SMOTE)', 'color': '#add8e6'},

    # Modeling Layer
    {'x': 0.2, 'y': 0.55, 'w': 0.6, 'h': 0.15, 'text': '', 'color': '#e6e6fa', 'alpha': 0.5}, # Container for models
    {'x': 0.25, 'y': 0.575, 'w': 0.15, 'h': 0.1, 'text': 'Logistic\nRegression', 'color': '#98fb98'},
    {'x': 0.425, 'y': 0.575, 'w': 0.15, 'h': 0.1, 'text': 'Random Forest &\nXGBoost (Tuned)', 'color': '#98fb98'},
    {'x': 0.6, 'y': 0.575, 'w': 0.15, 'h': 0.1, 'text': 'Keras Neural\nNetwork', 'color': '#98fb98'},

    # Evaluation Layer
    {'x': 0.4, 'y': 0.35, 'w': 0.2, 'h': 0.1, 'text': 'Model Evaluation &\nSHAP Interpretation', 'color': '#ffd700'},

    # Deployment Layer
    {'x': 0.35, 'y': 0.1, 'w': 0.3, 'h': 0.1, 'text': 'Streamlit Deployment App\n(Drop-In Compatibility Prediction)', 'color': '#ffb6c1'}
]

# Draw boxes
for box in boxes:
    alpha = box.get('alpha', 1.0)
    rect = patches.Rectangle((box['x'], box['y']), box['w'], box['h'], linewidth=2, edgecolor='black', facecolor=box['color'], alpha=alpha)
    ax.add_patch(rect)
    if box['text']:
        ax.text(box['x'] + box['w']/2, box['y'] + box['h']/2, box['text'], ha='center', va='center', fontsize=11, fontweight='bold', wrap=True)

# Add group label for modeling
ax.text(0.5, 0.72, 'Model Training & Selection', ha='center', va='center', fontsize=12, fontweight='bold')

# Draw arrows
arrows = [
    ((0.35, 0.85), (0.4, 0.85)),
    ((0.6, 0.85), (0.65, 0.85)),
    ((0.5, 0.8), (0.5, 0.7)),
    ((0.5, 0.55), (0.5, 0.45)),
    ((0.5, 0.35), (0.5, 0.2))
]

for start, end in arrows:
    ax.annotate('', xy=end, xytext=start, arrowprops=dict(facecolor='black', shrink=0.05, width=2, headwidth=8))

plt.title('SAF Compatibility Prediction Architecture', fontsize=16, fontweight='bold', y=1.05)
plt.tight_layout()
plt.savefig('SAF_Compatibility_Prediction/images/system_architecture.png', dpi=300)
print("System architecture image generated.")
