import matplotlib.pyplot as plt
import matplotlib.patches as patches

fig, ax = plt.subplots(figsize=(16, 10))
ax.axis('off')
fig.patch.set_facecolor('white')

# Helper function to draw rounded boundary boxes for layers
def draw_boundary(ax, x, y, w, h, title, label_y_offset=0):
    rect = patches.Rectangle((x, y), w, h, linewidth=2, edgecolor='gray', linestyle='--', facecolor='none', zorder=1)
    ax.add_patch(rect)
    ax.text(x + w/2, y - 0.03 + label_y_offset, title, ha='center', va='top', fontsize=14, fontweight='bold', zorder=5)

# Helper function to draw inner blocks (like the specific sectors or servers)
def draw_block(ax, x, y, w, h, title, text="", color='#f0f8ff'):
    rect = patches.Rectangle((x, y), w, h, linewidth=1.5, edgecolor='black', facecolor=color, zorder=2)
    ax.add_patch(rect)
    if title:
        ax.text(x + w/2, y + h - 0.05, title, ha='center', va='top', fontsize=11, fontweight='bold', zorder=5)
    if text:
        ax.text(x + w/2, y + h/2 - 0.02, text, ha='center', va='center', fontsize=10, wrap=True, zorder=5)

# Arrow drawing
def draw_arrow(ax, start, end, style='->', lw=2, linestyle='-'):
    ax.annotate('', xy=end, xytext=start, arrowprops=dict(arrowstyle=style, lw=lw, color='black', ls=linestyle), zorder=3)

# 1. Edge Layer (Left side)
draw_boundary(ax, 0.05, 0.1, 0.45, 0.8, "Edge Layer\n(Data Acquisition & Local Processing)", label_y_offset=-0.02)

#   1a. Lab Sector
draw_block(ax, 0.08, 0.65, 0.25, 0.2, "Chemical Analysis Sector", text="[Sensors/GC-MS]\n\nAromatics, Alkanes,\nCycloalkanes, Olefins", color='#e6f2ff')
#   1b. Physical Sector
draw_block(ax, 0.08, 0.40, 0.25, 0.2, "Physical Properties Sector", text="[Testing Rigs]\n\nViscosity, Density,\nFlash/Freezing Point", color='#e6f2ff')
#   1c. Gateway
draw_block(ax, 0.36, 0.45, 0.12, 0.25, "Local Gateway", text="Data Cleaning\n&\nStandardization", color='#f0fff0')

# Connect sectors to gateway
draw_arrow(ax, (0.33, 0.75), (0.36, 0.65), style='<|-|>', linestyle=':')
draw_arrow(ax, (0.33, 0.50), (0.36, 0.50), style='<|-|>', linestyle=':')


# 2. Platform Layer (Top Right)
draw_boundary(ax, 0.55, 0.5, 0.4, 0.4, "Platform Layer", label_y_offset=-0.02)
draw_block(ax, 0.6, 0.55, 0.3, 0.3, "Cloud ML Server", text="Training Pipeline:\nLogReg, RF, XGBoost, NN\n(SMOTE & GridSearchCV)", color='#fff0f5')


# 3. Enterprise Layer (Bottom Right)
draw_boundary(ax, 0.55, 0.1, 0.4, 0.35, "Enterprise Layer", label_y_offset=-0.02)
draw_block(ax, 0.6, 0.15, 0.3, 0.25, "Decision & Deployment Hub", text="[SIEM Equivalent]\n\nSHAP Interpretability\n&\nStreamlit App (Pass/Fail Alert)", color='#ffffe0')


# Cross-Layer Connections
# Gateway to Cloud Server
draw_arrow(ax, (0.48, 0.575), (0.55, 0.7), lw=2, linestyle='--')
# Cloud Server to Enterprise Hub
draw_arrow(ax, (0.75, 0.55), (0.75, 0.4), lw=2, linestyle='-')
# Enterprise Hub back to Cloud (Feedback loop)
draw_arrow(ax, (0.85, 0.4), (0.85, 0.55), lw=2, linestyle='--')


plt.title('Hierarchical SAF Compatibility Prediction Architecture', fontsize=18, fontweight='bold', y=0.98)
plt.tight_layout()
plt.savefig('SAF_Compatibility_Prediction/images/system_architecture.png', dpi=300, bbox_inches='tight')
print("Multi-layered architecture image generated successfully.")
