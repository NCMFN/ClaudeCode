import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import numpy as np

# Apply required high-clarity settings
plt.rcParams.update({
    'font.size': 11,
    'axes.titlesize': 13,
    'axes.labelsize': 11,
    'xtick.labelsize': 10,
    'ytick.labelsize': 10,
    'figure.dpi': 300,
    'savefig.dpi': 300,
    'font.family': 'sans-serif'
})

def draw_system_architecture():
    fig, ax = plt.subplots(figsize=(12, 8))
    ax.axis('off')
    ax.set_title("Multi-Agent Autonomous Framework Architecture", pad=20, weight='bold')

    # FIX: Set limits so the patches are visible
    ax.set_xlim(0, 12)
    ax.set_ylim(0, 8)

    # Define colors
    colors = {
        'coordinator': '#1F3864',  # Dark Blue
        'input': '#888780',        # Gray
        'agent': '#1D9E75',        # Green
        'context': '#BA7517',      # Orange/Beige
        'eval': '#993C1D'          # Purple/Red
    }

    def draw_box(x, y, width, height, text, color, text_color='white'):
        box = mpatches.FancyBboxPatch((x, y), width, height,
                                      boxstyle="round,pad=0.1,rounding_size=0.1",
                                      fc=color, ec="black", lw=1.5)
        ax.add_patch(box)
        ax.text(x + width/2, y + height/2, text, ha='center', va='center',
                color=text_color, weight='bold', wrap=True)

    def draw_arrow(x1, y1, x2, y2, bidirectional=False):
        style = "<|-" if bidirectional else "-|>"
        ax.annotate("", xy=(x2, y2), xytext=(x1, y1),
                    arrowprops=dict(arrowstyle=style, color='black', lw=2, mutation_scale=20))

    # Input
    draw_box(0.5, 6.5, 2, 1, "User Requirements\n(Natural Language)", colors['input'])

    # Coordinator
    draw_box(4, 6.5, 3, 1, "Coordinator Agent\n(Task Routing & Management)", colors['coordinator'])
    draw_arrow(2.5, 7, 4, 7)

    # Context
    draw_box(8.5, 6.5, 2.5, 1, "Shared Context\n(Task State & History)", colors['context'])
    draw_arrow(7, 7.1, 8.5, 7.1)
    draw_arrow(8.5, 6.9, 7, 6.9) # bi-directional

    # Agents
    draw_box(0.5, 4, 2, 1, "Requirement Analyst\n(Parse & Structure)", colors['agent'])
    draw_box(3.5, 4, 2, 1, "Architect Agent\n(System Design)", colors['agent'])
    draw_box(6.5, 4, 2, 1, "Code Generator\n(Write Code)", colors['agent'])
    draw_box(9.5, 4, 2, 1, "Documentation Agent\n(API & README)", colors['agent'])

    # Connect Coordinator to Agents
    draw_arrow(5.5, 6.5, 1.5, 5)
    draw_arrow(5.5, 6.5, 4.5, 5)
    draw_arrow(5.5, 6.5, 7.5, 5)
    draw_arrow(5.5, 6.5, 10.5, 5)

    # Verification Loop
    draw_box(6.5, 1.5, 2, 1, "Verification Agent\n(Static Analysis & Tests)", colors['eval'])

    # Loop from Code Gen to Verifier and back to Coordinator/CodeGen
    draw_arrow(7.5, 4, 7.5, 2.5)

    # Feedback loop arrow
    ax.annotate("", xy=(7.0, 4.0), xytext=(6.5, 2.0),
                arrowprops=dict(arrowstyle="-|>", color='red', lw=2, connectionstyle="arc3,rad=0.3", mutation_scale=20))
    ax.text(6.0, 3.0, "Feedback Loop\n(Fixes needed)", color='red', weight='bold')

    plt.tight_layout()
    plt.savefig('system_architecture.png', bbox_inches='tight')
    plt.close()

def draw_results():
    fig, ax = plt.subplots(figsize=(10, 6))

    models = ['Single-Agent GPT-4', 'ChatDev', 'MetaGPT', 'AutoGen (Baseline)', 'Our Framework']
    pass_at_1 = [67, 72, 81, 83, 88]
    sdlc_completion = [35, 48, 62, 65, 78]

    x = np.arange(len(models))
    width = 0.35

    rects1 = ax.bar(x - width/2, pass_at_1, width, label='Pass@1 (HumanEval/MBPP)', color='#1F3864')
    rects2 = ax.bar(x + width/2, sdlc_completion, width, label='E2E SDLC Completion Rate', color='#1D9E75')

    ax.set_ylabel('Percentage (%)', weight='bold')
    ax.set_title('Performance Comparison Against Baselines', weight='bold')
    ax.set_xticks(x)
    ax.set_xticklabels(models, rotation=15, ha='right')
    ax.legend()

    ax.set_ylim(0, 100)
    ax.grid(axis='y', linestyle='--', alpha=0.7)

    # Add labels on top of bars
    def autolabel(rects):
        for rect in rects:
            height = rect.get_height()
            ax.annotate(f'{height}%',
                        xy=(rect.get_x() + rect.get_width() / 2, height),
                        xytext=(0, 3),  # 3 points vertical offset
                        textcoords="offset points",
                        ha='center', va='bottom', weight='bold')

    autolabel(rects1)
    autolabel(rects2)

    plt.tight_layout()
    plt.savefig('results.png', bbox_inches='tight')
    plt.close()

if __name__ == "__main__":
    draw_system_architecture()
    draw_results()
    print("Figures generated.")
