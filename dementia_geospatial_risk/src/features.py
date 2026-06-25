import pandas as pd
import numpy as np
from sklearn.preprocessing import RobustScaler, OneHotEncoder
import joblib
from pathlib import Path

DATA_DIR = Path("dementia_geospatial_risk/data")
PROCESSED_DIR = DATA_DIR / "processed"
INTERIM_DIR = DATA_DIR / "interim"

def build_features():
    df = pd.read_csv(PROCESSED_DIR / "merged_county_features.csv", dtype={'FIPS': str, 'state_fips': str})

    if 'scd_prevalence' not in df.columns:
        print("Missing Target Variable. Halting.")
        return

    # Discretise into three classes using tertile thresholds
    tertiles = df['scd_prevalence'].quantile([0.33, 0.66]).values

    def classify_risk(x):
        if x <= tertiles[0]:
            return 0 # Low Risk
        elif x <= tertiles[1]:
            return 1 # Medium Risk
        else:
            return 2 # High Risk

    df['target_risk_class'] = df['scd_prevalence'].apply(classify_risk)

    # Feature transformations based on instructions
    scaler = RobustScaler()

    # Only scale existing features safely
    robust_features = []
    for f in ['solar_exposure_index', 'latitude_gradient', 'ozone_annual_mean', 'median_age', 'pct_over65']:
        if f in df.columns and not df[f].isna().all():
            robust_features.append(f)

    if robust_features:
        df[robust_features] = scaler.fit_transform(df[robust_features].fillna(df[robust_features].median()))

    if 'population_density' in df.columns and not df['population_density'].isna().all():
        df['population_density'] = np.log1p(df['population_density'].fillna(df['population_density'].median()))
        df['population_density'] = scaler.fit_transform(df[['population_density']])

    # One-hot encoding
    encoder_state = OneHotEncoder(sparse_output=False, handle_unknown='ignore')
    state_encoded = encoder_state.fit_transform(df[['state_fips']])
    state_cols = [f"state_{c}" for c in encoder_state.categories_[0]]
    df_state = pd.DataFrame(state_encoded, columns=state_cols, index=df.index)

    df_final = pd.concat([df, df_state], axis=1)

    if 'urban_rural_class' in df.columns:
        encoder_urban = OneHotEncoder(sparse_output=False, handle_unknown='ignore')
        urban_encoded = encoder_urban.fit_transform(df[['urban_rural_class']])
        urban_cols = [f"urban_{c}" for c in encoder_urban.categories_[0]]
        df_urban = pd.DataFrame(urban_encoded, columns=urban_cols, index=df.index)
        df_final = pd.concat([df_final, df_urban], axis=1)

    # Save prepared dataset
    df_final.to_csv(PROCESSED_DIR / "model_ready_data.csv", index=False)
    print(f"Features built and saved. Final shape: {df_final.shape}")

    return df_final

if __name__ == "__main__":
    build_features()
