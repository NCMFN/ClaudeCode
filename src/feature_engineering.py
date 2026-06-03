import pandas as pd
import numpy as np

def engineer_features(df: pd.DataFrame) -> pd.DataFrame:
    """
    Engineers synthetic features for the dataset.
    """
    # Create a copy
    df = df.copy()

    # 1. Energy-Noise Ratio (ENR)
    # Residual_Energy / (Ambient_Noise + ε)
    epsilon = 1e-5
    df['ENR'] = df['Residual_Energy'] / (df['Noise_Level'] + epsilon)

    # 2. Spatial Decay Factor (SDF)
    # 1 / (1 + sqrt((X - X_base)^2 + (Y - Y_base)^2))
    # Assume base station is at the centroid
    x_base = df['X_Coordinate'].mean()
    y_base = df['Y_Coordinate'].mean()

    distance = np.sqrt((df['X_Coordinate'] - x_base)**2 + (df['Y_Coordinate'] - y_base)**2)
    df['SDF'] = 1 / (1 + distance)

    # 3. Temporal Noise Smoothing
    # Rolling mean of Ambient Noise over a 5-sample window
    # If Timestamp exists, sort by it first, or by Node_ID
    if 'Timestamp' in df.columns:
        df['Timestamp'] = pd.to_datetime(df['Timestamp'])
        df = df.sort_values(by=['Node_ID', 'Timestamp'])
    else:
        df = df.sort_values(by=['Node_ID'])

    df['Temporal_Noise_Smoothing'] = df.groupby('Node_ID')['Noise_Level'].transform(
        lambda x: x.rolling(window=5, min_periods=1).mean()
    )

    # Alternatively, if there is no temporal sequence per node (e.g. 1 row per node),
    # the rolling window grouped by Node_ID will just be the single value.
    # Let's check if nodes have multiple rows.
    # Actually, in the primary dataset there are 10,000 unique node IDs and 10,000 rows.
    # So 1 row per node. The research step "Temporal Noise Smoothing = Rolling mean of
    # Ambient Noise over a 5-sample window" implies either we sort by timestamp and do a global
    # rolling window, or the dataset is temporal. Let's do a global rolling sorted by timestamp.
    df = df.sort_values(by='Timestamp')
    df['Temporal_Noise_Smoothing'] = df['Noise_Level'].rolling(window=5, min_periods=1).mean()

    return df

if __name__ == "__main__":
    from data_loader import download_data, load_all_datasets
    p_path, _, _ = download_data()
    df = load_all_datasets(p_path, None, None)
    df_engineered = engineer_features(df)

    print("Engineered Features:")
    print(df_engineered[['ENR', 'SDF', 'Temporal_Noise_Smoothing']].head())

    # Check correlation with Detection_Accuracy
    corr = df_engineered[['ENR', 'SDF', 'Temporal_Noise_Smoothing', 'Detection_Accuracy']].corr()
    print("\nCorrelation with Detection Accuracy:")
    print(corr['Detection_Accuracy'])
