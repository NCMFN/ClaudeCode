# DRPP Tables Index

## T01 — drpp_attack_probability
- **Columns**: k, p_theoretical, p_simulated, ci_lo, ci_hi, n_trials

## T02 — collusion_attack_probability
- **Columns**: k, n_colluders, p_theoretical, p_simulated

## T03 — traditional_sensitivity
- **Columns**: deception_prob, p_simulated, n_trials

## T04 — modality_classifier_metrics
- **Columns**: modality, classifier, accuracy, precision, recall, f1, auc

## T05 — confusion_matrix_values
- **Columns**: modality, classifier, TN, FP, FN, TP

## T06 — latency_statistics
- **Columns**: modality, mean_s, median_s, std_s, p95_s

## T07 — accuracy_vs_noise
- **Columns**: modality, classifier, noise_level, accuracy

## T08 — multimodal_attack_probability
- **Columns**: k, single_modal, dual_modal, triple_modal

## T09 — dos_simulation
- **Columns**: time_s, requests_no_rl, requests_with_rl, blocked

## T10 — ablation_study
- **Columns**: configuration, p_attack

## T11 — simulation_config
- **Columns**: parameter, value

## T12 — related_work_comparison
- **Columns**: protocol, deception_model, physical_presence, collusion_resistance, human_centric, boundary_binding

## T13 — modality_bit_capacity
- **Columns**: modality, encoding_scheme, effective_k_range, sensor

## T14 — security_usability_matrix
- **Columns**: k, p_attack, latency_s, knock_ok, touch_ok, gesture_ok

## T15 — runtime_cost
- **Columns**: experiment, wall_clock_s, trials_per_sec

## T16 — statistical_significance
- **Columns**: k, p_simulated, ci_lo, ci_hi, std_error

## T17 — hardware_specification
- **Columns**: component, spec, cost_usd

## T18 — notation_glossary
- **Columns**: symbol, meaning

## T19 — theoretical_vs_empirical_summary
- **Columns**: experiment, theoretical, empirical

## T20 — power_estimation
- **Columns**: modality, k, active_power_mw, duration_s, energy_mj

## T21 — side_channel_mitigation
- **Columns**: attack_type, mitigation, p_attack_no_mit, p_attack_with_mit
