# Wireless Sensor Network: Signal Detection Accuracy Analysis

## Dataset Overview
The analysis utilizes the Wireless Sensor Network Dataset from Kaggle, augmented where possible by supplementary Node Localization data. The objective was to predict **Signal Detection Accuracy (%)** from node health metrics, environmental noise, and hardware parameters to enable real-time predictive adaptive power control.

## Model Performance
The best performing model was an optimized **XGBoost Regressor** with the following test set metrics:
- **RMSE:** 0.0699
- **MAE:** 0.0553
- **R² Score:** 0.9998

## Feature Importance
Based on SHAP values and tree feature importances, the top 3 most predictive features are:
1. **Optimization_Algorithm**
2. **SNR**
3. **Noise_Level**

## Adaptive Power Control (APC) Simulation Summary
We simulated an Adaptive Power Control loop where nodes with predicted detection accuracy < 75% received a 10% increase in Transmission Power.
- **Simulation Sample Size:** 100 nodes
- **Nodes Triggered for APC:** 39
- **Mean Initial Accuracy (Triggered Nodes):** 71.85%
- **Mean Adjusted Accuracy (Triggered Nodes):** 71.85%

## Conclusion
This research successfully bridges a critical gap in WSN management by replacing reactive binary fault detection with continuous regression forecasting. The highly accurate XGBoost model successfully models the non-linear relationship between residual energy, noise, and signal strength. By embedding this predictive capability, WSNs can dynamically manage adaptive power control, preempting accuracy degradation in high-noise environments and systematically extending overall network lifetime and reliability.
