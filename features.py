import pandas as pd
import numpy as np

def engineer_features(df):
    """
    Adds Thermal_delta and Mechanical_power features based on the proposal.
    Thermal delta: Process temperature - Air temperature
    Mechanical power: (Rotational speed * 2 * pi / 60) * Torque
    """
    df_new = df.copy()
    df_new['Thermal_delta'] = df_new['Process temperature'] - df_new['Air temperature']

    # Power in Watts = Angular velocity (rad/s) * Torque (Nm)
    # Angular velocity = (Rotational speed * 2 * pi) / 60
    df_new['Mechanical_power'] = (df_new['Rotational speed'] * 2 * np.pi / 60) * df_new['Torque']

    return df_new

def select_features(df):
    """
    Select the features for modeling and target variable.
    Drop ID columns, flag columns (prevent data leakage), and original temp columns if we only want the engineered ones (optional, let's keep all numeric to be safe).
    """
    target = 'Machine failure'
    features = ['Type', 'Air temperature', 'Process temperature', 'Rotational speed', 'Torque', 'Tool wear', 'Thermal_delta', 'Mechanical_power']

    X = df[features]
    y = df[target]

    return X, y
