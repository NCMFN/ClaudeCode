import matplotlib.pyplot as plt
import os
import csv
import json

def generate_conceptual_figure():
    os.makedirs("outputs/figures", exist_ok=True)
    os.makedirs("deliverables/figures", exist_ok=True)

    fig, ax = plt.subplots(figsize=(8, 4), constrained_layout=True)
    # Using Okabe-Ito palette
    colors = ['#56B4E9', '#E69F00']

    ax.text(0.5, 0.5, "Data -> Time-Stratified Sampling -> Causal Features -> Purge Gap ->\nChronological Train/Validation/Test -> Metrics with Block-Bootstrap CIs",
            ha='center', va='center', fontsize=10, bbox=dict(facecolor=colors[0], alpha=0.5))

    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.axis('off')

    # Save as PDF and PNG
    plt.savefig("outputs/figures/concept_methodology.pdf", format='pdf')
    plt.savefig("outputs/figures/concept_methodology.png", format='png', dpi=300)
    plt.close(fig)

def create_manifest():
    with open("outputs/figure_manifest.csv", "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["filename", "type", "source_script", "source_data_hash", "status_at_generation"])
        writer.writerow(["concept_methodology.pdf", "CONCEPTUAL", "src/figures.py", "N/A", "PROPOSED"])
        writer.writerow(["concept_methodology.png", "CONCEPTUAL", "src/figures.py", "N/A", "PROPOSED"])

if __name__ == "__main__":
    generate_conceptual_figure()
    create_manifest()
