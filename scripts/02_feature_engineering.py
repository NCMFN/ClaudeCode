import pandas as pd
import numpy as np
import yaml
import os
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.preprocessing import RobustScaler
import joblib

with open("config.yaml", "r") as f:
    config = yaml.safe_load(f)

raw_dir = config['data']['raw_dir']
processed_dir = config['data']['processed_dir']
tables_dir = config['data']['tables_dir']
figures_dir = config['data']['figures_dir']
reports_dir = config['data']['reports_dir']

# Load data
p1_gen = pd.read_csv(os.path.join(raw_dir, 'Plant_1_Generation_Data.csv'))
p1_wea = pd.read_csv(os.path.join(raw_dir, 'Plant_1_Weather_Sensor_Data.csv'))
p2_gen = pd.read_csv(os.path.join(raw_dir, 'Plant_2_Generation_Data.csv'))
p2_wea = pd.read_csv(os.path.join(raw_dir, 'Plant_2_Weather_Sensor_Data.csv'))

# Convert dates
for df in [p1_gen, p1_wea, p2_gen, p2_wea]:
    # Try different formats, as kaggle solar data date formats can be inconsistent
    df['DATE_TIME'] = pd.to_datetime(df['DATE_TIME'], format='mixed', dayfirst=True)

# Plant 1 & 2 Merge
p1 = pd.merge(p1_gen, p1_wea, on=['DATE_TIME', 'PLANT_ID'], how='inner')
p2 = pd.merge(p2_gen, p2_wea, on=['DATE_TIME', 'PLANT_ID'], how='inner')
df = pd.concat([p1, p2], ignore_index=True)

# Sort by inverter and time
df = df.sort_values(by=['SOURCE_KEY_x', 'DATE_TIME']).reset_index(drop=True)

# 2. Compute derived features
df['thermal_elevation'] = df['MODULE_TEMPERATURE'] - df['AMBIENT_TEMPERATURE']
df['conversion_efficiency'] = np.where(df['DC_POWER'] > 0, df['AC_POWER'] / df['DC_POWER'], 0)
df['power_loss_proxy'] = df['DC_POWER'] - df['AC_POWER']

# Rolling z-score of module temp per inverter
window = config['features']['rolling_window']
df['mod_temp_rolling_mean'] = df.groupby('SOURCE_KEY_x')['MODULE_TEMPERATURE'].transform(lambda x: x.rolling(window, min_periods=1).mean())
df['mod_temp_rolling_std'] = df.groupby('SOURCE_KEY_x')['MODULE_TEMPERATURE'].transform(lambda x: x.rolling(window, min_periods=1).std())
df['mod_temp_rolling_zscore'] = np.where(df['mod_temp_rolling_std'] > 0,
                                         (df['MODULE_TEMPERATURE'] - df['mod_temp_rolling_mean']) / df['mod_temp_rolling_std'],
                                         0)

# Localized median filter for transient dropouts for missing value imputation (though none expected in raw)
# Apply on numericals
num_cols = ['DC_POWER', 'AC_POWER', 'DAILY_YIELD', 'TOTAL_YIELD', 'AMBIENT_TEMPERATURE', 'MODULE_TEMPERATURE', 'IRRADIATION']
for col in num_cols:
    df[col] = df.groupby('SOURCE_KEY_x')[col].transform(lambda x: x.fillna(x.rolling(window, min_periods=1).median()))

df = df.dropna(subset=num_cols + ['thermal_elevation', 'conversion_efficiency'])

# 3. Label construction
def determine_state(row):
    # State 3: Failure proxy (near zero AC output during expected gen hours)
    if row['IRRADIATION'] > config['features']['low_irradiation_threshold'] and row['AC_POWER'] < 5: # arbitrary low threshold
        return 3
    # State 2: Grid/Output Volatility (efficiency deviation without thermal cause)
    # Using 15% as arbitrary threshold for deviation (efficiency < normal_min)
    if row['conversion_efficiency'] < config['features']['normal_efficiency_min'] and row['thermal_elevation'] <= config['features']['normal_elevation_max'] and row['DC_POWER'] > 0:
        return 2
    # State 1: Thermal Warning
    if row['thermal_elevation'] > config['features']['normal_elevation_max'] and row['conversion_efficiency'] >= config['features']['normal_efficiency_min']:
        return 1
    # State 0: Normal
    return 0

df['state'] = df.apply(determine_state, axis=1)

# Write label construction report
with open(os.path.join(reports_dir, 'label_construction.md'), 'w') as f:
    f.write("# Label Construction Rules\n\n")
    f.write("State 0 (Normal): thermal elevation and efficiency within config-defined normal bands.\n")
    f.write("State 1 (Thermal Warning): thermal elevation exceeds config threshold but efficiency still nominal.\n")
    f.write("State 2 (Grid/Output Volatility): efficiency or power output deviates beyond config threshold without thermal cause.\n")
    f.write("State 3 (Failure proxy): near-zero AC output during expected generation hours (irradiation above config threshold) — proxy for inverter failure, since no hardware fault flag exists in this data.\n")
    f.write("\n**Note:** This is a heuristic label, not ground truth.\n")

pd.DataFrame({
    'State': [0, 1, 2, 3],
    'Description': ['Normal', 'Thermal Warning', 'Volatility', 'Failure Proxy'],
    'Thresholds': [
        f"Elev <= {config['features']['normal_elevation_max']}, Eff >= {config['features']['normal_efficiency_min']}",
        f"Elev > {config['features']['normal_elevation_max']}, Eff >= {config['features']['normal_efficiency_min']}",
        f"Eff < {config['features']['normal_efficiency_min']}, Elev <= {config['features']['normal_elevation_max']}, DC > 0",
        f"Irr > {config['features']['low_irradiation_threshold']}, AC < 5"
    ]
}).to_csv(os.path.join(tables_dir, '02_label_thresholds.csv'), index=False)


# Check class distribution
class_dist = df['state'].value_counts().reset_index()
class_dist.columns = ['state', 'count']
class_dist['percentage'] = (class_dist['count'] / len(df)) * 100
class_dist.to_csv(os.path.join(tables_dir, '03_class_distribution.csv'), index=False)

plt.figure(figsize=(8, 5))
sns.barplot(data=class_dist, x='state', y='count')
plt.title('Class Distribution')
plt.savefig(os.path.join(figures_dir, '02_class_distribution.png'), dpi=300, bbox_inches='tight')
plt.close()

# Thermal elevation vs efficiency scatter
plt.figure(figsize=(10, 6))
sns.scatterplot(data=df.sample(min(10000, len(df)), random_state=42), x='thermal_elevation', y='conversion_efficiency', hue='state', palette='Set1', s=10)
plt.title('Thermal Elevation vs Efficiency')
plt.savefig(os.path.join(figures_dir, '04_thermal_vs_efficiency.png'), dpi=300, bbox_inches='tight')
plt.close()

# 5. Correlation matrix & collinearity
feature_cols = ['DC_POWER', 'AC_POWER', 'DAILY_YIELD', 'TOTAL_YIELD', 'AMBIENT_TEMPERATURE',
                'MODULE_TEMPERATURE', 'IRRADIATION', 'thermal_elevation', 'conversion_efficiency',
                'power_loss_proxy', 'mod_temp_rolling_zscore']

corr = df[feature_cols].corr()

plt.figure(figsize=(12, 10))
sns.heatmap(corr, annot=True, cmap='coolwarm', fmt=".2f")
plt.title('Feature Correlation Matrix')
plt.savefig(os.path.join(figures_dir, '03_correlation_matrix.png'), dpi=300, bbox_inches='tight')
plt.close()

# Drop collinear features
upper = corr.where(np.triu(np.ones(corr.shape), k=1).astype(bool))
to_drop = [column for column in upper.columns if any(upper[column].abs() > config['features']['collinearity_threshold'])]

dropped_info = []
for drop_col in to_drop:
    correlated_with = upper.index[upper[drop_col].abs() > config['features']['collinearity_threshold']].tolist()
    for corr_col in correlated_with:
        dropped_info.append({'dropped_feature': drop_col, 'correlated_with': corr_col, 'correlation': upper.loc[corr_col, drop_col]})

pd.DataFrame(dropped_info).to_csv(os.path.join(tables_dir, '04_dropped_features.csv'), index=False)

final_features = [c for c in feature_cols if c not in to_drop]

# Feature distribution histogram grid
plt.figure(figsize=(15, 12))
for i, col in enumerate(final_features, 1):
    plt.subplot(4, 3, i)
    sns.histplot(df[col], bins=30, kde=True)
    plt.title(col)
plt.tight_layout()
plt.savefig(os.path.join(figures_dir, '05_feature_distributions.png'), dpi=300, bbox_inches='tight')
plt.close()

# 6. RobustScaler
scaler = RobustScaler()
df[final_features] = scaler.fit_transform(df[final_features])
joblib.dump(scaler, os.path.join(processed_dir, 'robust_scaler.pkl'))

# Save to parquet
df[final_features + ['state']].to_parquet(os.path.join(processed_dir, 'features_labeled.parquet'), index=False)
print("Stage 2 Complete")
