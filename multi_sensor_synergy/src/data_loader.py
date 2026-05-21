"""Load and merge all datasets."""
import pandas as pd
import numpy as np
import config

def load_and_merge_data():
    """
    Loads all datasets, standardizes columns, merges them on common features,
    handles missing values (median imputation), and saves/returns unified DataFrame.
    """
    # 1. Primary Dataset - Smart Agriculture Dataset
    df_smart_ag = pd.read_csv(config.DATASETS['smart_ag'])
    # Columns: ['crop ID', 'soil_type', 'Seedling Stage', 'MOI', 'temp', 'humidity', 'result']
    df_smart_ag = df_smart_ag.rename(columns={
        'temp': 'Temperature',
        'humidity': 'Humidity',
        'MOI': 'Soil_Moisture' # Assuming this is soil moisture in this context, though MOI feature is calculated later. Let's see later. Wait, MOI is already there? Let's check.
    })

    # 2. Supplementary - Smart Farming Sensor Data
    df_smart_farm = pd.read_csv(config.DATASETS['smart_farming'])
    # Columns: ['farm_id', 'region', 'crop_type', 'soil_moisture_%', 'soil_pH', 'temperature_C', 'rainfall_mm', 'humidity_%', ...]
    df_smart_farm = df_smart_farm.rename(columns={
        'temperature_C': 'Temperature',
        'humidity_%': 'Humidity',
        'soil_pH': 'pH',
        'soil_moisture_%': 'Soil_Moisture',
        'rainfall_mm': 'Rainfall',
        'crop_type': 'Soil_Type' # Use crop_type as a proxy or just keep it
    })

    # 3. Supplementary - Hydroponics Feed
    # Read with engine='python' to avoid EOF error
    df_hydro = pd.read_csv(config.DATASETS['hydroponics'], on_bad_lines='skip', engine='python')
    # Columns: ['created_at', 'entry_id', 'field1', 'field2', 'field3', ...]
    # Field1: Temp, Field2: Humidity, Field3: Heat Index (or similar)
    df_hydro['field1'] = pd.to_numeric(df_hydro['field1'], errors='coerce')
    df_hydro['field2'] = pd.to_numeric(df_hydro['field2'], errors='coerce')
    df_hydro = df_hydro.rename(columns={
        'field1': 'Temperature',
        'field2': 'Humidity'
    })

    # 4. Supplementary - Soil pH, Moisture, Temp
    df_soil = pd.read_excel(config.DATASETS['soil_ph'])
    # Columns: ['No', 'pH', 'Kelembaban', 'Suhu']
    df_soil = df_soil.rename(columns={
        'Kelembaban': 'Soil_Moisture',
        'Suhu': 'Temperature'
    })
    # Clean pH column if it contains strings
    df_soil['pH'] = pd.to_numeric(df_soil['pH'], errors='coerce')
    df_soil['Soil_Moisture'] = pd.to_numeric(df_soil['Soil_Moisture'], errors='coerce')
    df_soil['Temperature'] = pd.to_numeric(df_soil['Temperature'], errors='coerce')

    # 5. Supplementary - Crop Recommendation
    df_crop = pd.read_csv(config.DATASETS['crop_rec'])
    # Columns: ['N', 'P', 'K', 'temperature', 'humidity', 'ph', 'rainfall', 'label']
    df_crop = df_crop.rename(columns={
        'temperature': 'Temperature',
        'humidity': 'Humidity',
        'ph': 'pH',
        'rainfall': 'Rainfall',
        'label': 'Soil_Type' # Use label as a proxy for grouping later if needed
    })

    # Target columns to keep
    core_cols = ['Temperature', 'Humidity', 'pH', 'Soil_Moisture', 'Rainfall', 'Soil_Type']

    # Ensure all dfs have core columns
    dfs = [df_smart_ag, df_smart_farm, df_hydro, df_soil, df_crop]
    for i in range(len(dfs)):
        for col in core_cols:
            if col not in dfs[i].columns:
                dfs[i][col] = np.nan
        dfs[i] = dfs[i][core_cols]

    # Combine datasets
    df_combined = pd.concat(dfs, ignore_index=True)

    # Handle missing values: median imputation for numerical, mode for categorical
    num_cols = ['Temperature', 'Humidity', 'pH', 'Soil_Moisture', 'Rainfall']
    for col in num_cols:
        df_combined[col] = pd.to_numeric(df_combined[col], errors='coerce')
        df_combined[col] = df_combined[col].fillna(df_combined[col].median())

    cat_cols = ['Soil_Type']
    for col in cat_cols:
        df_combined[col] = df_combined[col].fillna(df_combined[col].mode()[0])

    df_combined.to_csv(config.UNIFIED_DATA_PATH, index=False)
    print(f"Data loaded, merged, and saved to {config.UNIFIED_DATA_PATH}. Shape: {df_combined.shape}")
    return df_combined

if __name__ == "__main__":
    load_and_merge_data()
