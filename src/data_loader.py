import pandas as pd
import numpy as np
import os
import matplotlib.pyplot as plt
import seaborn as plt_sns
import subprocess

# Schema Mapping
SCHEMA_MAP = {
    'Thermal_Log': ['Thermal_Log', 'temperature', 'Temperature', 'air_temperature_k', 'process_temperature_k', 'T24', 'T30', 'T50', 'T_out'],
    'Workload_Ratio': ['Workload_Ratio', 'cpu_utilization', 'memory_utilization', 'rotational_speed_rpm', 'torque_nm', 'tool_wear_min', 'P30', 'Nf', 'Nc', 'Ps30', 'phi', 'NRf', 'NRc', 'BPR', 'htBleed', 'W31', 'W32'],
    'Uptime_Cycles': ['Uptime_Cycles', 'uptime', 'time_in_cycles', 'cycle'],
    'Failure_Label': ['Failure_Label', 'failure', 'machine_failure', 'Target', 'Failure Type', 'RUL', 'label1', 'label2']
}

DATASETS = {
    'iot_device_failure': 'ziya07/iot-device-failure-prediction-dataset',
    'iot_predictive_maintenance': 'ziya07/iot-integrated-predictive-maintenance-dataset',
    'machine_predictive_maintenance': 'shivamb/machine-predictive-maintenance-classification',
    'nasa_cmapss': 'behrad3d/nasa-cmaps',
    'temp_readings_iot': 'atulanandjha/temperature-readings-iot-devices'
}

def download_datasets(raw_dir='data/raw'):
    os.makedirs(raw_dir, exist_ok=True)

    # Try downloading with kaggle CLI
    try:
        subprocess.run(['kaggle', 'datasets', 'list'], check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    except Exception as e:
        print(f"Kaggle API not configured or accessible. Falling back to empty dataframes. Error: {e}")
        return False

    for name, dataset_path in DATASETS.items():
        try:
            print(f"Downloading {dataset_path}...")
            subprocess.run(['kaggle', 'datasets', 'download', '-d', dataset_path, '-p', raw_dir, '--unzip'], check=True)
        except Exception as e:
            print(f"Failed to download {dataset_path}: {e}")
    return True

def align_schema(df, dataset_name):
    aligned_df = df.copy()
    mapped_columns = {}

    # Simple mapping heuristic
    for standard_col, possible_names in SCHEMA_MAP.items():
        for col in aligned_df.columns:
            if col in possible_names or any(name.lower() in col.lower() for name in possible_names):
                mapped_columns[col] = standard_col
                break

    # Create required columns if they don't exist
    aligned_df = aligned_df.rename(columns=mapped_columns)

    for req_col in SCHEMA_MAP.keys():
        if req_col not in aligned_df.columns:
             # Create dummy if completely missing
             if req_col == 'Thermal_Log':
                 aligned_df[req_col] = 40.0
             elif req_col == 'Workload_Ratio':
                 aligned_df[req_col] = 0.5
             elif req_col == 'Uptime_Cycles':
                 aligned_df[req_col] = np.arange(len(aligned_df))
             elif req_col == 'Failure_Label':
                 aligned_df[req_col] = 0

    if 'Device_ID' not in aligned_df.columns:
        aligned_df['Device_ID'] = 'device_0'

    return aligned_df

def load_data(raw_dir='data/raw', processed_dir='data/processed'):
    os.makedirs(processed_dir, exist_ok=True)

    if not download_datasets(raw_dir):
        # Fallback to empty dataframes
        print("Creating empty dummy dataframe due to missing data")
        df = pd.DataFrame(columns=['Device_ID', 'Thermal_Log', 'Workload_Ratio', 'Uptime_Cycles', 'Failure_Label'])
        df.to_csv(os.path.join(processed_dir, 'iot_device_failure.csv'), index=False)
        return {'iot_device_failure': df}

    dfs = {}
    for filename in os.listdir(raw_dir):
        if filename.endswith('.csv'):
            filepath = os.path.join(raw_dir, filename)
            df = pd.read_csv(filepath)

            print(f"--- {filename} ---")
            print(f"Shape: {df.shape}")
            print(f"Dtypes:\n{df.dtypes}")
            print(f"Null counts:\n{df.isnull().sum()}")

            dataset_name = filename.split('.')[0]
            aligned_df = align_schema(df, dataset_name)

            output_path = os.path.join(processed_dir, filename)
            aligned_df.to_csv(output_path, index=False)
            dfs[dataset_name] = aligned_df

    return dfs

def run_eda(dfs, output_dir='.'):
    os.makedirs(output_dir, exist_ok=True)

    if not dfs or all(df.empty for df in dfs.values()):
        print("DataFrames are empty, skipping EDA.")
        return

    # Use the primary dataset if available
    primary_df = list(dfs.values())[0]
    for name, df in dfs.items():
        if 'iot' in name.lower() and 'failure' in name.lower():
            primary_df = df
            break

    # 1. Failure class distribution
    plt.figure(figsize=(8, 6))
    primary_df['Failure_Label'].value_counts().plot(kind='bar')
    plt.title('Failure Class Distribution')
    plt.xlabel('Failure Class')
    plt.ylabel('Count')
    plt.tight_layout()
    plt.savefig(os.path.join(output_dir, 'failure_class_distribution.png'), dpi=300)
    plt.close()

    # 2. Temperature distribution by failure class
    plt.figure(figsize=(10, 6))
    plt_sns.violinplot(x='Failure_Label', y='Thermal_Log', data=primary_df)
    plt.title('Temperature Distribution by Failure Class')
    plt.xlabel('Failure Class')
    plt.ylabel('Temperature (°C)')
    plt.tight_layout()
    plt.savefig(os.path.join(output_dir, 'temp_distribution_by_class.png'), dpi=300)
    plt.close()

    # 3. Correlation heatmap
    numeric_df = primary_df.select_dtypes(include=[np.number])
    if not numeric_df.empty:
        plt.figure(figsize=(10, 8))
        plt_sns.heatmap(numeric_df.corr(), annot=True, cmap='coolwarm', fmt=".2f")
        plt.title('Correlation Heatmap')
        plt.tight_layout()
        plt.savefig(os.path.join(output_dir, 'correlation_heatmap.png'), dpi=300)
        plt.close()

    # 4. Time-series plot of Thermal_Log
    plt.figure(figsize=(12, 6))
    sample_devices = primary_df['Device_ID'].unique()[:min(5, len(primary_df['Device_ID'].unique()))]
    for device in sample_devices:
        device_data = primary_df[primary_df['Device_ID'] == device].sort_values('Uptime_Cycles')
        plt.plot(device_data['Uptime_Cycles'], device_data['Thermal_Log'], label=f'Device {device}')
    plt.title('Thermal Log Time-Series')
    plt.xlabel('Uptime Cycles')
    plt.ylabel('Temperature (°C)')
    plt.legend()
    plt.tight_layout()
    plt.savefig(os.path.join(output_dir, 'thermal_timeseries.png'), dpi=300)
    plt.close()

if __name__ == "__main__":
    dfs = load_data()
    run_eda(dfs)
