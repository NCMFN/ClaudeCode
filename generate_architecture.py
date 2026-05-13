import matplotlib.pyplot as plt
import matplotlib.patches as patches

# Global settings for high-clarity publication quality diagram
plt.rcParams.update({
    'font.size': 11,
    'axes.titlesize': 13,
    'axes.labelsize': 11,
    'xtick.labelsize': 10,
    'ytick.labelsize': 10,
    'figure.dpi': 300,
    'savefig.dpi': 300
})

def draw_rounded_box(ax, center_x, center_y, width, height, text, color, text_color='black'):
    # Soft scientific color palettes by module type
    box = patches.FancyBboxPatch((center_x - width/2, center_y - height/2), width, height,
                                 boxstyle="round,pad=0.1", ec="black", fc=color, lw=1.5)
    ax.add_patch(box)
    ax.text(center_x, center_y, text, ha='center', va='center', fontsize=10, color=text_color, fontweight='bold')

fig, ax = plt.subplots(figsize=(12, 8))

# Define colors
c_data = '#A8D0E6'      # Light Blue - Data
c_process = '#F8E9A1'   # Light Yellow - Processing
c_feature = '#F76C6C'   # Soft Red - Feature Engineering
c_model = '#374785'     # Dark Blue - ML Model (text white)
c_eval = '#24305E'      # Navy - Evaluation (text white)

# 1. Data Sources
draw_rounded_box(ax, 2, 7, 2.5, 1, "Raw Sensor Logs\n(IoT Thermal & CPU)", c_data)
draw_rounded_box(ax, 2, 5, 2.5, 1, "Historical Failure\nRecords (Multi-class)", c_data)

# 2. Preprocessing
draw_rounded_box(ax, 5, 6, 2.5, 1.5, "Data Preprocessing\n- Missing Value Imputation\n- IQR Outlier Capping\n- SMOTE Balancing", c_process)

# 3. Feature Engineering
draw_rounded_box(ax, 8, 6, 2.5, 1.5, "Feature Engineering\n- Stress Index (CPUxTemp)\n- Duty Cycle Ratio\n- Peak Excursion Count\n- RUL Extraction", c_feature)

# 4. ML Models
draw_rounded_box(ax, 11, 7, 2.5, 1.2, "Task A: RUL Regression\n(XGBoost / RF)", c_model, text_color='white')
draw_rounded_box(ax, 11, 5, 2.5, 1.2, "Task B: Classification\n(Failure Modes)", c_model, text_color='white')

# 5. Output / Evaluation
draw_rounded_box(ax, 14, 6, 2.5, 1.5, "Evaluation & Output\n- SHAP Explanations\n- Degradation Trends\n- End-of-Life Prediction", c_eval, text_color='white')

# Add arrows
# Data -> Preprocessing
ax.annotate("", xy=(3.75, 6.25), xytext=(3.25, 7), arrowprops=dict(arrowstyle="->", lw=2))
ax.annotate("", xy=(3.75, 5.75), xytext=(3.25, 5), arrowprops=dict(arrowstyle="->", lw=2))

# Preprocessing -> Feature Engineering
ax.annotate("", xy=(6.75, 6), xytext=(6.25, 6), arrowprops=dict(arrowstyle="->", lw=2))

# Feature Engineering -> Models
ax.annotate("", xy=(9.75, 6.8), xytext=(9.25, 6.2), arrowprops=dict(arrowstyle="->", lw=2))
ax.annotate("", xy=(9.75, 5.2), xytext=(9.25, 5.8), arrowprops=dict(arrowstyle="->", lw=2))

# Models -> Evaluation
ax.annotate("", xy=(12.75, 6.2), xytext=(12.25, 6.8), arrowprops=dict(arrowstyle="->", lw=2))
ax.annotate("", xy=(12.75, 5.8), xytext=(12.25, 5.2), arrowprops=dict(arrowstyle="->", lw=2))

# Formatting
ax.set_xlim(0, 16)
ax.set_ylim(4, 8)
ax.axis('off')
plt.title("Hardware End-of-Life Prediction ML Architecture", pad=20, fontweight='bold', fontsize=14)

plt.tight_layout()
plt.savefig("system_architecture.png", dpi=300, bbox_inches='tight')
plt.close()
