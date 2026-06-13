# DRPP Extended Simulation & Empirical Study: Results Report

## Introduction
This report details the empirical evaluation and stress-testing of the Deception-Resistant Presence Proof (DRPP) protocol.

## Methodology
The protocol was simulated using a Monte Carlo approach. The cryptographic challenge-response mechanism uses an HMAC-SHA256 PRF. Liveness detection for the three proposed physical modalities (knock-pattern, capacitive touch, visual gesture) was modeled using synthetically generated data.

### Experiment Configurations
See Table T11 for the core simulation hyperparameters.

## Results

### Core Attack Probabilities
The theoretical security bound of $P_{attack} = 2^{-k}$ holds empirically under the single-guess adversary model.

![Theoretical vs Simulated](../figures/F1_theoretical_vs_simulated.png)
*Figure 1: Shows tight empirical alignment with $2^{-k}$.*

When introducing colluding adversaries, the attack probability scales linearly with the number of colluders $n$, but still decays exponentially with $k$.
![Collusion Attack](../figures/F2_collusion_probability.png)
*Figure 2: Collusion attack probability.*

### Comparison with Traditional Methods
Compared to traditional environmental-cue baseline authentication (fixed ~34% success rate), DRPP rapidly provides stronger security bounds as $k$ exceeds 2 bits.
![DRPP vs Traditional](../figures/F3_comparison.png)

### Liveness Detection & Modality Robustness
Classifiers were trained to detect spoofed actions. Random Forest models consistently outperformed Logistic Regression and showed high resilience to sensor noise up to ~15% relative jitter.
![ROC Knock](../figures/F7_roc_knock.png)
![ROC Touch](../figures/F8_roc_touch.png)
![ROC Gesture](../figures/F9_roc_gesture.png)
![Accuracy vs Noise](../figures/F14_accuracy_vs_noise.png)

### Multi-Modal Extensions
By requiring a multi-modal response (e.g., Knock AND Touch), the probability of a successful attack is drastically reduced to roughly $2^{-2k}$, assuming independent liveness channels.
![Multimodal Bar](../figures/F16_multimodal_bar.png)

### Ablation Study
Removing any of the defense layers (Cryptographic challenge, Liveness detection, Temporal variability) leads to a rapid collapse in security guarantees.
![Ablation](../figures/F18_ablation.png)

## Discussion & Limitations
The Monte Carlo simulation confirms the fundamental robustness of the DRPP protocol against standard guessing, collusion, and injection attacks when a robust liveness-detection classifier is in place.
**Limitations:** The primary limitation is the use of synthetic Gaussian data for the liveness classifiers. Future work must validate these specific classifier architectures (Random Forest) against real-world human sensor data (e.g., recorded on mobile accelerometers or capacitive arrays).

## Future Work
Directions for further research include replacing HMAC-SHA256 with quantum-resistant primitives, exploring Zero-Knowledge proofs of physical presence, and deploying the protocol in decentralized or DePIN IoT architectures.
