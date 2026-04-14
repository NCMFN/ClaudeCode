def create_flowchart_diagram():
    import matplotlib.pyplot as plt
    import matplotlib.patches as patches

    # Increased figsize for higher overall native resolution
    fig, ax = plt.subplots(figsize=(16, 20))
    ax.axis('off')

    # Helper to draw shapes with better contrasting outlines and stylized fonts
    def draw_ellipse(x, y, w, h, fc):
        ax.add_patch(patches.Ellipse((x, y), w, h, facecolor=fc, edgecolor='#333333', lw=2.5, zorder=1))

    def draw_rect(x, y, w, h, fc):
        # Using FancyBboxPatch for rounded rectangles, makes it look much more polished
        ax.add_patch(patches.FancyBboxPatch(
            (x - w/2, y - h/2), w, h,
            boxstyle="round,pad=0.015",
            facecolor=fc, edgecolor='#333333', lw=2.5, zorder=1
        ))

    def draw_diamond(x, y, w, h, fc):
        ax.add_patch(patches.Polygon([
            (x, y + h/2), (x + w/2, y), (x, y - h/2), (x - w/2, y)
        ], facecolor=fc, edgecolor='#333333', lw=2.5, zorder=1))

    def draw_text(x, y, text, fs=13, color='#111111', fw='bold'):
        ax.text(x, y, text, ha='center', va='center', fontsize=fs, color=color, fontweight=fw, zorder=2)

    def draw_arrow(x1, y1, x2, y2, color='#111111', rad=0.0, ls='solid', lw=2.5):
        ax.annotate('', xy=(x2, y2), xytext=(x1, y1),
                    arrowprops=dict(arrowstyle="->,head_width=0.6,head_length=0.8", color=color, lw=lw, ls=ls,
                                    connectionstyle=f"arc3,rad={rad}"))

    # Title - Crisp and large
    ax.text(0.5, 0.98, "Indigenous SDG Mapping - Advanced Flowchart Algorithm",
            ha='center', va='center', fontsize=22, fontweight='black', color='#1F2937',
            bbox=dict(boxstyle="round,pad=0.5", facecolor="#F3F4F6", edgecolor="#D1D5DB", lw=2))

    # Refined Colors (Higher contrast and pastel vibrancy)
    c_start = '#E5E7EB' # Light Gray
    c_acq = '#BAE6FD' # Light Blue
    c_prep = '#86EFAC' # Light Green
    c_dia = '#FDE047' # Bright Yellow
    c_split = '#FED7AA' # Light Orange/Wheat
    c_eval = '#D8B4FE' # Light Purple
    c_out = '#FBCFE8' # Light Pink

    # Draw Shapes
    draw_ellipse(0.5, 0.93, 0.12, 0.04, c_start)
    draw_text(0.5, 0.93, "Start", fs=14)

    draw_rect(0.5, 0.84, 0.45, 0.08, c_acq)
    draw_text(0.5, 0.84, "Data Acquisition\nLoad/Simulate Dataset\n(NGO Reports, Surveys, Traditional Knowledge)", fs=13)

    draw_rect(0.5, 0.73, 0.45, 0.08, c_prep)
    draw_text(0.5, 0.73, "Data Preprocessing\n- Text Cleaning & Parsing\n- Language Detection\n- Feature Generation", fs=13)

    draw_diamond(0.5, 0.61, 0.55, 0.08, c_dia)
    draw_text(0.5, 0.61, "Preprocessing Quality\nInsufficient?", fs=13)

    draw_rect(0.5, 0.50, 0.30, 0.06, c_split)
    draw_text(0.5, 0.50, "Preparation for\nSDG Mapping", fs=14)

    # 3 Parallel Boxes - Wider and better aligned
    draw_rect(0.20, 0.39, 0.26, 0.07, c_split)
    draw_text(0.20, 0.39, "Automated\nSDG Tagging", fs=14)

    draw_rect(0.5, 0.39, 0.28, 0.07, c_split)
    draw_text(0.5, 0.39, "Coherence &\nGap Analysis", fs=14)

    draw_rect(0.80, 0.39, 0.26, 0.07, c_split)
    draw_text(0.80, 0.39, "Solution\nFramework Gen", fs=14)

    draw_rect(0.5, 0.28, 0.40, 0.07, c_eval)
    draw_text(0.5, 0.28, "Mapping Evaluation\n(Prevalence, Conflicts, Impact)", fs=14)

    draw_diamond(0.5, 0.17, 0.55, 0.08, c_dia)
    draw_text(0.5, 0.17, "Mapping Quality\nAcceptable?", fs=13)

    draw_rect(0.5, 0.07, 0.40, 0.07, c_out)
    draw_text(0.5, 0.07, "Select Best Scenarios\n& Output Policies", fs=14)

    draw_diamond(0.5, -0.03, 0.55, 0.08, c_dia)
    draw_text(0.5, -0.03, "Policy Relevance\nDegrades?", fs=13)

    # Draw Arrows
    # Forward paths (Solid Dark Slate)
    arr_color = '#1E293B'
    draw_arrow(0.5, 0.91, 0.5, 0.88, color=arr_color) # Start to Acq
    draw_arrow(0.48, 0.80, 0.48, 0.77, color=arr_color) # Acq to Preproc
    draw_arrow(0.48, 0.69, 0.48, 0.65, color=arr_color) # Preproc to Dia1

    draw_arrow(0.5, 0.57, 0.5, 0.53, color='#16A34A') # Dia1 to Split (No)
    ax.text(0.52, 0.55, "No", color='#16A34A', fontweight='black', fontsize=14)

    # Split to 3 boxes
    draw_arrow(0.45, 0.47, 0.23, 0.425, color=arr_color)
    draw_arrow(0.5, 0.47, 0.5, 0.425, color=arr_color)
    draw_arrow(0.55, 0.47, 0.77, 0.425, color=arr_color)

    # 3 boxes to Eval
    draw_arrow(0.23, 0.355, 0.45, 0.315, color=arr_color)
    draw_arrow(0.5, 0.355, 0.5, 0.315, color=arr_color)
    draw_arrow(0.77, 0.355, 0.55, 0.315, color=arr_color)

    draw_arrow(0.5, 0.245, 0.5, 0.21, color=arr_color) # Eval to Dia2

    draw_arrow(0.5, 0.13, 0.5, 0.105, color='#16A34A') # Dia2 to Out (Yes)
    ax.text(0.52, 0.117, "Yes", color='#16A34A', fontweight='black', fontsize=14)

    draw_arrow(0.5, 0.035, 0.5, 0.01, color=arr_color) # Out to Dia3

    # Feedback paths (Vibrant Red)
    red_color = '#DC2626'

    # Dia1 Yes to Acq
    draw_arrow(0.775, 0.61, 0.725, 0.84, color=red_color, rad=0.25)
    ax.text(0.78, 0.75, "Yes", color=red_color, fontweight='black', fontsize=13)

    # Dia2 No (Retune) to middle models
    draw_arrow(0.65, 0.19, 0.55, 0.365, color=red_color, rad=0.35)
    ax.text(0.68, 0.21, "No (Retune)", color=red_color, fontweight='black', fontsize=13)

    # Dia2 No (Refine Features) to Split
    draw_arrow(0.775, 0.17, 0.65, 0.50, color=red_color, rad=0.55)
    ax.text(0.85, 0.32, "No (Refine Features)", color=red_color, fontweight='black', fontsize=13)

    # Dia3 Yes (Retrain) to Split
    draw_arrow(0.775, -0.03, 0.65, 0.48, color=red_color, rad=0.7)
    ax.text(0.86, 0.12, "Yes (Retrain)", color=red_color, fontweight='black', fontsize=13)

    # Concept loops (Purple dashed)
    purp_color = '#7C3AED'
    # Eval to Split
    draw_arrow(0.35, 0.30, 0.35, 0.48, color=purp_color, rad=-0.4, ls='dashed')
    ax.text(0.32, 0.35, "Mapping ↔ Prep loop", color='#4C1D95', fontsize=11, fontweight='bold', rotation=70)

    # Eval to Preproc
    draw_arrow(0.70, 0.28, 0.65, 0.71, color=purp_color, rad=0.45, ls='dashed')
    ax.text(0.75, 0.48, "Preproc ↔ Eval loop", color='#4C1D95', fontsize=11, fontweight='bold', rotation=75)

    plt.tight_layout()
    # DPI increased to 400 for high resolution, sharpness, and clarity
    plt.savefig('output_figures/plot_29.png', bbox_inches='tight', dpi=400)
    plt.show()
