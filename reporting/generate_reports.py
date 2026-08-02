import os
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np

def generate_reports(results_dir: str, output_figures_dir: str, output_tables_dir: str):
    os.makedirs(output_figures_dir, exist_ok=True)
    os.makedirs(output_tables_dir, exist_ok=True)

    # Track generated files for summary
    generated_figures = []
    generated_tables = []

    def save_fig(fig, filename):
        path = os.path.join(output_figures_dir, filename)
        fig.savefig(path, dpi=300, bbox_inches='tight')
        plt.close(fig)
        generated_figures.append(path)

    def save_table(df, filename, index=False):
        path = os.path.join(output_tables_dir, filename)
        df.to_csv(path, index=index)
        generated_tables.append(path)

    # Load data
    ionq_path = os.path.join(results_dir, 'simulation_results_ionq_aria.csv')
    aqt_path = os.path.join(results_dir, 'simulation_results_aqt_ring.csv')

    if not os.path.exists(ionq_path) or not os.path.exists(aqt_path):
        print("Required simulation data missing. Please run `python simulate.py` first.")
        return

    df_ionq = pd.read_csv(ionq_path)
    df_aqt = pd.read_csv(aqt_path)

    # Ensure boolean columns are strictly boolean for correlation
    bool_cols = ['zombie_adaptive', 'unnecessary_flush_adaptive', 'zombie_static', 'unnecessary_flush_static']
    for col in bool_cols:
        df_ionq[col] = df_ionq[col].astype(float)
        df_aqt[col] = df_aqt[col].astype(float)

    # ------------------ FIGURES ------------------
    # 01. Fidelity vs RTT (IonQ)
    fig1 = plt.figure(figsize=(8,5))
    df_sorted_ionq = df_ionq.sort_values(by='rtt')
    plt.plot(df_sorted_ionq['rtt'], df_sorted_ionq['true_fidelity'], label='IonQ Aria')
    plt.axhline(0.85, color='r', linestyle='--', label='Threshold')
    plt.title('True Fidelity vs RTT (IonQ Aria)')
    plt.xlabel('RTT (s)')
    plt.ylabel('Fidelity')
    plt.legend()
    save_fig(fig1, '01_fidelity_decay_curve_ionq.png')

    # 02. Fidelity vs RTT (AQT)
    fig2 = plt.figure(figsize=(8,5))
    df_sorted_aqt = df_aqt.sort_values(by='rtt')
    plt.plot(df_sorted_aqt['rtt'], df_sorted_aqt['true_fidelity'], label='AQT Ring', color='orange')
    plt.axhline(0.85, color='r', linestyle='--', label='Threshold')
    plt.title('True Fidelity vs RTT (AQT Ring)')
    plt.xlabel('RTT (s)')
    plt.ylabel('Fidelity')
    plt.legend()
    save_fig(fig2, '02_fidelity_decay_curve_aqt.png')

    # 03. RTT Histogram
    fig3 = plt.figure(figsize=(8,5))
    sns.histplot(df_ionq['rtt'], bins=30, kde=True, color='gray')
    plt.title('RTT Distribution')
    plt.xlabel('RTT (s)')
    plt.ylabel('Frequency')
    save_fig(fig3, '03_rtt_distribution_histogram.png')

    # 04. Fidelity Distribution (IonQ)
    fig4 = plt.figure(figsize=(8,5))
    sns.histplot(df_ionq['true_fidelity'], bins=30, kde=True, color='blue')
    plt.axvline(0.85, color='r', linestyle='--')
    plt.title('Fidelity Distribution (IonQ Aria)')
    plt.xlabel('Fidelity')
    plt.ylabel('Frequency')
    save_fig(fig4, '04_fidelity_distribution_ionq.png')

    # 05. Fidelity Distribution (AQT)
    fig5 = plt.figure(figsize=(8,5))
    sns.histplot(df_aqt['true_fidelity'], bins=30, kde=True, color='orange')
    plt.axvline(0.85, color='r', linestyle='--')
    plt.title('Fidelity Distribution (AQT Ring)')
    plt.xlabel('Fidelity')
    plt.ylabel('Frequency')
    save_fig(fig5, '05_fidelity_distribution_aqt.png')

    # 06. Policy Actions Bar (IonQ)
    fig6, ax = plt.subplots(figsize=(8,5))
    adaptive_counts = df_ionq['adaptive_action'].value_counts()
    static_counts = df_ionq['static_action'].value_counts()
    labels = ['HOLD', 'FLUSH']
    x = np.arange(len(labels))
    width = 0.35
    ax.bar(x - width/2, [adaptive_counts.get(l, 0) for l in labels], width, label='Adaptive')
    ax.bar(x + width/2, [static_counts.get(l, 0) for l in labels], width, label='Static')
    ax.set_xticks(x)
    ax.set_xticklabels(labels)
    ax.set_ylabel('Count')
    ax.set_title('Policy Actions Comparison (IonQ Aria)')
    ax.legend()
    save_fig(fig6, '06_policy_actions_bar_ionq.png')

    # 07. Policy Actions Bar (AQT)
    fig7, ax = plt.subplots(figsize=(8,5))
    adaptive_counts = df_aqt['adaptive_action'].value_counts()
    static_counts = df_aqt['static_action'].value_counts()
    ax.bar(x - width/2, [adaptive_counts.get(l, 0) for l in labels], width, label='Adaptive', color='orange')
    ax.bar(x + width/2, [static_counts.get(l, 0) for l in labels], width, label='Static', color='brown')
    ax.set_xticks(x)
    ax.set_xticklabels(labels)
    ax.set_ylabel('Count')
    ax.set_title('Policy Actions Comparison (AQT Ring)')
    ax.legend()
    save_fig(fig7, '07_policy_actions_bar_aqt.png')

    # 08. Error Types (IonQ)
    fig8, ax = plt.subplots(figsize=(8,5))
    err_labels = ['Zombie Keys Exposed', 'Unnecessary Flushes']
    adaptive_errs = [df_ionq['zombie_adaptive'].sum(), df_ionq['unnecessary_flush_adaptive'].sum()]
    static_errs = [df_ionq['zombie_static'].sum(), df_ionq['unnecessary_flush_static'].sum()]
    x2 = np.arange(len(err_labels))
    ax.bar(x2 - width/2, adaptive_errs, width, label='Adaptive')
    ax.bar(x2 + width/2, static_errs, width, label='Static')
    ax.set_xticks(x2)
    ax.set_xticklabels(err_labels)
    ax.set_ylabel('Count')
    ax.set_title('Error Types (IonQ Aria)')
    ax.legend()
    save_fig(fig8, '08_error_types_comparison_ionq.png')

    # 09. Error Types (AQT)
    fig9, ax = plt.subplots(figsize=(8,5))
    adaptive_errs = [df_aqt['zombie_adaptive'].sum(), df_aqt['unnecessary_flush_adaptive'].sum()]
    static_errs = [df_aqt['zombie_static'].sum(), df_aqt['unnecessary_flush_static'].sum()]
    ax.bar(x2 - width/2, adaptive_errs, width, label='Adaptive', color='orange')
    ax.bar(x2 + width/2, static_errs, width, label='Static', color='brown')
    ax.set_xticks(x2)
    ax.set_xticklabels(err_labels)
    ax.set_ylabel('Count')
    ax.set_title('Error Types (AQT Ring)')
    ax.legend()
    save_fig(fig9, '09_error_types_comparison_aqt.png')

    # 10. RTT Trace
    fig10 = plt.figure(figsize=(10,4))
    plt.plot(df_ionq.index[:100], df_ionq['rtt'][:100], marker='.', color='black')
    plt.title('RTT Time Series Trace (First 100 steps)')
    plt.xlabel('Timestep')
    plt.ylabel('RTT (s)')
    save_fig(fig10, '10_rtt_timeseries_trace.png')

    # 11. Fidelity Trace (IonQ)
    fig11 = plt.figure(figsize=(10,4))
    plt.plot(df_ionq.index[:100], df_ionq['true_fidelity'][:100], marker='.')
    plt.axhline(0.85, color='r', linestyle='--')
    plt.title('Fidelity Trace (IonQ - First 100 steps)')
    plt.xlabel('Timestep')
    plt.ylabel('Fidelity')
    save_fig(fig11, '11_fidelity_timeseries_trace_ionq.png')

    # 12. Fidelity Trace (AQT)
    fig12 = plt.figure(figsize=(10,4))
    plt.plot(df_aqt.index[:100], df_aqt['true_fidelity'][:100], marker='.', color='orange')
    plt.axhline(0.85, color='r', linestyle='--')
    plt.title('Fidelity Trace (AQT - First 100 steps)')
    plt.xlabel('Timestep')
    plt.ylabel('Fidelity')
    save_fig(fig12, '12_fidelity_timeseries_trace_aqt.png')

    # 13. Correlation Heatmap (IonQ)
    numeric_ionq = df_ionq.select_dtypes(include=[np.number])
    fig13 = plt.figure(figsize=(8,6))
    sns.heatmap(numeric_ionq.corr(), annot=True, cmap='coolwarm', fmt=".2f")
    plt.title('Correlation Heatmap (IonQ Aria)')
    save_fig(fig13, '13_correlation_heatmap_ionq.png')

    # 14. Correlation Heatmap (AQT)
    numeric_aqt = df_aqt.select_dtypes(include=[np.number])
    fig14 = plt.figure(figsize=(8,6))
    sns.heatmap(numeric_aqt.corr(), annot=True, cmap='coolwarm', fmt=".2f")
    plt.title('Correlation Heatmap (AQT Ring)')
    save_fig(fig14, '14_correlation_heatmap_aqt.png')

    # ------------------ TABLES ------------------
    # 01. RTT Summary Stats
    df_rtt_desc = df_ionq[['rtt']].describe().T
    df_rtt_desc['missing_%'] = df_ionq['rtt'].isnull().mean() * 100
    save_table(df_rtt_desc, '01_rtt_summary_stats.csv', index=True)

    # 02. Fidelity Summary (IonQ)
    df_fid_desc_ionq = df_ionq[['true_fidelity']].describe().T
    df_fid_desc_ionq['missing_%'] = df_ionq['true_fidelity'].isnull().mean() * 100
    save_table(df_fid_desc_ionq, '02_fidelity_summary_ionq.csv', index=True)

    # 03. Fidelity Summary (AQT)
    df_fid_desc_aqt = df_aqt[['true_fidelity']].describe().T
    df_fid_desc_aqt['missing_%'] = df_aqt['true_fidelity'].isnull().mean() * 100
    save_table(df_fid_desc_aqt, '03_fidelity_summary_aqt.csv', index=True)

    # 04. Policy Actions (IonQ)
    df_actions_ionq = pd.DataFrame({
        'Adaptive': df_ionq['adaptive_action'].value_counts(),
        'Static': df_ionq['static_action'].value_counts()
    }).fillna(0)
    save_table(df_actions_ionq, '04_policy_actions_summary_ionq.csv', index=True)

    # 05. Policy Actions (AQT)
    df_actions_aqt = pd.DataFrame({
        'Adaptive': df_aqt['adaptive_action'].value_counts(),
        'Static': df_aqt['static_action'].value_counts()
    }).fillna(0)
    save_table(df_actions_aqt, '05_policy_actions_summary_aqt.csv', index=True)

    # 06. Error Metrics (IonQ)
    df_err_ionq = pd.DataFrame({
        'Metric': ['Zombie Keys Exposed', 'Unnecessary Flushes'],
        'Adaptive': [df_ionq['zombie_adaptive'].sum(), df_ionq['unnecessary_flush_adaptive'].sum()],
        'Static': [df_ionq['zombie_static'].sum(), df_ionq['unnecessary_flush_static'].sum()]
    })
    save_table(df_err_ionq, '06_error_metrics_ionq.csv')

    # 07. Error Metrics (AQT)
    df_err_aqt = pd.DataFrame({
        'Metric': ['Zombie Keys Exposed', 'Unnecessary Flushes'],
        'Adaptive': [df_aqt['zombie_adaptive'].sum(), df_aqt['unnecessary_flush_adaptive'].sum()],
        'Static': [df_aqt['zombie_static'].sum(), df_aqt['unnecessary_flush_static'].sum()]
    })
    save_table(df_err_aqt, '07_error_metrics_aqt.csv')

    # 08. Top 10 Highest RTT
    df_top_rtt = df_ionq.nlargest(10, 'rtt')[['timestamp', 'rtt']]
    save_table(df_top_rtt, '08_top_10_highest_rtt.csv')

    # 09. Top 10 Lowest Fidelity (IonQ)
    df_top_fid_ionq = df_ionq.nsmallest(10, 'true_fidelity')[['timestamp', 'rtt', 'true_fidelity']]
    save_table(df_top_fid_ionq, '09_top_10_lowest_fidelity_ionq.csv')

    # 10. Top 10 Lowest Fidelity (AQT)
    df_top_fid_aqt = df_aqt.nsmallest(10, 'true_fidelity')[['timestamp', 'rtt', 'true_fidelity']]
    save_table(df_top_fid_aqt, '10_top_10_lowest_fidelity_aqt.csv')

    # 11. Zombie Events Sample (Static AQT)
    df_zombies = df_aqt[df_aqt['zombie_static'] == 1].head(10)[['timestamp', 'rtt', 'true_fidelity', 'static_action']]
    save_table(df_zombies, '11_zombie_events_log_static_aqt.csv')

    # 12. Data Quality Report
    dq = pd.DataFrame({
        'Column': df_ionq.columns,
        'Dtype': df_ionq.dtypes.astype(str),
        'Null_Count': df_ionq.isnull().sum(),
        'Unique_Count': df_ionq.nunique()
    })
    save_table(dq, '12_data_quality_report.csv')

    # 13. Correlation Matrix Table (AQT)
    save_table(numeric_aqt.corr(), '13_correlation_matrix_aqt.csv', index=True)

    # ------------------ SUMMARY ------------------
    print(f"\n--- REPORTING SUMMARY ---")
    print(f"Successfully generated {len(generated_figures)} figures:")
    for f in generated_figures:
        print(f"  - {f}")

    print(f"\nSuccessfully generated {len(generated_tables)} tables:")
    for t in generated_tables:
        print(f"  - {t}")

    print("\nNote: All requested assets have been successfully created from the pipeline output.")

if __name__ == "__main__":
    base_dir = os.path.dirname(os.path.dirname(__file__))
    results_dir = os.path.join(base_dir, 'outputs')
    generate_reports(results_dir, os.path.join(base_dir, 'outputs/figures'), os.path.join(base_dir, 'outputs/tables'))
