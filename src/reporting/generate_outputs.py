import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import os
import json

from src.reporting.plot_style import apply, COLORS

apply()

# Data loading
df = pd.read_csv('/app/src/outputs/raw/simulation_results.csv')
df['timestamp'] = pd.to_datetime(df['timestamp'], format='ISO8601')

manifest = {}
def add_manifest(file_name, source, desc):
    manifest[file_name] = {"source": source, "description": desc}

os.makedirs('/app/src/outputs/figures', exist_ok=True)
os.makedirs('/app/src/outputs/tables', exist_ok=True)

# 1. fidelity_decay_vs_threshold.png
def fig_1():
    fig, ax = plt.subplots()
    t = np.linspace(0, 0.2, 500)

    ionq_t2 = 1.0
    aqt_t2 = 0.05

    ionq_f = 0.5 + 0.5 * np.exp(-t / ionq_t2)
    aqt_f = 0.5 + 0.5 * np.exp(-t / aqt_t2)

    ax.plot(t, ionq_f, label='IonQ Aria (T2=1.0s)', color=COLORS['primary'])
    ax.plot(t, aqt_f, label='AQT (T2=0.05s)', color=COLORS['secondary'])
    ax.axhline(0.85, color=COLORS['neutral'], linestyle='--', label='Threshold (0.85)')

    ax.set_xlabel('Latency / RTT (s)')
    ax.set_ylabel('Fidelity F(t)')
    ax.set_title('Fidelity Decay vs Threshold')
    ax.legend()
    plt.tight_layout()
    plt.savefig('/app/src/outputs/figures/fidelity_decay_vs_threshold.png')
    plt.close()
    add_manifest('fidelity_decay_vs_threshold.png', 'model/fidelity.py logic', 'Theoretical F(t) over time with threshold.')
fig_1()

# 2. flush_hold_comparison_adaptive_vs_static.png
def fig_2():
    agg = df.groupby(['t2_regime', 'policy', 'action']).size().unstack(fill_value=0).reset_index()
    # we need FLUSH and HOLD
    if 'FLUSH' not in agg.columns: agg['FLUSH'] = 0
    if 'HOLD' not in agg.columns: agg['HOLD'] = 0

    labels = []
    flush_counts = []
    hold_counts = []
    for _, row in agg.iterrows():
        labels.append(f"{row['t2_regime']}\n{row['policy']}")
        flush_counts.append(row['FLUSH'])
        hold_counts.append(row['HOLD'])

    x = np.arange(len(labels))
    width = 0.35

    fig, ax = plt.subplots()
    ax.bar(x - width/2, flush_counts, width, label='FLUSH', color=COLORS['secondary'])
    ax.bar(x + width/2, hold_counts, width, label='HOLD', color=COLORS['primary'])

    ax.set_ylabel('Count')
    ax.set_title('FLUSH/HOLD Counts: Adaptive vs Static')
    ax.set_xticks(x)
    ax.set_xticklabels(labels)
    ax.legend()
    plt.tight_layout()
    plt.savefig('/app/src/outputs/figures/flush_hold_comparison_adaptive_vs_static.png')
    plt.close()
    add_manifest('flush_hold_comparison_adaptive_vs_static.png', 'outputs/raw/simulation_results.csv', 'Grouped bar of FLUSH/HOLD counts.')
fig_2()

# 3. zombie_key_exposure_rate.png
def fig_3():
    # Zombie: action == HOLD and fidelity < 0.85
    # Early flush: action == FLUSH and fidelity >= 0.85

    df['is_zombie'] = (df['action'] == 'HOLD') & (df['fidelity'] < 0.85)
    df['is_early'] = (df['action'] == 'FLUSH') & (df['fidelity'] >= 0.85)

    agg = df.groupby(['t2_regime', 'policy']).agg({
        'is_zombie': 'mean',
        'is_early': 'mean'
    }).reset_index()

    agg['is_zombie'] *= 100
    agg['is_early'] *= 100

    fig, ax = plt.subplots()
    for _, row in agg.iterrows():
        label = f"{row['t2_regime']} {row['policy']}"
        ax.scatter(row['is_early'], row['is_zombie'], label=label, s=100)
        ax.annotate(label, (row['is_early'], row['is_zombie']))

    ax.set_xlabel('Premature Flushes (%)')
    ax.set_ylabel('Zombie Key Exposures (%)')
    ax.set_title('Security vs Efficiency Tradeoff')
    # ax.legend()
    plt.tight_layout()
    plt.savefig('/app/src/outputs/figures/zombie_key_exposure_rate.png')
    plt.close()
    add_manifest('zombie_key_exposure_rate.png', 'outputs/raw/simulation_results.csv', 'Scatter of zombie exposure vs premature flush rates.')
fig_3()

# 4. rtt_distribution_histogram.png
def fig_4():
    # RTTs are identical across policies, take one slice
    rtt_samples = df[df['policy'] == 'Adaptive']['rtt_seconds'] * 1000 # ms

    fig, ax = plt.subplots()
    ax.hist(rtt_samples, bins=50, color=COLORS['tertiary'], edgecolor='black')
    ax.set_xlabel('RTT (ms)')
    ax.set_ylabel('Frequency')
    ax.set_title('RTT Distribution')
    plt.tight_layout()
    plt.savefig('/app/src/outputs/figures/rtt_distribution_histogram.png')
    plt.close()
    add_manifest('rtt_distribution_histogram.png', 'outputs/raw/simulation_results.csv', 'Histogram of raw RTT samples.')
fig_4()

# 5. fidelity_at_flush_distribution.png
def fig_5():
    flushes = df[df['action'] == 'FLUSH']

    if len(flushes) == 0:
        fig, ax = plt.subplots()
        ax.text(0.5, 0.5, "No FLUSH events", ha='center')
        plt.savefig('/app/src/outputs/figures/fidelity_at_flush_distribution.png')
        plt.close()
    else:
        fig, ax = plt.subplots()
        for p in ['Adaptive', 'Static']:
            sub = flushes[flushes['policy'] == p]['fidelity']
            if len(sub) > 0:
                ax.hist(sub, bins=20, alpha=0.5, label=p)
        ax.set_xlabel('Fidelity at FLUSH')
        ax.set_ylabel('Frequency')
        ax.set_title('Fidelity at Flush Distribution')
        ax.legend()
        plt.tight_layout()
        plt.savefig('/app/src/outputs/figures/fidelity_at_flush_distribution.png')
        plt.close()
    add_manifest('fidelity_at_flush_distribution.png', 'outputs/raw/simulation_results.csv', 'Distribution of fidelity when FLUSH is triggered.')
fig_5()

# 6. flush_timing_ionq_vs_aqt.png
def fig_6():
    # Treat simulation as time series and get flush frequency per second

    fig, ax = plt.subplots()
    for regime, color in zip(['IonQ_Aria', 'AQT'], [COLORS['primary'], COLORS['secondary']]):
        sub = df[(df['t2_regime'] == regime) & (df['policy'] == 'Adaptive')].copy()
        sub.set_index('timestamp', inplace=True)
        # Resample to 1-second bins and count flushes
        flushes_per_sec = (sub['action'] == 'FLUSH').resample('1s').sum()

        ax.plot(flushes_per_sec.index, flushes_per_sec.values, label=regime, color=color, alpha=0.7)

    ax.set_xlabel('Time')
    ax.set_ylabel('Flushes per second')
    ax.set_title('Flush Frequency (Adaptive Policy)')
    ax.legend()
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.savefig('/app/src/outputs/figures/flush_timing_ionq_vs_aqt.png')
    plt.close()
    add_manifest('flush_timing_ionq_vs_aqt.png', 'outputs/raw/simulation_results.csv', 'Flush frequency over time for IonQ vs AQT.')
fig_6()

# 7. buffer_efficiency_comparison.png
def fig_7():
    # "HOLD duration distribution" -> we just plot the fraction of time we are HOLDING
    # Let's plot HOLD counts since each timestep is uniform
    agg = df[df['action'] == 'HOLD'].groupby(['t2_regime', 'policy']).size()

    if len(agg) == 0:
        fig, ax = plt.subplots()
        ax.text(0.5, 0.5, "No HOLD events", ha='center')
        plt.savefig('/app/src/outputs/figures/buffer_efficiency_comparison.png')
        plt.close()
        add_manifest('buffer_efficiency_comparison.png', 'outputs/raw/simulation_results.csv', 'HOLD counts comparison.')
        return

    agg = agg.reset_index(name='hold_count')

    fig, ax = plt.subplots()
    labels = [f"{r['t2_regime']}\n{r['policy']}" for _, r in agg.iterrows()]
    ax.bar(labels, agg['hold_count'], color=COLORS['tertiary'])
    ax.set_ylabel('Total Timesteps in HOLD')
    ax.set_title('Buffer Efficiency (HOLD Duration)')
    plt.tight_layout()
    plt.savefig('/app/src/outputs/figures/buffer_efficiency_comparison.png')
    plt.close()
    add_manifest('buffer_efficiency_comparison.png', 'outputs/raw/simulation_results.csv', 'HOLD duration distribution proxy.')
fig_7()

# 8. cumulative_flush_events_over_time.png
def fig_8():
    fig, ax = plt.subplots()

    for regime in ['IonQ_Aria', 'AQT']:
        for policy in ['Adaptive', 'Static']:
            sub = df[(df['t2_regime'] == regime) & (df['policy'] == policy)].copy()
            sub = sub.sort_values('timestamp')
            sub['flush_cum'] = (sub['action'] == 'FLUSH').cumsum()
            ax.plot(sub['timestamp'], sub['flush_cum'], label=f"{regime}-{policy}")

    ax.set_xlabel('Time')
    ax.set_ylabel('Cumulative FLUSH Events')
    ax.set_title('Cumulative Flush Events Over Time')
    ax.legend()
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.savefig('/app/src/outputs/figures/cumulative_flush_events_over_time.png')
    plt.close()
    add_manifest('cumulative_flush_events_over_time.png', 'outputs/raw/simulation_results.csv', 'Cumulative flushes over time.')
fig_8()

# 9. rtt_vs_fidelity_scatter.png
def fig_9():
    fig, ax = plt.subplots()
    sub_ionq = df[df['t2_regime'] == 'IonQ_Aria'].head(500)
    sub_aqt = df[df['t2_regime'] == 'AQT'].head(500)

    ax.scatter(sub_ionq['rtt_seconds']*1000, sub_ionq['fidelity'], color=COLORS['primary'], label='IonQ Aria', alpha=0.5)
    ax.scatter(sub_aqt['rtt_seconds']*1000, sub_aqt['fidelity'], color=COLORS['secondary'], label='AQT', alpha=0.5)

    ax.set_xlabel('RTT (ms)')
    ax.set_ylabel('Fidelity')
    ax.set_title('RTT vs Fidelity (Subset)')
    ax.legend()
    plt.tight_layout()
    plt.savefig('/app/src/outputs/figures/rtt_vs_fidelity_scatter.png')
    plt.close()
    add_manifest('rtt_vs_fidelity_scatter.png', 'outputs/raw/simulation_results.csv', 'Scatter of RTT vs Fidelity colored by regime.')
fig_9()

# 10. static_ttl_threshold_miss_rate.png
def fig_10():
    # We computed 'is_zombie' (undershoots) and 'is_early' (overshoots) in fig 3
    # Let's plot this specifically for the Static policy
    static_df = df[df['policy'] == 'Static']
    agg = static_df.groupby('t2_regime').agg({
        'is_zombie': 'sum',
        'is_early': 'sum'
    }).reset_index()

    x = np.arange(len(agg))
    width = 0.35

    fig, ax = plt.subplots()
    ax.bar(x - width/2, agg['is_zombie'], width, label='Undershoot (Zombie)', color=COLORS['secondary'])
    ax.bar(x + width/2, agg['is_early'], width, label='Overshoot (Early Flush)', color=COLORS['primary'])

    ax.set_ylabel('Count')
    ax.set_title('Static TTL Misses (Overshoot vs Undershoot)')
    ax.set_xticks(x)
    ax.set_xticklabels(agg['t2_regime'])
    ax.legend()
    plt.tight_layout()
    plt.savefig('/app/src/outputs/figures/static_ttl_threshold_miss_rate.png')
    plt.close()
    add_manifest('static_ttl_threshold_miss_rate.png', 'outputs/raw/simulation_results.csv', 'Bar chart of static policy over- or under-shoots.')
fig_10()

# ----------------- TABLES (10) -----------------

# 1. policy_event_log_summary.csv
def tab_1():
    agg = df.groupby(['policy', 't2_regime']).agg({
        'action': lambda x: (x == 'FLUSH').sum(),
        'fidelity': ['mean', 'median']
    }).reset_index()
    # Flattens multi-index columns
    agg.columns = ['policy', 't2_regime', 'flush_count', 'mean_fidelity_at_flush', 'median_fidelity_at_flush']
    agg.to_csv('/app/src/outputs/tables/policy_event_log_summary.csv', index=False)
    add_manifest('policy_event_log_summary.csv', 'outputs/raw/simulation_results.csv', 'Summary of events and fidelities per policy/regime.')
tab_1()

# 2. zombie_vs_early_flush_tradeoff.csv
def tab_2():
    agg = df.groupby(['t2_regime', 'policy']).agg({
        'is_zombie': ['sum', 'mean'],
        'is_early': ['sum', 'mean']
    }).reset_index()
    agg.columns = ['t2_regime', 'policy', 'zombie_count', 'zombie_rate', 'early_flush_count', 'early_flush_rate']
    agg.to_csv('/app/src/outputs/tables/zombie_vs_early_flush_tradeoff.csv', index=False)
    add_manifest('zombie_vs_early_flush_tradeoff.csv', 'outputs/raw/simulation_results.csv', 'Security vs efficiency tradeoffs.')
tab_2()

# 3. t2_regime_comparison.csv
def tab_3():
    agg = df.groupby('t2_regime').agg({
        'rtt_seconds': 'mean',
        'action': lambda x: (x == 'FLUSH').mean()
    }).reset_index()
    agg.columns = ['t2_regime', 'mean_rtt_tolerated', 'flush_rate']
    agg.to_csv('/app/src/outputs/tables/t2_regime_comparison.csv', index=False)
    add_manifest('t2_regime_comparison.csv', 'outputs/raw/simulation_results.csv', 'Regime comparisons.')
tab_3()

# 4. rtt_summary_stats.csv
def tab_4():
    sub = df[df['policy'] == 'Adaptive'] # take one policy since RTT is identical
    stats = sub['rtt_seconds'].describe(percentiles=[.5]).reset_index()
    stats.columns = ['metric', 'value']
    stats.to_csv('/app/src/outputs/tables/rtt_summary_stats.csv', index=False)
    add_manifest('rtt_summary_stats.csv', 'outputs/raw/simulation_results.csv', 'Descriptive stats of RTT samples.')
tab_4()

# 5. fidelity_at_flush_stats.csv
def tab_5():
    sub = df[df['action'] == 'FLUSH']
    agg = sub.groupby(['t2_regime', 'policy'])['fidelity'].describe().reset_index()
    agg.to_csv('/app/src/outputs/tables/fidelity_at_flush_stats.csv', index=False)
    add_manifest('fidelity_at_flush_stats.csv', 'outputs/raw/simulation_results.csv', 'Descriptive stats of fidelity when FLUSH is triggered.')
tab_5()

# 6. sampling_assumptions.csv
def tab_6():
    res = [{
        "sampling_interval_ms": 10,
        "synthetic_timestamp_scheme": "Start at 2026-01-01, increment by interval",
        "row_count": len(df),
        "source_time_slice_count": 688 # as documented in loader
    }]
    pd.DataFrame(res).to_csv('/app/src/outputs/tables/sampling_assumptions.csv', index=False)
    add_manifest('sampling_assumptions.csv', 'data_loaders/netlatency_loader.py', 'Documented sampling assumptions.')
tab_6()

# 7. open_mct_schema_sample.csv
def tab_7():
    with open('/app/src/outputs/raw/open_mct_telemetry.json', 'r') as f:
        data = json.load(f)
    sample = pd.DataFrame(data[:20])
    sample.to_csv('/app/src/outputs/tables/open_mct_schema_sample.csv', index=False)
    add_manifest('open_mct_schema_sample.csv', 'outputs/raw/open_mct_telemetry.json', 'Sample of JSON telemetry schema.')
tab_7()

# 8. config_constants_used.csv
def tab_8():
    res = [
        {"config_key": "IonQ_Aria_T2", "value": "1.0s", "source_citation": "https://www.ionq.com/quantum-systems/aria"},
        {"config_key": "AQT_T2", "value": "0.05s", "source_citation": "https://aqt.lbl.gov/about-aqt/collaborate-with-us/aqt-capabilities/"},
        {"config_key": "Adaptive_Threshold", "value": "0.85", "source_citation": "Prompt requirement"},
        {"config_key": "Static_TTL_IonQ", "value": "0.1s", "source_citation": "simulate.py heuristic"},
        {"config_key": "Static_TTL_AQT", "value": "0.01s", "source_citation": "simulate.py heuristic"},
    ]
    pd.DataFrame(res).to_csv('/app/src/outputs/tables/config_constants_used.csv', index=False)
    add_manifest('config_constants_used.csv', 'Source Code', 'Config constants and citations.')
tab_8()

# 9. per_regime_flush_frequency.csv
def tab_9():
    agg = df.groupby(['t2_regime', 'policy']).apply(lambda x: (x['action'] == 'FLUSH').sum() / len(x)).reset_index(name='flushes_per_timestep')
    agg.to_csv('/app/src/outputs/tables/per_regime_flush_frequency.csv', index=False)
    add_manifest('per_regime_flush_frequency.csv', 'outputs/raw/simulation_results.csv', 'Flush frequency per regime and policy.')
tab_9()

# 10. data_provenance.csv
def tab_10():
    res = [{
        "repo_url": "https://github.com/uofa-rzhu3/NetLatency-Data",
        "dataset_used": "Seattle (99x99 matrices)",
        "row_count": len(df),
        "open_mct_schema_ref": "https://github.com/nasa/openmct-demo"
    }]
    pd.DataFrame(res).to_csv('/app/src/outputs/tables/data_provenance.csv', index=False)
    add_manifest('data_provenance.csv', 'Prompt requirement', 'Data provenance and references.')
tab_10()

# Write Manifest
with open("/app/src/outputs/source_manifest.json", "w") as f:
    json.dump(manifest, f, indent=4)

print(f"Generated {len([k for k in manifest if k.endswith('.png')])} figures and {len([k for k in manifest if k.endswith('.csv')])} tables.")
