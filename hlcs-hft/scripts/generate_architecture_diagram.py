#!/usr/bin/env python3
import os
import matplotlib.pyplot as plt
import matplotlib.patches as patches

# Ensure figures directory exists
os.makedirs('results/figures', exist_ok=True)

def draw_box(ax, x, y, width, height, label, color):
    # Draw rounded rectangle
    box = patches.FancyBboxPatch((x, y), width, height,
                                 boxstyle="round,pad=0.2,rounding_size=0.1",
                                 edgecolor='black', facecolor=color, lw=1.5)
    ax.add_patch(box)

    # Add text label
    ax.text(x + width/2, y + height/2, label,
            ha='center', va='center', fontsize=10, weight='bold')

def draw_arrow(ax, start_x, start_y, end_x, end_y, label=""):
    ax.annotate("",
                xy=(end_x, end_y), xycoords='data',
                xytext=(start_x, start_y), textcoords='data',
                arrowprops=dict(arrowstyle="->", color="black", lw=1.5, shrinkA=5, shrinkB=5))
    if label:
        mid_x = (start_x + end_x) / 2
        mid_y = (start_y + end_y) / 2
        ax.text(mid_x, mid_y, label, ha='center', va='bottom', fontsize=8)

fig, ax = plt.subplots(figsize=(12, 10))

# Define colors per standard
# Blue for ML/Processing, Green for core, Purple for Evaluation, Beige/Orange for integration
color_input = '#DCE6F1' # Light Blue
color_commit = '#EBF1DE' # Light Green
color_agg = '#E5DFEC' # Light Purple
color_disc = '#FDE9D9' # Light Orange
color_audit = '#DAEEF3' # Light Cyan
color_market = '#F2DCDB' # Light Red

# Title
plt.title("Fig. 1: Hybrid Post-Quantum Commitment System Architecture", fontsize=14, weight='bold', y=1.05)

# --- 1. Input Layer ---
draw_box(ax, 0.5, 8.5, 4, 1, "Input Layer\n(Trading Engine & Normalization)", color_input)

# --- 2. Commitment Layer ---
draw_box(ax, 0.5, 7, 1.8, 1, "Hash Commitment\nFast Path\n(SHA3-256)", color_commit)
draw_box(ax, 2.7, 7, 1.8, 1, "Lattice-Proxy\nPost-Quantum Path\n(LWE proxy)", color_commit)
draw_box(ax, 1.0, 5.5, 3, 1, "Hybrid Commitment Controller", color_commit)

# --- 3. Aggregation Layer ---
draw_box(ax, 1.0, 4, 3, 1, "Aggregation Layer\n(Merkle-Lattice Tree & Root)", color_agg)

# --- 4. Disclosure Layer ---
draw_box(ax, 6, 7, 2, 1.5, "Disclosure Layer\n(Fiat-Shamir Baseline)", color_disc)
draw_box(ax, 8.5, 7, 2, 1.5, "Disclosure Layer\n(STARK ZK Pipeline)", color_disc)

# --- 5. Verification and Audit Layer ---
draw_box(ax, 6.5, 4, 3.5, 1, "Verification & Audit Layer\n(Roots, Openings, Proofs)", color_audit)

# --- 6. Market-Impact Analysis Layer ---
draw_box(ax, 6.5, 1.5, 3.5, 1.5, "Market-Impact Analysis Layer\n(Cryptographic Latency -> Slippage)", color_market)

# --- Connections ---
# Input to Commitments
draw_arrow(ax, 2.5, 8.5, 1.4, 8)
draw_arrow(ax, 2.5, 8.5, 3.6, 8)

# Commitments to Hybrid Controller
draw_arrow(ax, 1.4, 7, 2.0, 6.5)
draw_arrow(ax, 3.6, 7, 3.0, 6.5)

# Hybrid to Aggregation
draw_arrow(ax, 2.5, 5.5, 2.5, 5)

# Aggregation to Disclosure
draw_arrow(ax, 4.0, 4.5, 7.0, 7)
draw_arrow(ax, 4.0, 4.5, 9.5, 7)

# Disclosure to Verification
draw_arrow(ax, 7.0, 7, 7.5, 5)
draw_arrow(ax, 9.5, 7, 9.0, 5)

# Aggregation to Verification
draw_arrow(ax, 4.0, 4.2, 6.5, 4.2)

# Verification to Market Impact
draw_arrow(ax, 8.25, 4, 8.25, 3)

# Add dotted box around groups to show structure
import matplotlib.patches as patches
commit_group = patches.Rectangle((0.2, 5.2), 4.6, 3.1, linewidth=1.5, edgecolor='gray', facecolor='none', linestyle='--')
ax.add_patch(commit_group)
ax.text(0.3, 8.1, "Commitment Layer", fontsize=9, color='gray')

disc_group = patches.Rectangle((5.8, 6.8), 4.9, 1.9, linewidth=1.5, edgecolor='gray', facecolor='none', linestyle='--')
ax.add_patch(disc_group)
ax.text(5.9, 8.5, "Disclosure Layer", fontsize=9, color='gray')

# Formatting
ax.set_xlim(0, 11)
ax.set_ylim(0, 10)
ax.axis('off')

plt.tight_layout()
plt.savefig('results/figures/system_architecture.png', dpi=300, bbox_inches='tight')
plt.close()
