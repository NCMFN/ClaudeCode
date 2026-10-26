import matplotlib.pyplot as plt
import matplotlib.patches as patches
import pandas as pd
import os
import json
import logging

logger = logging.getLogger(__name__)

STYLE = {'primary': '#56B4E9', 'secondary': '#E69F00'}

plt.rcParams['pdf.fonttype'] = 42
plt.rcParams['ps.fonttype'] = 42
plt.rcParams['font.size'] = 8

def check_provenance():
    prov_path = 'outputs/provenance.json'
    if not os.path.exists(prov_path):
        raise RuntimeError("provenance.json missing. Refusing to generate MEASURED figures.")

    with open(prov_path, 'r') as f:
        prov = json.load(f)

    if prov.get('status') in ['FIXTURE']:
        raise RuntimeError("Provenance indicates FIXTURE data. Refusing to generate MEASURED figures.")

    return prov

def generate_figure_a(df_legacy: pd.DataFrame, df_stratified: pd.DataFrame, output_dir: str, legacy_pr_auc: float = None):
    prov = check_provenance()
    os.makedirs(output_dir, exist_ok=True)

    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(8, 6), sharex=True, constrained_layout=True)

    if not df_legacy.empty:
        leaky_benign = df_legacy[df_legacy['is_malicious'] == 0].groupby('day').size()
        leaky_malicious = df_legacy[df_legacy['is_malicious'] == 1].groupby('day').size()
        ax1.bar(leaky_benign.index, leaky_benign.values, color=STYLE['primary'], label='Benign (Legacy Replay)', alpha=0.7)
        ax1.bar(leaky_malicious.index, leaky_malicious.values, color=STYLE['secondary'], label='Malicious', alpha=0.7)

        # Plot the leaky baseline PR-AUC as an inset or text box conceptually (allowed for data annotations)
        if legacy_pr_auc is not None and not pd.isna(legacy_pr_auc):
            ax1.text(0.02, 0.8, f"Time-only Baseline PR-AUC: {legacy_pr_auc:.3f}",
                     transform=ax1.transAxes, bbox=dict(facecolor='white', alpha=0.8, edgecolor='black'))

    ax1.set_ylabel('Event Count')
    ax1.legend()

    if not df_stratified.empty:
        strat_benign = df_stratified[df_stratified['is_malicious'] == 0].groupby('day').size()
        strat_malicious = df_stratified[df_stratified['is_malicious'] == 1].groupby('day').size()
        ax2.bar(strat_benign.index, strat_benign.values, color=STYLE['primary'], label='Benign (Stratified)', alpha=0.7)
        ax2.bar(strat_malicious.index, strat_malicious.values, color=STYLE['secondary'], label='Malicious', alpha=0.7)

    train_end = prov['config']['protocols']['p3_train_days']
    test_start = train_end + prov['config']['protocols']['purge_gap_days']
    ax2.axvline(train_end, color='black', linestyle='--', label='Train End')
    ax2.axvline(test_start, color='red', linestyle='--', label='Test Start')

    ax2.set_xlabel('Day')
    ax2.set_ylabel('Event Count')
    ax2.legend()

    out_prefix = os.path.join(output_dir, 'figure_a')
    plt.savefig(f"{out_prefix}.pdf", format='pdf')
    plt.savefig(f"{out_prefix}.png", format='png', dpi=300)
    plt.close()

def generate_figure_b(output_dir: str):
    os.makedirs(output_dir, exist_ok=True)
    fig, ax = plt.subplots(figsize=(8, 4), constrained_layout=True)

    ax.add_patch(patches.Rectangle((0.1, 0.4), 0.2, 0.2, fill=True, color=STYLE['primary'], alpha=0.5))
    ax.text(0.2, 0.5, 'Data Ingestion\n& Time-Stratified\nSampling', ha='center', va='center')
    ax.add_patch(patches.Arrow(0.32, 0.5, 0.06, 0, width=0.05, color='black'))

    ax.add_patch(patches.Rectangle((0.4, 0.4), 0.2, 0.2, fill=True, color=STYLE['secondary'], alpha=0.5))
    ax.text(0.5, 0.5, 'Causal Features\n(Expanding Window)', ha='center', va='center')
    ax.add_patch(patches.Arrow(0.62, 0.5, 0.06, 0, width=0.05, color='black'))

    ax.add_patch(patches.Rectangle((0.7, 0.4), 0.25, 0.2, fill=False, edgecolor='black', linewidth=2))
    ax.add_patch(patches.Rectangle((0.72, 0.45), 0.08, 0.1, fill=True, color='green', alpha=0.4))
    ax.text(0.76, 0.5, 'Train', ha='center', va='center')

    ax.add_patch(patches.Rectangle((0.80, 0.45), 0.05, 0.1, fill=True, color='grey', alpha=0.2))
    ax.text(0.825, 0.5, 'Purge\nGap', ha='center', va='center', fontsize=6)

    ax.add_patch(patches.Rectangle((0.85, 0.45), 0.08, 0.1, fill=True, color='red', alpha=0.4))
    ax.text(0.89, 0.5, 'Test', ha='center', va='center')

    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.axis('off')

    out_prefix = os.path.join(output_dir, 'concept_figure_b')
    plt.savefig(f"{out_prefix}.pdf", format='pdf')
    plt.savefig(f"{out_prefix}.png", format='png', dpi=300)
    plt.close()
