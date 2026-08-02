import os
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

def generate_reports(results_dir: str, output_figures_dir: str, output_tables_dir: str):
    os.makedirs(output_figures_dir, exist_ok=True)
    os.makedirs(output_tables_dir, exist_ok=True)

    # Load data
    ionq_path = os.path.join(results_dir, 'simulation_results_ionq_aria.csv')
    aqt_path = os.path.join(results_dir, 'simulation_results_aqt_ring.csv')

    df_ionq = pd.read_csv(ionq_path)
    df_aqt = pd.read_csv(aqt_path)

    # ------------------ FIGURES ------------------
    # 01. Fidelity vs RTT (IonQ)
    plt.figure(figsize=(8,5))
    df_sorted_ionq = df_ionq.sort_values(by='rtt')
    plt.plot(df_sorted_ionq['rtt'], df_sorted_ionq['true_fidelity'], label='IonQ Aria')
    plt.axhline(0.85, color='r', linestyle='--', label='Threshold')
    plt.title('True Fidelity vs RTT (IonQ Aria)')
    plt.xlabel('RTT (s)')
    plt.ylabel('Fidelity')
    plt.legend()
    plt.savefig(os.path.join(output_figures_dir, '01_fidelity_decay_curve_ionq.png'), dpi=300)
    plt.close()

    # 02. Fidelity vs RTT (AQT)
    plt.figure(figsize=(8,5))
    df_sorted_aqt = df_aqt.sort_values(by='rtt')
    plt.plot(df_sorted_aqt['rtt'], df_sorted_aqt['true_fidelity'], label='AQT Ring', color='orange')
    plt.axhline(0.85, color='r', linestyle='--', label='Threshold')
    plt.title('True Fidelity vs RTT (AQT Ring)')
    plt.xlabel('RTT (s)')
    plt.ylabel('Fidelity')
    plt.legend()
    plt.savefig(os.path.join(output_figures_dir, '02_fidelity_decay_curve_aqt.png'), dpi=300)
    plt.close()

    # 03. RTT Histogram
    plt.figure(figsize=(8,5))
    plt.hist(df_ionq['rtt'], bins=30, color='gray', edgecolor='black')
    plt.title('RTT Distribution')
    plt.xlabel('RTT (s)')
    plt.ylabel('Frequency')
    plt.savefig(os.path.join(output_figures_dir, '03_rtt_distribution_histogram.png'), dpi=300)
    plt.close()

    # 04. Fidelity Distribution (IonQ)
    plt.figure(figsize=(8,5))
    plt.hist(df_ionq['true_fidelity'], bins=30, color='blue', edgecolor='black')
    plt.axvline(0.85, color='r', linestyle='--')
    plt.title('Fidelity Distribution (IonQ Aria)')
    plt.xlabel('Fidelity')
    plt.ylabel('Frequency')
    plt.savefig(os.path.join(output_figures_dir, '04_fidelity_distribution_ionq.png'), dpi=300)
    plt.close()

    # 05. Fidelity Distribution (AQT)
    plt.figure(figsize=(8,5))
    plt.hist(df_aqt['true_fidelity'], bins=30, color='orange', edgecolor='black')
    plt.axvline(0.85, color='r', linestyle='--')
    plt.title('Fidelity Distribution (AQT Ring)')
    plt.xlabel('Fidelity')
    plt.ylabel('Frequency')
    plt.savefig(os.path.join(output_figures_dir, '05_fidelity_distribution_aqt.png'), dpi=300)
    plt.close()

    # 06. Policy Actions Bar (IonQ)
    plt.figure(figsize=(8,5))
    adaptive_counts = df_ionq['adaptive_action'].value_counts()
    static_counts = df_ionq['static_action'].value_counts()
    labels = ['HOLD', 'FLUSH']
    x = np.arange(len(labels))
    width = 0.35
    plt.bar(x - width/2, [adaptive_counts.get(l, 0) for l in labels], width, label='Adaptive')
    plt.bar(x + width/2, [static_counts.get(l, 0) for l in labels], width, label='Static')
    plt.xticks(x, labels)
    plt.ylabel('Count')
    plt.title('Policy Actions Comparison (IonQ Aria)')
    plt.legend()
    plt.savefig(os.path.join(output_figures_dir, '06_policy_actions_bar_ionq.png'), dpi=300)
    plt.close()

    # 07. Policy Actions Bar (AQT)
    plt.figure(figsize=(8,5))
    adaptive_counts = df_aqt['adaptive_action'].value_counts()
    static_counts = df_aqt['static_action'].value_counts()
    plt.bar(x - width/2, [adaptive_counts.get(l, 0) for l in labels], width, label='Adaptive', color='orange')
    plt.bar(x + width/2, [static_counts.get(l, 0) for l in labels], width, label='Static', color='brown')
    plt.xticks(x, labels)
    plt.ylabel('Count')
    plt.title('Policy Actions Comparison (AQT Ring)')
    plt.legend()
    plt.savefig(os.path.join(output_figures_dir, '07_policy_actions_bar_aqt.png'), dpi=300)
    plt.close()

    # 08. Error Types (IonQ)
    plt.figure(figsize=(8,5))
    err_labels = ['Zombie Keys Exposed', 'Unnecessary Flushes']
    adaptive_errs = [df_ionq['zombie_adaptive'].sum(), df_ionq['unnecessary_flush_adaptive'].sum()]
    static_errs = [df_ionq['zombie_static'].sum(), df_ionq['unnecessary_flush_static'].sum()]
    x2 = np.arange(len(err_labels))
    plt.bar(x2 - width/2, adaptive_errs, width, label='Adaptive')
    plt.bar(x2 + width/2, static_errs, width, label='Static')
    plt.xticks(x2, err_labels)
    plt.ylabel('Count')
    plt.title('Error Types (IonQ Aria)')
    plt.legend()
    plt.savefig(os.path.join(output_figures_dir, '08_error_types_comparison_ionq.png'), dpi=300)
    plt.close()

    # 09. Error Types (AQT)
    plt.figure(figsize=(8,5))
    adaptive_errs = [df_aqt['zombie_adaptive'].sum(), df_aqt['unnecessary_flush_adaptive'].sum()]
    static_errs = [df_aqt['zombie_static'].sum(), df_aqt['unnecessary_flush_static'].sum()]
    plt.bar(x2 - width/2, adaptive_errs, width, label='Adaptive', color='orange')
    plt.bar(x2 + width/2, static_errs, width, label='Static', color='brown')
    plt.xticks(x2, err_labels)
    plt.ylabel('Count')
    plt.title('Error Types (AQT Ring)')
    plt.legend()
    plt.savefig(os.path.join(output_figures_dir, '09_error_types_comparison_aqt.png'), dpi=300)
    plt.close()

    # 10. RTT Trace
    plt.figure(figsize=(10,4))
    plt.plot(df_ionq.index[:100], df_ionq['rtt'][:100], marker='.', color='black')
    plt.title('RTT Time Series Trace (First 100 steps)')
    plt.xlabel('Timestep')
    plt.ylabel('RTT (s)')
    plt.savefig(os.path.join(output_figures_dir, '10_rtt_timeseries_trace.png'), dpi=300)
    plt.close()

    # 11. Fidelity Trace (IonQ)
    plt.figure(figsize=(10,4))
    plt.plot(df_ionq.index[:100], df_ionq['true_fidelity'][:100], marker='.')
    plt.axhline(0.85, color='r', linestyle='--')
    plt.title('Fidelity Trace (IonQ - First 100 steps)')
    plt.xlabel('Timestep')
    plt.ylabel('Fidelity')
    plt.savefig(os.path.join(output_figures_dir, '11_fidelity_timeseries_trace_ionq.png'), dpi=300)
    plt.close()

    # 12. Fidelity Trace (AQT)
    plt.figure(figsize=(10,4))
    plt.plot(df_aqt.index[:100], df_aqt['true_fidelity'][:100], marker='.', color='orange')
    plt.axhline(0.85, color='r', linestyle='--')
    plt.title('Fidelity Trace (AQT - First 100 steps)')
    plt.xlabel('Timestep')
    plt.ylabel('Fidelity')
    plt.savefig(os.path.join(output_figures_dir, '12_fidelity_timeseries_trace_aqt.png'), dpi=300)
    plt.close()

    # ------------------ TABLES ------------------
    # 01. RTT Summary Stats
    df_rtt_desc = df_ionq[['rtt']].describe()
    df_rtt_desc.to_csv(os.path.join(output_tables_dir, '01_rtt_summary_stats.csv'))

    # 02. Fidelity Summary (IonQ)
    df_fid_desc_ionq = df_ionq[['true_fidelity']].describe()
    df_fid_desc_ionq.to_csv(os.path.join(output_tables_dir, '02_fidelity_summary_ionq.csv'))

    # 03. Fidelity Summary (AQT)
    df_fid_desc_aqt = df_aqt[['true_fidelity']].describe()
    df_fid_desc_aqt.to_csv(os.path.join(output_tables_dir, '03_fidelity_summary_aqt.csv'))

    # 04. Policy Actions (IonQ)
    df_actions_ionq = pd.DataFrame({
        'Adaptive': df_ionq['adaptive_action'].value_counts(),
        'Static': df_ionq['static_action'].value_counts()
    }).fillna(0)
    df_actions_ionq.to_csv(os.path.join(output_tables_dir, '04_policy_actions_summary_ionq.csv'))

    # 05. Policy Actions (AQT)
    df_actions_aqt = pd.DataFrame({
        'Adaptive': df_aqt['adaptive_action'].value_counts(),
        'Static': df_aqt['static_action'].value_counts()
    }).fillna(0)
    df_actions_aqt.to_csv(os.path.join(output_tables_dir, '05_policy_actions_summary_aqt.csv'))

    # 06. Error Metrics (IonQ)
    df_err_ionq = pd.DataFrame({
        'Metric': ['Zombie Keys Exposed', 'Unnecessary Flushes'],
        'Adaptive': [df_ionq['zombie_adaptive'].sum(), df_ionq['unnecessary_flush_adaptive'].sum()],
        'Static': [df_ionq['zombie_static'].sum(), df_ionq['unnecessary_flush_static'].sum()]
    })
    df_err_ionq.to_csv(os.path.join(output_tables_dir, '06_error_metrics_ionq.csv'), index=False)

    # 07. Error Metrics (AQT)
    df_err_aqt = pd.DataFrame({
        'Metric': ['Zombie Keys Exposed', 'Unnecessary Flushes'],
        'Adaptive': [df_aqt['zombie_adaptive'].sum(), df_aqt['unnecessary_flush_adaptive'].sum()],
        'Static': [df_aqt['zombie_static'].sum(), df_aqt['unnecessary_flush_static'].sum()]
    })
    df_err_aqt.to_csv(os.path.join(output_tables_dir, '07_error_metrics_aqt.csv'), index=False)

    # 08. Top 10 Highest RTT
    df_top_rtt = df_ionq.nlargest(10, 'rtt')[['timestamp', 'rtt']]
    df_top_rtt.to_csv(os.path.join(output_tables_dir, '08_top_10_highest_rtt.csv'), index=False)

    # 09. Top 10 Lowest Fidelity (IonQ)
    df_top_fid_ionq = df_ionq.nsmallest(10, 'true_fidelity')[['timestamp', 'rtt', 'true_fidelity']]
    df_top_fid_ionq.to_csv(os.path.join(output_tables_dir, '09_top_10_lowest_fidelity_ionq.csv'), index=False)

    # 10. Top 10 Lowest Fidelity (AQT)
    df_top_fid_aqt = df_aqt.nsmallest(10, 'true_fidelity')[['timestamp', 'rtt', 'true_fidelity']]
    df_top_fid_aqt.to_csv(os.path.join(output_tables_dir, '10_top_10_lowest_fidelity_aqt.csv'), index=False)

    # 11. Zombie Events Sample (Static AQT)
    df_zombies = df_aqt[df_aqt['zombie_static'] == True].head(10)[['timestamp', 'rtt', 'true_fidelity', 'static_action']]
    df_zombies.to_csv(os.path.join(output_tables_dir, '11_zombie_events_log_static_aqt.csv'), index=False)

    print("Reports generated successfully!")

if __name__ == "__main__":
    base_dir = os.path.dirname(os.path.dirname(__file__))
    results_dir = os.path.join(base_dir, 'outputs')
    generate_reports(results_dir, os.path.join(base_dir, 'outputs/figures'), os.path.join(base_dir, 'outputs/tables'))
