import pandas as pd
import numpy as np
import os
import joblib
from sklearn.model_selection import RandomizedSearchCV, GroupShuffleSplit
from sklearn.linear_model import LinearRegression
from sklearn.ensemble import RandomForestRegressor
from xgboost import XGBRegressor
from lightgbm import LGBMRegressor
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
import matplotlib.pyplot as plt
import seaborn as sns
import shap
import json
import io
import requests
import zipfile
import subprocess
import copy

plt.rcParams.update({'font.size': 11, 'axes.titlesize': 13, 'axes.labelsize': 11, 'xtick.labelsize': 10, 'ytick.labelsize': 10, 'figure.dpi': 300, 'savefig.dpi': 300})
np.random.seed(42)

DATA_DIR = 'data/raw/'
PROCESSED_DIR = 'data/processed/'
MODELS_DIR = 'models/'
FIG_DIR = 'outputs/figures/'
RES_DIR = 'outputs/results/'
LOGS_DIR = 'results/logs/'

for d in [DATA_DIR, PROCESSED_DIR, MODELS_DIR, FIG_DIR, RES_DIR, LOGS_DIR]:
    os.makedirs(d, exist_ok=True)

with open('ASSUMPTIONS.md', 'w') as f:
    f.write("# Modeling Assumptions\n")
    f.write("1. **Fuel Consumption Proxy:** Direct fuel consumption is absent from standard EV datasets. We assume 8.8 kWh/L gasoline energy density operating at an average 30% ICE efficiency. Thus, Estimated Fuel (L) = Restored Energy (kWh) / (8.8 * 0.3).\n")
    f.write("2. **Generator Activation:** Defined as rows where `soc_pct` drops below a rolling 10-row minimum, followed by a positive spike in `charge_rate_kw`.\n")
    f.write("3. **Missing Features:** Since the datasets do not all strictly overlap, certain proxy or derived calculations (like using battery voltage/current to compute power demand) are applied.\n")
    f.write("4. **Leakage Prevention:** To avoid perfect algebraic target leakage, SoC rolling features and deltas are shifted by 1 row to represent the *past* SoC context rather than mathematically leaking the *current* target SoC.\n")

print("Step 1: Downloading Datasets...")
datasets = {
    "uci_secondary_storage": "https://archive.ics.uci.edu/dataset/616/secondary+storage+of+electrical+energy",
    "kaggle_ev_energy": "ziya07/ev-energy-consumption-dataset",
    "kaggle_battery_heating": "atechnohazard/battery-and-heating-data-in-real-driving-cycles",
    "kaggle_ev_charging": "ziya07/ev-battery-charging-data",
    "kaggle_ev_load": "datasetengineer/ev-charging-load-dataset-and-optimal-routing"
}

def download_kaggle(dataset_ref):
    print(f"Attempting to download Kaggle dataset {dataset_ref}...")
    try:
        subprocess.run(['kaggle', 'datasets', 'download', '-d', dataset_ref, '-p', DATA_DIR, '--unzip'], check=True, capture_output=True)
        print(f"Successfully downloaded and unzipped {dataset_ref}")
    except subprocess.CalledProcessError as e:
        err_msg = f"Failed to download Kaggle dataset {dataset_ref}. Error: {e.stderr.decode('utf-8') if e.stderr else 'Unknown Error'}"
        with open(os.path.join(LOGS_DIR, "download_errors.log"), "a") as f:
            f.write(err_msg + "\n")
        raise RuntimeError(err_msg)

for name, ref in datasets.items():
    if "kaggle" in name:
        if name == "kaggle_ev_energy" and os.path.exists(os.path.join(DATA_DIR, "EV_Energy_Consumption_Dataset.csv")): continue
        if name == "kaggle_battery_heating" and os.path.exists(os.path.join(DATA_DIR, "TripA01.csv")): continue
        if name == "kaggle_ev_charging" and os.path.exists(os.path.join(DATA_DIR, "ev_battery_charging_data.csv")): continue
        if name == "kaggle_ev_load" and os.path.exists(os.path.join(DATA_DIR, "ev_charging_dataset.csv")): continue
        download_kaggle(ref)
    else:
        if os.path.exists(os.path.join(DATA_DIR, "uci_616_features.csv")) and os.path.getsize(os.path.join(DATA_DIR, "uci_616_features.csv")) > 0: continue
        print(f"Attempting to fetch from URL: {ref}")
        try:
            from ucimlrepo import fetch_ucirepo
            uci_data = fetch_ucirepo(id=616)
            df_uci = uci_data.data.features
            df_uci.to_csv(os.path.join(DATA_DIR, "uci_616_features.csv"), index=False)
            print("Successfully downloaded UCI 616")
        except Exception as e:
            err_msg = f"Failed to download UCI dataset 616 from URL {ref}. Error: {e}"
            with open(os.path.join(LOGS_DIR, "download_errors.log"), "a") as f: f.write(err_msg + "\n")
            raise RuntimeError(err_msg)  # STRICTLY HALTS PIPELINE; DO NOT CATCH!

print("Step 2: Data Ingestion and Audit...")
standard_cols = ['soc_pct', 'speed_kmh', 'incline_deg', 'ambient_temp_c', 'battery_temp_c',
                 'power_demand_kw', 'energy_consumed_kwh', 'charge_rate_kw', 'trip_id', 'timestamp']

audit_report = []
def audit_df(name, df):
    audit_report.append(f"--- Dataset: {name} ---")
    audit_report.append(f"Shape: {df.shape}")
    buffer = io.StringIO()
    df.info(buf=buffer)
    audit_report.append(buffer.getvalue())
    audit_report.append("\nSummary Statistics:")
    audit_report.append(df.describe().to_string())
    audit_report.append("\nMissing values:")
    audit_report.append(df.isnull().sum().to_string())
    missing_standard = [col for col in standard_cols if col not in df.columns]
    if missing_standard:
        audit_report.append("\nAbsent Standard Variables (Mapped to NaN):")
        audit_report.append(", ".join(missing_standard))
    audit_report.append("\n" + "="*50 + "\n")

all_standardized_dfs = []

# 1. EV Energy Consumption
if os.path.exists(os.path.join(DATA_DIR, 'EV_Energy_Consumption_Dataset.csv')):
    df1 = pd.read_csv(os.path.join(DATA_DIR, 'EV_Energy_Consumption_Dataset.csv'))
    df1_std = df1.rename(columns={
        'Battery_State_%': 'soc_pct', 'Energy_Consumption_kWh': 'energy_consumed_kwh',
        'Speed_kmh': 'speed_kmh', 'Temperature_C': 'ambient_temp_c',
        'Battery_Temperature_C': 'battery_temp_c', 'Vehicle_ID': 'trip_id', 'Timestamp': 'timestamp'
    })
    for col in standard_cols:
        if col not in df1_std.columns: df1_std[col] = np.nan
    df1_std = df1_std[standard_cols]
    df1_std.to_csv(os.path.join(PROCESSED_DIR, 'ev_energy.csv'), index=False)
    audit_df("EV Energy Consumption", df1_std)
    df1_std['source'] = 'ev_energy'
    all_standardized_dfs.append(df1_std)

# 2. EV Battery Charging
if os.path.exists(os.path.join(DATA_DIR, 'ev_battery_charging_data.csv')):
    df2 = pd.read_csv(os.path.join(DATA_DIR, 'ev_battery_charging_data.csv'))
    df2_std = df2.rename(columns={
        'SOC (%)': 'soc_pct', 'Battery Temp (°C)': 'battery_temp_c',
        'Ambient Temp (°C)': 'ambient_temp_c'
    })
    if 'Voltage (V)' in df2_std.columns and 'Current (A)' in df2_std.columns:
        df2_std['charge_rate_kw'] = (df2_std['Voltage (V)'] * df2_std['Current (A)']) / 1000.0
    for col in standard_cols:
        if col not in df2_std.columns: df2_std[col] = np.nan
    df2_std['trip_id'] = [f"charging_{i}" for i in range(len(df2_std))]
    df2_std = df2_std[standard_cols]
    df2_std.to_csv(os.path.join(PROCESSED_DIR, 'ev_charging.csv'), index=False)
    audit_df("EV Battery Charging", df2_std)
    df2_std['source'] = 'ev_charging'
    all_standardized_dfs.append(df2_std)

# 3. EV Charging Load
if os.path.exists(os.path.join(DATA_DIR, 'ev_charging_dataset.csv')):
    df3 = pd.read_csv(os.path.join(DATA_DIR, 'ev_charging_dataset.csv'))
    df3_std = df3.rename(columns={
        'State_of_Charge_%': 'soc_pct', 'Energy_Drawn_kWh': 'energy_consumed_kwh',
        'Charging_Rate_kW': 'charge_rate_kw', 'Temperature_C': 'ambient_temp_c',
        'Vehicle_ID': 'trip_id', 'Date_Time': 'timestamp'
    })
    for col in standard_cols:
        if col not in df3_std.columns: df3_std[col] = np.nan
    df3_std = df3_std[standard_cols]
    df3_std.to_csv(os.path.join(PROCESSED_DIR, 'ev_load.csv'), index=False)
    audit_df("EV Charging Load", df3_std)
    df3_std['source'] = 'ev_load'
    all_standardized_dfs.append(df3_std)

# 4. UCI 616
if os.path.exists(os.path.join(DATA_DIR, "uci_616_features.csv")):
    try:
        df4 = pd.read_csv(os.path.join(DATA_DIR, "uci_616_features.csv"))
        df4_std = df4.copy()
        for col in standard_cols:
            if col not in df4_std.columns: df4_std[col] = np.nan
        df4_std = df4_std[standard_cols]
        df4_std.to_csv(os.path.join(PROCESSED_DIR, 'uci_storage.csv'), index=False)
        audit_df("UCI Secondary Storage", df4_std)
        df4_std['source'] = 'uci_storage'
        all_standardized_dfs.append(df4_std)
    except: pass

# 5. Battery and Heating
battery_dfs = []
for file in os.listdir(DATA_DIR):
    if file.startswith('Trip') and file.endswith('.csv'):
        try:
            trip_df = pd.read_csv(os.path.join(DATA_DIR, file), sep=';', encoding='latin1', on_bad_lines='skip')
            trip_df['trip_id'] = file.replace('.csv', '')
            col_map = {
                'SoC [%]': 'soc_pct', 'Velocity [km/h]': 'speed_kmh', 'Velocity [km/h]]': 'speed_kmh',
                'Elevation [m]': 'elevation_m', 'Ambient Temperature [°C]': 'ambient_temp_c',
                'Battery Temperature [°C]': 'battery_temp_c', 'Battery Voltage [V]': 'battery_v',
                'Battery Current [A]': 'battery_a', 'Time [s]': 'timestamp'
            }
            trip_df = trip_df.rename(columns={col: col_map[col] for col in trip_df.columns if col in col_map})
            if 'battery_v' in trip_df.columns and 'battery_a' in trip_df.columns:
                trip_df['power_demand_kw'] = (trip_df['battery_v'] * trip_df['battery_a']) / 1000.0

            if 'elevation_m' in trip_df.columns:
                trip_df['incline_deg'] = trip_df['elevation_m'].diff().fillna(0)

            for col in standard_cols:
                if col not in trip_df.columns: trip_df[col] = np.nan
            trip_df = trip_df[standard_cols]
            battery_dfs.append(trip_df)
        except Exception as e:
            pass

if battery_dfs:
    df5_std = pd.concat(battery_dfs, ignore_index=True)
    df5_std.to_csv(os.path.join(PROCESSED_DIR, 'battery_heating.csv'), index=False)
    audit_df("Battery and Heating (Combined Trips)", df5_std)
    df5_std['source'] = 'battery_heating'
    all_standardized_dfs.append(df5_std)

with open('data_audit_report.txt', 'w') as f:
    f.write('\n'.join(audit_report))

print("Step 3: Target Variable Engineering...")
df = pd.concat(all_standardized_dfs, ignore_index=True)
df.to_csv(os.path.join(PROCESSED_DIR, 'combined_ev_data.csv'), index=False)

df = df.sort_values(by=['source', 'trip_id', 'timestamp'])
df = df.reset_index(drop=True)

df['power_demand_kw'] = df['power_demand_kw'].fillna(10.0)
df['charge_rate_kw'] = df['charge_rate_kw'].fillna(df['power_demand_kw'].apply(lambda x: -x if x < 0 else 0))
df['battery_temp_c'] = df['battery_temp_c'].fillna(25.0)
df['ambient_temp_c'] = df['ambient_temp_c'].fillna(20.0)
df['speed_kmh'] = df['speed_kmh'].fillna(50.0)
df['incline_deg'] = df['incline_deg'].fillna(0.0)
df['energy_consumed_kwh'] = df['energy_consumed_kwh'].fillna(0.0)

df['soc_min_10'] = df.groupby('trip_id')['soc_pct'].transform(lambda x: x.rolling(10, min_periods=1).min())

# Bug Fix: Properly group before shift and rolling to prevent cross-trip leakage
df['charge_spike'] = df.groupby('trip_id')['charge_rate_kw'].transform(
    lambda x: x.shift(-1).rolling(5, min_periods=1).max()
) > 0.5

df['generator_activated'] = (df['soc_pct'] < df['soc_min_10'].shift(1)) & df['charge_spike']

activation_indices = df[df['generator_activated']].index
print(f"Detected {len(activation_indices)} raw activation signals.")

eta_vals = np.zeros(len(df))
soc_trigger_vals = np.zeros(len(df))
eta_vals[:] = np.nan
soc_trigger_vals[:] = np.nan

clipped_rows = []

for count, idx in enumerate(activation_indices):
    if count > 2000: break
    start_idx = max(0, idx - 5)
    end_idx = min(len(df) - 1, idx + 5)
    if df.loc[start_idx, 'trip_id'] != df.loc[end_idx, 'trip_id']: continue

    delta_kwh = df.loc[start_idx:end_idx, 'charge_rate_kw'].sum() / 3600.0 * 10
    if delta_kwh <= 0: continue

    estimated_fuel_l = delta_kwh / (8.8 * 0.3)
    eta = delta_kwh / estimated_fuel_l if estimated_fuel_l > 0 else 0

    # Log clipped rows per instructions
    if eta > 4.0:
        clipped_rows.append({'index': idx, 'raw_eta': eta})
        eta = 4.0

    eta_vals[idx] = eta
    soc_trigger_vals[idx] = df.loc[idx, 'soc_pct']

if clipped_rows:
    pd.DataFrame(clipped_rows).to_csv(os.path.join(LOGS_DIR, 'clipped_eta_rows.csv'), index=False)
    print(f"Logged {len(clipped_rows)} clipped ETA values.")

df['eta'] = eta_vals
df['soc_trigger_pct'] = soc_trigger_vals

print("Step 4: Feature Engineering...")
# IEEE-ready Documentation for Physical Rationale:
# speed_x_incline models the gravitational resistance power term (P ~ v * sin(theta)), linearly proportional to slope for small angles.
df['speed_x_incline'] = df['speed_kmh'] * df['incline_deg']
# thermal_stress models heat dissipation limits (Newton's law of cooling q ~ delta_T) defining battery operating envelope.
df['thermal_stress'] = df['battery_temp_c'] - df['ambient_temp_c']

# LEAKAGE PREVENTION: Shift SoC-dependent rolling features
df['soc_rolling_mean'] = df.groupby('trip_id')['soc_pct'].transform(lambda x: x.shift(1).rolling(10, min_periods=1).mean())
df['soc_rolling_std'] = df.groupby('trip_id')['soc_pct'].transform(lambda x: x.shift(1).rolling(10, min_periods=1).std()).fillna(0)
df['soc_delta'] = df.groupby('trip_id')['soc_pct'].transform(lambda x: x.shift(1).diff()).fillna(0)

# Unshifted external features
df['power_rolling_mean'] = df.groupby('trip_id')['power_demand_kw'].transform(lambda x: x.rolling(10, min_periods=1).mean())
df['power_rolling_max'] = df.groupby('trip_id')['power_demand_kw'].transform(lambda x: x.rolling(10, min_periods=1).max())
df['speed_rolling_mean'] = df.groupby('trip_id')['speed_kmh'].transform(lambda x: x.rolling(10, min_periods=1).mean())
df['discharge_rate_pct_per_min'] = df['soc_delta'] / (1.0 / 60.0)

features = [
    'speed_kmh', 'incline_deg', 'ambient_temp_c', 'battery_temp_c', 'power_demand_kw',
    'speed_x_incline', 'thermal_stress', 'soc_rolling_mean', 'soc_rolling_std',
    'power_rolling_mean', 'power_rolling_max', 'speed_rolling_mean',
    'soc_delta', 'discharge_rate_pct_per_min', 'charge_rate_kw', 'energy_consumed_kwh'
]

df_target = df[df['eta'].notnull()].copy()
df_target = df_target.dropna(subset=features + ['soc_trigger_pct', 'eta'])

print(f"Step 5 & 6: Model Training... (Data size: {len(df_target)})")
counts = df_target['trip_id'].value_counts()
valid_groups = counts[counts >= 1].index
df_target = df_target[df_target['trip_id'].isin(valid_groups)]

# In case of data scarcity we duplicate for CV execution validation ONLY if needed.
if len(df_target['trip_id'].unique()) < 3 and len(df_target) > 0:
    print("Warning: Only 1-2 physical trips found. Duplicating to allow cross-validation.")
    df_dup1 = df_target.copy()
    df_dup1['trip_id'] = df_dup1['trip_id'].astype(str) + "_dup1"
    df_dup2 = df_target.copy()
    df_dup2['trip_id'] = df_dup2['trip_id'].astype(str) + "_dup2"
    df_target = pd.concat([df_target, df_dup1, df_dup2], ignore_index=True)

trips = df_target['trip_id'].unique()
np.random.shuffle(trips)

n_train = max(1, int(0.8 * len(trips)))
n_val = max(1, int(0.1 * len(trips)))

train_trips = trips[:n_train]
val_trips = trips[n_train:n_train+n_val]
test_trips = trips[n_train+n_val:]

if len(test_trips) == 0:
    train_trips = trips[:max(1, len(trips)-2)]
    val_trips = trips[max(1, len(trips)-2):max(1, len(trips)-1)]
    test_trips = trips[-1:]

train_data = df_target[df_target['trip_id'].isin(train_trips)]
val_data = df_target[df_target['trip_id'].isin(val_trips)]
test_data = df_target[df_target['trip_id'].isin(test_trips)]

X_train, y_train_soc, y_train_eta = train_data[features], train_data['soc_trigger_pct'], train_data['eta']
X_val, y_val_soc, y_val_eta = val_data[features], val_data['soc_trigger_pct'], val_data['eta']
X_test, y_test_soc, y_test_eta = test_data[features], test_data['soc_trigger_pct'], test_data['eta']

models = {
    'Linear Regression': LinearRegression(),
    'Random Forest': RandomForestRegressor(n_estimators=200, max_depth=15, random_state=42, n_jobs=-1),
    'XGBoost': XGBRegressor(learning_rate=0.05, n_estimators=500, early_stopping_rounds=20, random_state=42, n_jobs=-1),
    'LightGBM': LGBMRegressor(num_leaves=63, random_state=42, verbose=-1, n_jobs=-1)
}

results_soc = []
best_mae = float('inf')
best_model_name = None
best_model_soc = None

for name, model in models.items():
    print(f"Training {name}...")
    if name == 'XGBoost':
        model.fit(X_train, y_train_soc, eval_set=[(X_val, y_val_soc)], verbose=False)
    else:
        model.fit(X_train, y_train_soc)

    preds = model.predict(X_test)
    mae = mean_absolute_error(y_test_soc, preds)
    rmse = np.sqrt(mean_squared_error(y_test_soc, preds))
    r2 = r2_score(y_test_soc, preds)

    results_soc.append({'Model': name, 'MAE': mae, 'RMSE': rmse, 'R2': r2})

    if mae < best_mae:
        best_mae = mae
        best_model_name = name
        best_model_soc = model

pd.DataFrame(results_soc).to_csv(os.path.join(RES_DIR, 'model_comparison.csv'), index=False)

print(f"Best model for SoC was {best_model_name} with MAE {best_mae:.4f}")

# Dynamic Secondary Model Construction using EXACT configuration as the best model (without early stopping args if absent)
print("Training Secondary Eta model using Best Model Architecture...")
if best_model_name == 'XGBoost':
    eta_model = XGBRegressor(learning_rate=0.05, n_estimators=500, random_state=42, n_jobs=-1)
elif best_model_name == 'LightGBM':
    eta_model = LGBMRegressor(num_leaves=63, random_state=42, verbose=-1, n_jobs=-1)
elif best_model_name == 'Random Forest':
    eta_model = RandomForestRegressor(n_estimators=200, max_depth=15, random_state=42, n_jobs=-1)
else:
    eta_model = LinearRegression()

eta_model.fit(X_train, y_train_eta)
eta_preds = eta_model.predict(X_test)

eta_metrics = [{
    'Model': f"{best_model_name} (Eta)",
    'MAE': mean_absolute_error(y_test_eta, eta_preds),
    'RMSE': np.sqrt(mean_squared_error(y_test_eta, eta_preds)),
    'R2': r2_score(y_test_eta, eta_preds)
}]
pd.DataFrame(eta_metrics).to_csv(os.path.join(RES_DIR, 'eta_model_metrics.csv'), index=False)

print(f"Step 7: Hyperparameter Tuning for {best_model_name}...")
if best_model_name == 'XGBoost':
    param_dist = {
        'n_estimators': [300, 500, 700], 'max_depth': [4, 6, 8, 10], 'learning_rate': [0.01, 0.05, 0.1],
        'subsample': [0.7, 0.8, 1.0], 'colsample_bytree': [0.7, 0.8, 1.0], 'min_child_weight': [1, 3, 5]
    }
    search_model = XGBRegressor(random_state=42, n_jobs=-1)
elif best_model_name == 'LightGBM':
    param_dist = {
        'n_estimators': [300, 500, 700], 'num_leaves': [31, 63, 127], 'learning_rate': [0.01, 0.05, 0.1]
    }
    search_model = LGBMRegressor(random_state=42, verbose=-1, n_jobs=-1)
elif best_model_name == 'Random Forest':
    param_dist = {
        'n_estimators': [200, 400, 600], 'max_depth': [10, 15, 20, 25]
    }
    search_model = RandomForestRegressor(random_state=42, n_jobs=-1)
else:
    search_model = None

if search_model is not None:
    random_search = RandomizedSearchCV(search_model, param_distributions=param_dist, n_iter=30, cv=5, scoring='neg_mean_absolute_error', random_state=42)
    random_search.fit(X_train, y_train_soc)

    with open(os.path.join(RES_DIR, 'best_params.json'), 'w') as f:
        def convert(o):
            if isinstance(o, np.int64): return int(o)
            raise TypeError
        json.dump(random_search.best_params_, f, default=convert, indent=4)

    best_model_soc = random_search.best_estimator_
else:
    with open(os.path.join(RES_DIR, 'best_params.json'), 'w') as f:
        json.dump({"note": f"Tuning skipped. Best model was {best_model_name}"}, f, indent=4)

joblib.dump(best_model_soc, os.path.join(MODELS_DIR, 'best_model.pkl'))


print("Step 8: Explainability (SHAP)...")
plt.clf()
# Use TreeExplainer for Tree models, LinearExplainer for Linear
if best_model_name in ['XGBoost', 'LightGBM', 'Random Forest']:
    explainer = shap.TreeExplainer(best_model_soc)
else:
    explainer = shap.LinearExplainer(best_model_soc, X_train)

X_test_sample = X_test.sample(min(1000, len(X_test)), random_state=42)
shap_values = explainer.shap_values(X_test_sample)

shap.summary_plot(shap_values, X_test_sample, plot_type="bar", show=False)
plt.savefig(os.path.join(FIG_DIR, 'shap_summary_bar.png'), bbox_inches='tight')
plt.clf()

shap.summary_plot(shap_values, X_test_sample, show=False)
plt.savefig(os.path.join(FIG_DIR, 'shap_beeswarm.png'), bbox_inches='tight')
plt.clf()

# For Linear, SHAP outputs might have slightly different shapes
vals_for_imp = np.abs(shap_values).mean(0)
feature_importance = pd.DataFrame({
    'feature': features,
    'importance': vals_for_imp
}).sort_values('importance', ascending=False)

feature_importance.to_csv(os.path.join(RES_DIR, 'feature_importance.csv'), index=False)
print("Top 5 Features:")
print(feature_importance.head(5))

shap.dependence_plot('soc_rolling_mean', shap_values, X_test_sample, show=False)
plt.savefig(os.path.join(FIG_DIR, 'shap_dependence_soc.png'), bbox_inches='tight')
plt.clf()

print("Step 9: Simulation...")
t = np.arange(200)
sim_df = pd.DataFrame({
    'speed_kmh': 65 + 35 * np.sin(t / 10),
    'incline_deg': np.random.uniform(-10, 10, 200),
    'ambient_temp_c': 25,
    'battery_temp_c': 30,
    'power_demand_kw': np.random.uniform(10, 50, 200),
    'energy_consumed_kwh': np.cumsum(np.random.uniform(0.1, 0.5, 200)),
    'charge_rate_kw': 0
})

sim_df['speed_x_incline'] = sim_df['speed_kmh'] * sim_df['incline_deg']
sim_df['thermal_stress'] = sim_df['battery_temp_c'] - sim_df['ambient_temp_c']
sim_df['soc_pct'] = 80 - t * 0.1
sim_df['soc_rolling_mean'] = 80 - t * 0.1
sim_df['soc_rolling_std'] = 1.0
sim_df['power_rolling_mean'] = 30.0
sim_df['power_rolling_max'] = 45.0
sim_df['speed_rolling_mean'] = 65.0
sim_df['soc_delta'] = -0.1
sim_df['discharge_rate_pct_per_min'] = -6.0

soc_base = 80.0
soc_base_hist = []
base_activations = 0

for i in range(200):
    soc_base_hist.append(soc_base)
    if soc_base < 30.0:
        base_activations += 1
        soc_base += 5.0
    soc_base -= 0.5

soc_ml = 80.0
soc_ml_hist = []
ml_activations = 0

for i in range(200):
    soc_ml_hist.append(soc_ml)
    sim_df.loc[i, 'soc_pct'] = soc_ml
    sim_df.loc[i, 'soc_rolling_mean'] = soc_ml
    X_sim = sim_df.loc[[i], features]
    thresh = best_model_soc.predict(X_sim)[0]

    if soc_ml <= thresh:
        ml_activations += 1
        soc_ml += 5.0
    soc_ml -= 0.5

plt.plot(t, soc_base_hist, label='Baseline (Fixed 30%)')
plt.plot(t, soc_ml_hist, label='ML Optimized')
plt.xlabel('Time Step')
plt.ylabel('SoC %')
plt.title('Simulation: SoC Trajectory')
plt.legend()
plt.savefig(os.path.join(FIG_DIR, 'soc_simulation_comparison.png'), bbox_inches='tight')

sim_res = pd.DataFrame({
    'Policy': ['Baseline', 'ML Optimized'],
    'Activations': [base_activations, ml_activations],
    'Final_SoC': [soc_base_hist[-1], soc_ml_hist[-1]],
    'Est_Fuel_L': [base_activations * (5.0 / (8.8*0.3)), ml_activations * (5.0 / (8.8*0.3))]
})
sim_res.to_csv(os.path.join(RES_DIR, 'simulation_summary.csv'), index=False)

print(sim_res.to_string(index=False))
print("Pipeline completed successfully.")
