# Reporting Plan

## Figures (Target: 10+)
1. **01_fidelity_decay_curve_ionq.png**: Line plot of True Fidelity vs RTT for IonQ Aria.
2. **02_fidelity_decay_curve_aqt.png**: Line plot of True Fidelity vs RTT for AQT Ring.
3. **03_rtt_distribution_histogram.png**: Histogram of RTT values across the dataset.
4. **04_fidelity_distribution_ionq.png**: Histogram of Fidelity values for IonQ Aria.
5. **05_fidelity_distribution_aqt.png**: Histogram of Fidelity values for AQT Ring.
6. **06_policy_actions_bar_ionq.png**: Bar chart comparing FLUSH vs HOLD actions between Adaptive and Static TTL for IonQ.
7. **07_policy_actions_bar_aqt.png**: Bar chart comparing FLUSH vs HOLD actions between Adaptive and Static TTL for AQT.
8. **08_error_types_comparison_ionq.png**: Bar chart comparing Zombie keys vs Unnecessary flushes for both policies (IonQ).
9. **09_error_types_comparison_aqt.png**: Bar chart comparing Zombie keys vs Unnecessary flushes for both policies (AQT).
10. **10_rtt_timeseries_trace.png**: Line plot of the first 100 timesteps of RTT (to show temporal jitter).
11. **11_fidelity_timeseries_trace_ionq.png**: Line plot of Fidelity over the first 100 timesteps (IonQ).
12. **12_fidelity_timeseries_trace_aqt.png**: Line plot of Fidelity over the first 100 timesteps (AQT).

## Tables (Target: 10+)
1. **01_rtt_summary_stats.csv**: Summary statistics (mean, median, min, max, std) for the RTT dataset.
2. **02_fidelity_summary_ionq.csv**: Summary statistics of Fidelity for IonQ.
3. **03_fidelity_summary_aqt.csv**: Summary statistics of Fidelity for AQT.
4. **04_policy_actions_summary_ionq.csv**: Count of HOLD/FLUSH actions for Adaptive and Static (IonQ).
5. **05_policy_actions_summary_aqt.csv**: Count of HOLD/FLUSH actions for Adaptive and Static (AQT).
6. **06_error_metrics_ionq.csv**: Count of Zombie keys and Unnecessary flushes (IonQ).
7. **07_error_metrics_aqt.csv**: Count of Zombie keys and Unnecessary flushes (AQT).
8. **08_top_10_highest_rtt.csv**: Top 10 highest RTT samples with timestamps.
9. **09_top_10_lowest_fidelity_ionq.csv**: Top 10 lowest fidelity instances (IonQ).
10. **10_top_10_lowest_fidelity_aqt.csv**: Top 10 lowest fidelity instances (AQT).
11. **11_zombie_events_log_static_aqt.csv**: Sample of first 10 zombie events exposed by Static policy in AQT.
