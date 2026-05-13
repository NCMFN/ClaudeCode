import matplotlib.pyplot as plt
import matplotlib.patches as patches

plt.rcParams.update({'font.size': 11, 'axes.titlesize': 13, 'axes.labelsize': 11, 'xtick.labelsize': 10, 'ytick.labelsize': 10, 'figure.dpi': 300, 'savefig.dpi': 300})

fig, ax = plt.subplots(figsize=(12, 8))
ax.axis('off')

# Data Sources
ax.add_patch(patches.FancyBboxPatch((0.1, 0.7), 0.2, 0.15, boxstyle="round,pad=0.05", fill=True, facecolor="#4CAF50", edgecolor="black", linewidth=2))
plt.text(0.2, 0.775, "CPS/IoT Data Sources\n(SWaT, HAI, NSL-KDD, etc.)", ha='center', va='center', weight='bold')

# Preprocessing
ax.add_patch(patches.FancyBboxPatch((0.4, 0.7), 0.2, 0.15, boxstyle="round,pad=0.05", fill=True, facecolor="#2196F3", edgecolor="black", linewidth=2))
plt.text(0.5, 0.775, "Data Preprocessing\n- Normalisation\n- Sliding Windows\n- SMOTE", ha='center', va='center', weight='bold')

# Models
ax.add_patch(patches.FancyBboxPatch((0.7, 0.7), 0.2, 0.15, boxstyle="round,pad=0.05", fill=True, facecolor="#9C27B0", edgecolor="black", linewidth=2))
plt.text(0.8, 0.775, "Anomaly Detection\nModels\n(CNN-BiLSTM-Attn, IF)", ha='center', va='center', weight='bold', color='white')

# Evaluation
ax.add_patch(patches.FancyBboxPatch((0.4, 0.4), 0.5, 0.15, boxstyle="round,pad=0.05", fill=True, facecolor="#FF9800", edgecolor="black", linewidth=2))
plt.text(0.65, 0.475, "Evaluation Metrics & Visualization\n- F1, Precision, Recall, ROC-AUC\n- Confusion Matrices\n- Real-time Latency", ha='center', va='center', weight='bold')

# Arrows
plt.annotate("", xy=(0.4, 0.775), xytext=(0.3, 0.775), arrowprops=dict(arrowstyle="->", lw=2))
plt.annotate("", xy=(0.7, 0.775), xytext=(0.6, 0.775), arrowprops=dict(arrowstyle="->", lw=2))
plt.annotate("", xy=(0.8, 0.55), xytext=(0.8, 0.7), arrowprops=dict(arrowstyle="->", lw=2))

plt.title("System Architecture for Anomaly Detection in Digital-Physical Environments", weight='bold', fontsize=14)
plt.tight_layout()
plt.savefig('system_architecture.png')
plt.close()
