import matplotlib.pyplot as plt
import matplotlib.patches as patches

plt.rcParams.update({'font.size': 11, 'axes.titlesize': 13, 'axes.labelsize': 11, 'xtick.labelsize': 10, 'ytick.labelsize': 10, 'figure.dpi': 300, 'savefig.dpi': 300})

def draw_arch():
    fig, ax = plt.subplots(figsize=(10, 6))
    ax.axis('off')

    # Device Boundary
    device_box = patches.FancyBboxPatch((0.1, 0.1), 0.8, 0.8, boxstyle="round,pad=0.05", edgecolor="black", facecolor="#f0f0f0", lw=2)
    ax.add_patch(device_box)
    ax.text(0.5, 0.95, 'DePIN Device', ha='center', va='center', fontsize=14, fontweight='bold')

    # Hardware/Battery
    hw_box = patches.FancyBboxPatch((0.15, 0.15), 0.25, 0.2, boxstyle="round,pad=0.05", edgecolor="black", facecolor="#e0e0e0", lw=1.5)
    ax.add_patch(hw_box)
    ax.text(0.275, 0.25, 'Battery / Hardware\n(SoC Sensor)', ha='center', va='center')

    # Primary Task
    pt_box = patches.FancyBboxPatch((0.6, 0.15), 0.25, 0.2, boxstyle="round,pad=0.05", edgecolor="black", facecolor="#d0d0ff", lw=1.5)
    ax.add_patch(pt_box)
    ax.text(0.725, 0.25, 'Primary Task\n(Always Active)', ha='center', va='center')

    # FSM Controller
    fsm_box = patches.FancyBboxPatch((0.35, 0.45), 0.3, 0.2, boxstyle="round,pad=0.05", edgecolor="black", facecolor="#d0ffd0", lw=1.5)
    ax.add_patch(fsm_box)
    ax.text(0.5, 0.55, 'FSM Controller\n(S1, S2, S3, S4)', ha='center', va='center', fontweight='bold')

    # Blockchain Module
    bc_box = patches.FancyBboxPatch((0.35, 0.75), 0.3, 0.15, boxstyle="round,pad=0.05", edgecolor="black", facecolor="#ffd0d0", lw=1.5)
    ax.add_patch(bc_box)
    ax.text(0.5, 0.825, 'Blockchain Operations\n(PoC, TX, Relay)', ha='center', va='center')

    # Arrows
    ax.annotate('', xy=(0.35, 0.55), xytext=(0.275, 0.35), arrowprops=dict(arrowstyle='->', lw=2))
    ax.text(0.25, 0.45, 'SoC %', ha='center', va='center', rotation=45)

    ax.annotate('', xy=(0.5, 0.75), xytext=(0.5, 0.65), arrowprops=dict(arrowstyle='->', lw=2))
    ax.text(0.55, 0.7, 'Control Ops', ha='left', va='center')

    # Network
    ax.annotate('', xy=(0.8, 0.825), xytext=(0.65, 0.825), arrowprops=dict(arrowstyle='<->', lw=2))
    ax.text(0.85, 0.825, 'DePIN Network', ha='left', va='center', fontsize=12, fontweight='bold', bbox=dict(boxstyle='round', facecolor='white'))

    plt.tight_layout()
    plt.savefig('results/figures/system_architecture.png')
    plt.savefig('results/figures/system_architecture.pdf')
    plt.close()

if __name__ == '__main__':
    draw_arch()
