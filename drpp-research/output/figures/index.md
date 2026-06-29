# DRPP Figures Index

## F01 — DRPP Attack Probability vs k
![F01](F01_drpp_attack_probability_vs_k.png)
Theoretical 2^-k bound vs Monte Carlo simulated P_attack (10,000 trials per k, with 95% Wilson confidence interval shading), k = 1–20.

## F02 — Collusion Attack vs k
![F02](F02_collusion_attack_vs_k.png)
Attack probability vs k for various numbers of colluders.

## F03 — Full Comparison
![F03](F03_full_comparison.png)
Comparison of DRPP, Collusion (n=2), and Traditional baselines.

## F04 — Attack Probability Contour (k vs n)
![F04](F04_3d_surface_attack_k_n.png)
3D surface contour showing attack probability across k and n.

## F05 — Heatmap of Collusion Success
![F05](F05_heatmap_collusion_k_n.png)
Grid heatmap representing the success probability of collusion attacks.

## F06 — Security vs Usability Tradeoff
![F06](F06_security_usability_tradeoff.png)
Dual Y-axis chart showing P_attack vs estimated system latency.

## F07 — ROC Curve: Knock
![F07](F07_roc_knock.png)
Receiver Operating Characteristic for the Knock modality.

## F08 — ROC Curve: Touch
![F08](F08_roc_touch.png)
Receiver Operating Characteristic for the Touch modality.

## F09 — ROC Curve: Gesture
![F09](F09_roc_gesture.png)
Receiver Operating Characteristic for the Gesture modality.

## F10 — Combined Confusion Matrix
![F10](F10_confusion_matrix_combined.png)
2x2 heatmap of confusion matrix values across combined modalities.

## F11 — Feature Histograms
![F11](F11_feature_histograms.png)
Distribution of legitimate vs spoofed features per modality.

## F12 — Latency Boxplot
![F12](F12_latency_boxplot.png)
Box-and-whisker plot of authentication latencies per modality.

## F13 — DET Curve
![F13](F13_det_curve.png)
Detection Error Tradeoff (FAR vs FRR) across modalities.

## F14 — Accuracy vs Noise Level
![F14](F14_accuracy_vs_noise.png)
Accuracy degradation across different modalities and classifiers as noise increases.

## F15 — Monte Carlo Convergence
![F15](F15_monte_carlo_convergence.png)
Simulation convergence towards theoretical bound over increasing trial counts.

## F16 — Multi-modal Attack Probability
![F16](F16_multimodal_bar.png)
Grouped bar chart showing attack probabilities for single, dual, and triple modal configurations.

## F17 — DoS Simulation
![F17](F17_dos_simulation.png)
Cumulative requests over time under simulated DoS attack with and without rate limiting.

## F18 — Ablation Study
![F18](F18_ablation_study.png)
Impact on attack probability when removing different DRPP components.

## F19 — Radar Comparison
![F19](F19_radar_comparison.png)
Qualitative assessment comparison using a spider/radar chart.

## F20 — Sequence Diagram
![F20](F20_sequence_diagram.png)
Drawn sequence diagram showing DRPP authentication flow.

## F21 — Architecture Diagram
![F21](F21_architecture_diagram.png)
System architecture map and interactions.

## F22 — CDF of Guesses
![F22](F22_cdf_guesses.png)
Cumulative distribution function showing probability of success within N guesses for various k.
