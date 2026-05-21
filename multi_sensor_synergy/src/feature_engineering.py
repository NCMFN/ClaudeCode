"""Feature engineering: MOI, WAI, Delta, SMOTE, smoothing."""
import pandas as pd
import numpy as np
from imblearn.over_sampling import SMOTE
import config

def engineer_features(df):
    """
    Apply rolling mean smoothing, engineer MOI, WAI, Delta,
    and create target labels.
    """
    df = df.copy()

    # 7. Apply Rolling Average Smoothing (window=5) to sensor readings
    cols_to_smooth = ['Temperature', 'Humidity', 'Soil_Moisture', 'pH']
    for col in cols_to_smooth:
        df[col] = df[col].rolling(window=config.SMOOTHING_WINDOW, min_periods=1).mean()

    # Prevent division by zero or negative values in calculations
    df['Temperature'] = df['Temperature'].replace(0, 0.001)
    df['Soil_Moisture'] = df['Soil_Moisture'].replace(0, 0.001)

    # 1. Engineer Moisture Index (MOI)
    # MOI = (Humidity / Soil_Moisture) / Temperature
    df['MOI'] = (df['Humidity'] / df['Soil_Moisture']) / df['Temperature']

    # 2. Engineer Water Availability Index (WAI)
    # WAI = Soil_Moisture / (Rainfall + 1)
    df['WAI'] = df['Soil_Moisture'] / (df['Rainfall'] + 1)

    # 4. Implement Sensor Delta Analysis
    df['pH_delta'] = df['pH'].diff().fillna(0)
    df['Moisture_delta'] = df['Soil_Moisture'].diff().fillna(0)
    df['Temperature_delta'] = df['Temperature'].diff().fillna(0)

    # Flag rows where |Δ| > 2 × rolling_std as potential hardware interference events
    df['pH_interference_flag'] = (df['pH_delta'].abs() > 2 * df['pH_delta'].rolling(window=config.SMOOTHING_WINDOW, min_periods=1).std().fillna(0)).astype(int)
    df['Moisture_interference_flag'] = (df['Moisture_delta'].abs() > 2 * df['Moisture_delta'].rolling(window=config.SMOOTHING_WINDOW, min_periods=1).std().fillna(0)).astype(int)
    df['Temperature_interference_flag'] = (df['Temperature_delta'].abs() > 2 * df['Temperature_delta'].rolling(window=config.SMOOTHING_WINDOW, min_periods=1).std().fillna(0)).astype(int)


    # 3. Create binary target label Intervention_Required
    df['Intervention_Required'] = 0

    # Label = 1 when MOI or WAI falls outside 2 std from soil-type-specific mean
    soil_groups = df.groupby('Soil_Type')

    for soil, group in soil_groups:
        moi_mean = group['MOI'].mean()
        moi_std = group['MOI'].std()
        wai_mean = group['WAI'].mean()
        wai_std = group['WAI'].std()

        # Handle cases where std is NaN (e.g. only 1 sample)
        moi_std = moi_std if pd.notna(moi_std) else 0
        wai_std = wai_std if pd.notna(wai_std) else 0

        idx = group.index

        # Condition 1: MOI outside 2 std
        moi_outlier = (df.loc[idx, 'MOI'] > moi_mean + 2*moi_std) | (df.loc[idx, 'MOI'] < moi_mean - 2*moi_std)

        # Condition 2: WAI outside 2 std
        wai_outlier = (df.loc[idx, 'WAI'] > wai_mean + 2*wai_std) | (df.loc[idx, 'WAI'] < wai_mean - 2*wai_std)

        # Update target
        df.loc[idx[moi_outlier | wai_outlier], 'Intervention_Required'] = 1

    print(f"Target distribution before SMOTE:\n{df['Intervention_Required'].value_counts()}")

    # One-hot encode Soil_Type
    df = pd.get_dummies(df, columns=['Soil_Type'], drop_first=True)

    # Drop rows with NaN or infinite values after feature engineering (if any)
    df = df.replace([np.inf, -np.inf], np.nan).dropna()

    df.to_csv(config.FEATURE_DATA_PATH, index=False)
    print(f"Feature engineering completed and saved. Shape: {df.shape}")
    return df

def apply_smote(X, y):
    """Address class imbalance using SMOTE."""
    smote = SMOTE(random_state=config.RANDOM_STATE)
    X_resampled, y_resampled = smote.fit_resample(X, y)
    print(f"Target distribution after SMOTE:\n{pd.Series(y_resampled).value_counts()}")
    return X_resampled, y_resampled

if __name__ == "__main__":
    df = pd.read_csv(config.UNIFIED_DATA_PATH)
    engineer_features(df)
