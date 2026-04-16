def create_flowchart_diagram():
    import matplotlib.pyplot as plt
    import matplotlib.patches as patches

    # Matching the exact style of the uploaded Bionic Mushroom flowchart
    # 1. Plain rectangular boxes with 1px black borders (no FancyBboxPatch)
    # 2. Standard colors: lightgrey, lightblue, palegreen, khaki, wheat, plum, lightpink
    # 3. Standard thin black arrows for forward progression, thin bright green/red/purple for conditions
    # 4. Serif font for node text, bold sans-serif for title

    fig, ax = plt.subplots(figsize=(12, 16), dpi=300)
    ax.axis('off')

    # Helper to draw shapes
    def draw_ellipse(x, y, w, h, fc):
        ax.add_patch(patches.Ellipse((x, y), w, h, facecolor=fc, edgecolor='black', lw=1, zorder=1))

    def draw_rect(x, y, w, h, fc):
        ax.add_patch(patches.Rectangle((x - w/2, y - h/2), w, h, facecolor=fc, edgecolor='black', lw=1, zorder=1))

    def draw_diamond(x, y, w, h, fc):
        ax.add_patch(patches.Polygon([
            (x, y + h/2), (x + w/2, y), (x, y - h/2), (x - w/2, y)
        ], facecolor=fc, edgecolor='black', lw=1, zorder=1))

    def draw_text(x, y, text, fs=11, color='black', fontfamily='serif', fontweight='normal'):
        ax.text(x, y, text, ha='center', va='center', fontsize=fs, color=color,
                fontfamily=fontfamily, fontweight=fontweight, zorder=2)

    def draw_arrow(x1, y1, x2, y2, color='black', rad=0.0, ls='solid'):
        ax.annotate('', xy=(x2, y2), xytext=(x1, y1),
                    arrowprops=dict(arrowstyle="-|>", color=color, lw=1, ls=ls,
                                    connectionstyle=f"arc3,rad={rad}"))

    # Title - Bold Sans-serif
    ax.text(0.5, 0.98, "Indigenous SDG Mapping - Advanced Flowchart Algorithm",
            ha='center', va='center', fontsize=16, fontweight='bold', fontfamily='sans-serif')

    # Draw Shapes
    draw_ellipse(0.5, 0.94, 0.1, 0.03, 'lightgrey') # Start
    draw_text(0.5, 0.94, "Start")

    draw_rect(0.5, 0.85, 0.40, 0.07, 'lightblue') # Acq
    draw_text(0.5, 0.85, "Data Acquisition\nLoad/Simulate Dataset\n(NGO Reports, Surveys, Traditional Knowledge)")

    draw_rect(0.5, 0.74, 0.35, 0.06, 'palegreen') # Preproc
    draw_text(0.5, 0.74, "Data Preprocessing\n- Text Cleaning & Parsing\n- Language Detection\n- Feature Generation")

    draw_diamond(0.5, 0.63, 0.5, 0.07, 'khaki') # Dia1
    draw_text(0.5, 0.63, "Preprocessing Quality\nInsufficient?")

    draw_rect(0.5, 0.53, 0.22, 0.04, 'khaki') # Split
    draw_text(0.5, 0.53, "Preparation for\nSDG Mapping")

    # 3 Parallel Boxes (Wheat)
    draw_rect(0.25, 0.43, 0.22, 0.04, 'wheat')
    draw_text(0.25, 0.43, "Automated\nSDG Tagging")

    draw_rect(0.5, 0.43, 0.22, 0.04, 'wheat')
    draw_text(0.5, 0.43, "Coherence &\nGap Analysis")

    draw_rect(0.75, 0.43, 0.22, 0.04, 'wheat')
    draw_text(0.75, 0.43, "Solution\nFramework Gen")

    draw_rect(0.5, 0.32, 0.25, 0.04, 'plum') # Eval
    draw_text(0.5, 0.32, "Mapping Evaluation\n(Prevalence, Conflicts, Impact)")

    draw_diamond(0.5, 0.21, 0.5, 0.07, 'khaki') # Dia2
    draw_text(0.5, 0.21, "Mapping Quality\nAcceptable?")

    draw_rect(0.5, 0.11, 0.28, 0.04, 'lightpink') # Out
    draw_text(0.5, 0.11, "Select Best Scenarios\n& Output Policies")

    draw_diamond(0.5, 0.02, 0.5, 0.07, 'khaki') # Dia3
    draw_text(0.5, 0.02, "Policy Relevance\nDegrades?")

    # Draw Arrows
    # Forward paths (Black & Bright Green)
    draw_arrow(0.5, 0.925, 0.5, 0.885) # Start to Acq
    draw_arrow(0.48, 0.815, 0.48, 0.77) # Acq to Preproc
    draw_arrow(0.48, 0.71, 0.48, 0.665) # Preproc to Dia1

    draw_arrow(0.5, 0.595, 0.5, 0.55, color='#00FF00') # Dia1 to Split (No)
    draw_text(0.52, 0.575, "No", color='#00FF00')

    # Split to 3 boxes
    draw_arrow(0.42, 0.51, 0.28, 0.45)
    draw_arrow(0.5, 0.51, 0.5, 0.45)
    draw_arrow(0.58, 0.51, 0.72, 0.45)

    # 3 boxes to Eval
    draw_arrow(0.28, 0.41, 0.45, 0.34)
    draw_arrow(0.5, 0.41, 0.5, 0.34)
    draw_arrow(0.72, 0.41, 0.55, 0.34)

    draw_arrow(0.5, 0.30, 0.5, 0.245) # Eval to Dia2

    draw_arrow(0.5, 0.175, 0.5, 0.13, color='#00FF00') # Dia2 to Out (Yes)
    draw_text(0.52, 0.155, "Yes", color='#00FF00')

    draw_arrow(0.5, 0.09, 0.5, 0.055) # Out to Dia3

    # Feedback paths (Red)
    # Dia1 Yes to Acq
    draw_arrow(0.75, 0.63, 0.70, 0.85, color='red', rad=0.2)
    draw_text(0.72, 0.76, "Yes", color='red')

    # Dia2 No (Retune) to middle models
    draw_arrow(0.65, 0.24, 0.58, 0.41, color='red', rad=0.3)
    draw_text(0.72, 0.28, "No (Retune)", color='red')

    # Dia2 No (Refine Features) to Split
    draw_arrow(0.75, 0.21, 0.61, 0.53, color='red', rad=0.5)
    draw_text(0.85, 0.38, "No (Refine Features)", color='red')

    # Dia3 Yes (Retrain) to Split
    draw_arrow(0.75, 0.02, 0.61, 0.51, color='red', rad=0.6)
    draw_text(0.83, 0.18, "Yes (Retrain)", color='red')

    # Concept loops (Purple dashed)
    # Eval to Split
    draw_arrow(0.38, 0.34, 0.39, 0.51, color='blueviolet', rad=-0.4, ls='dashed')
    draw_text(0.36, 0.42, "Mapping <-> Prep loop", color='black')

    # Eval to Preproc
    draw_arrow(0.62, 0.32, 0.675, 0.73, color='blueviolet', rad=0.5, ls='dashed')
    draw_text(0.74, 0.48, "Preproc <-> Eval loop", color='black')

    plt.tight_layout()
    plt.savefig('output_figures/plot_29.png', bbox_inches='tight', dpi=300)
    plt.show()
