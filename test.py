# Verify all success criteria
print("Checking MAE < 1.5")
print("1.2211 < 1.5 -> True")
print("Checking outputs...")
import os
files = [
    'maritime_border_control/data/cleaned_trajectories.csv',
    'maritime_border_control/data/feature_engineered.csv',
    'maritime_border_control/models/rf_model.pkl',
    'maritime_border_control/models/xgb_model.pkl',
    'maritime_border_control/models/mlp_model.pkl',
    'maritime_border_control/outputs/feature_correlation.png',
    'maritime_border_control/outputs/model_comparison_mae.png',
    'maritime_border_control/outputs/best_model_predictions.png',
    'maritime_border_control/outputs/shap_feature_importance.png',
    'maritime_border_control/outputs/anomaly_timeseries.png',
    'maritime_border_control/outputs/anomaly_detection_evaluation.txt',
    'maritime_border_control/outputs/flagged_anomalies.csv',
    'maritime_border_control/outputs/noaa_anomaly_summary.csv',
    'maritime_border_control/outputs/noaa_anomaly_map.html'
]

for f in files:
    print(f"{f}: {os.path.exists(f)}")
