import os
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import json
from shared_style import apply_style

def main():
    apply_style()
    raw_dir = 'outputs/raw'
    fig_dir = 'outputs/figures'
    tab_dir = 'outputs/tables'

    os.makedirs(fig_dir, exist_ok=True)
    os.makedirs(tab_dir, exist_ok=True)

    # Load data
    ionq = pd.read_csv(os.path.join(raw_dir, 'simulation_results_ionq_aria.csv'))
    aqt = pd.read_csv(os.path.join(raw_dir, 'simulation_results_aqt_ring.csv'))

    ionq['regime'] = 'IonQ Aria'
    aqt['regime'] = 'AQT'
    df = pd.concat([ionq, aqt])

    # FIG 1: fidelity_decay_vs_threshold.png
    fig1, ax1 = plt.subplots()
    rtt_vals = np.linspace(0, df['rtt'].max(), 100)
    # F(t) = 0.5 + 0.5 * exp(-t / T2)
    f_ionq = 0.5 + 0.5 * np.exp(-rtt_vals / 1.0)
    f_aqt = 0.5 + 0.5 * np.exp(-rtt_vals / 0.05)

    ax1.plot(rtt_vals, f_ionq, label='IonQ Aria (T2=1.0s)', color='blue')
    ax1.plot(rtt_vals, f_aqt, label='AQT (T2=0.05s)', color='orange')
    ax1.axhline(0.85, color='red', linestyle='--', label='Security Threshold (0.85)')
    ax1.set_xlabel('RTT (s)')
    ax1.set_ylabel('Fidelity')
    ax1.set_title('Fidelity Decay vs Threshold')
    ax1.legend()
    fig1.savefig(os.path.join(fig_dir, 'fidelity_decay_vs_threshold.png'), dpi=300, bbox_inches='tight')
    plt.close(fig1)

    # FIG 2: flush_hold_comparison_adaptive_vs_static.png
    fig2, axes = plt.subplots(1, 2, figsize=(12, 5), sharey=True)
    labels = ['HOLD', 'FLUSH']
    x = np.arange(len(labels))
    width = 0.35

    for i, (regime, data) in enumerate([('IonQ Aria', ionq), ('AQT', aqt)]):
        adapt_counts = data['adaptive_action'].value_counts()
        static_counts = data['static_action'].value_counts()

        adapt_vals = [adapt_counts.get(l, 0) for l in labels]
        stat_vals = [static_counts.get(l, 0) for l in labels]

        axes[i].bar(x - width/2, adapt_vals, width, label='Adaptive')
        axes[i].bar(x + width/2, stat_vals, width, label='Static')
        axes[i].set_xticks(x)
        axes[i].set_xticklabels(labels)
        axes[i].set_title(f'{regime}')
        if i == 0:
            axes[i].set_ylabel('Count')
            axes[i].legend()

    fig2.suptitle('FLUSH / HOLD Counts: Adaptive vs Static')
    fig2.savefig(os.path.join(fig_dir, 'flush_hold_comparison_adaptive_vs_static.png'), dpi=300, bbox_inches='tight')
    plt.close(fig2)

    # FIG 3: zombie_key_exposure_rate.png
    fig3, axes = plt.subplots(1, 2, figsize=(12, 5), sharey=True)
    err_labels = ['% Zombie Exposures', '% Premature Flushes']
    x = np.arange(len(err_labels))

    for i, (regime, data) in enumerate([('IonQ Aria', ionq), ('AQT', aqt)]):
        total = len(data)
        adapt_errs = [data['zombie_adaptive'].sum() / total * 100, data['unnecessary_flush_adaptive'].sum() / total * 100]
        stat_errs = [data['zombie_static'].sum() / total * 100, data['unnecessary_flush_static'].sum() / total * 100]

        axes[i].bar(x - width/2, adapt_errs, width, label='Adaptive')
        axes[i].bar(x + width/2, stat_errs, width, label='Static')
        axes[i].set_xticks(x)
        axes[i].set_xticklabels(err_labels)
        axes[i].set_title(f'{regime}')
        if i == 0:
            axes[i].set_ylabel('Rate (%)')
            axes[i].legend()

    fig3.suptitle('Zombie Exposure vs Premature Flush Rates')
    fig3.savefig(os.path.join(fig_dir, 'zombie_key_exposure_rate.png'), dpi=300, bbox_inches='tight')
    plt.close(fig3)

    # TABLE 1: policy_event_log_summary.csv
    summary_data = []
    for regime, data in [('IonQ Aria', ionq), ('AQT', aqt)]:
        for pol in ['adaptive', 'static']:
            col = f'{pol}_action'
            flushes = data[data[col] == 'FLUSH']
            summary_data.append({
                'Regime': regime,
                'Policy': pol.capitalize(),
                'HOLD_Count': (data[col] == 'HOLD').sum(),
                'FLUSH_Count': len(flushes),
                'Mean_Fidelity_at_Flush': flushes['true_fidelity'].mean() if len(flushes) > 0 else np.nan,
                'Median_Fidelity_at_Flush': flushes['true_fidelity'].median() if len(flushes) > 0 else np.nan
            })
    pd.DataFrame(summary_data).to_csv(os.path.join(tab_dir, 'policy_event_log_summary.csv'), index=False)

    # TABLE 2: zombie_vs_early_flush_tradeoff.csv
    tradeoff_data = []
    for regime, data in [('IonQ Aria', ionq), ('AQT', aqt)]:
        total = len(data)
        for pol in ['adaptive', 'static']:
            tradeoff_data.append({
                'Regime': regime,
                'Policy': pol.capitalize(),
                'Zombie_Count': data[f'zombie_{pol}'].sum(),
                'Zombie_Rate': data[f'zombie_{pol}'].sum() / total,
                'Premature_Flush_Count': data[f'unnecessary_flush_{pol}'].sum(),
                'Premature_Flush_Rate': data[f'unnecessary_flush_{pol}'].sum() / total
            })
    pd.DataFrame(tradeoff_data).to_csv(os.path.join(tab_dir, 'zombie_vs_early_flush_tradeoff.csv'), index=False)

    # TABLE 3: t2_regime_comparison.csv
    regime_data = []
    for regime, data in [('IonQ Aria', ionq), ('AQT', aqt)]:
        # Mean RTT tolerated -> mean RTT when action is HOLD
        mean_rtt_tol = data[data['adaptive_action'] == 'HOLD']['rtt'].mean()
        flush_rate = (data['adaptive_action'] == 'FLUSH').sum() / len(data)
        regime_data.append({
            'Regime': regime,
            'Mean_RTT_Tolerated_Adaptive': mean_rtt_tol,
            'Flush_Rate_Adaptive': flush_rate
        })
    pd.DataFrame(regime_data).to_csv(os.path.join(tab_dir, 't2_regime_comparison.csv'), index=False)

    # MANIFEST: outputs/source_manifest.json
    manifest = {
        'figures': [
            {'filename': 'fidelity_decay_vs_threshold.png', 'source': 'model equations + rtt limits'},
            {'filename': 'flush_hold_comparison_adaptive_vs_static.png', 'source': 'outputs/raw/simulation_results_*.csv'},
            {'filename': 'zombie_key_exposure_rate.png', 'source': 'outputs/raw/simulation_results_*.csv'}
        ],
        'tables': [
            {'filename': 'policy_event_log_summary.csv', 'source': 'outputs/raw/simulation_results_*.csv'},
            {'filename': 'zombie_vs_early_flush_tradeoff.csv', 'source': 'outputs/raw/simulation_results_*.csv'},
            {'filename': 't2_regime_comparison.csv', 'source': 'outputs/raw/simulation_results_*.csv'}
        ]
    }
    with open('outputs/source_manifest.json', 'w') as f:
        json.dump(manifest, f, indent=4)

    print("Task 2 complete.")

if __name__ == "__main__":
    main()
