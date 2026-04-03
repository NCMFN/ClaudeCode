import pandas as pd
import numpy as np

np.random.seed(42)
n_samples = 2000

# Generating realistic chemical composition and physical properties for SAF blends
data = {
    'Aromatics_vol_percent': np.random.normal(loc=15, scale=8, size=n_samples), # ASTM target 8-25%
    'Alkanes_vol_percent': np.random.normal(loc=60, scale=15, size=n_samples),
    'Cycloalkanes_vol_percent': np.random.normal(loc=20, scale=10, size=n_samples),
    'Olefins_vol_percent': np.random.exponential(scale=2, size=n_samples),
    'Kinematic_Viscosity_mms2': np.random.normal(loc=6, scale=3, size=n_samples), # ASTM Target <= 8.0 mm2/s
    'Density_kgm3': np.random.normal(loc=800, scale=30, size=n_samples), # target 775 - 840 kg/m3
    'Flash_Point_C': np.random.normal(loc=45, scale=10, size=n_samples), # min 38 C
    'Freezing_Point_C': np.random.normal(loc=-47, scale=15, size=n_samples), # max -40 C
    'Net_Heat_of_Combustion_MJkg': np.random.normal(loc=43.5, scale=1.5, size=n_samples) # min 42.8
}

df = pd.DataFrame(data)

# Ensure positive values where it makes sense
for col in df.columns:
    if col not in ['Freezing_Point_C']:
        df[col] = df[col].clip(lower=0)

# Normalize volume percentage to approximate 100% (Aromatics + Alkanes + Cycloalkanes + Olefins)
vol_cols = ['Aromatics_vol_percent', 'Alkanes_vol_percent', 'Cycloalkanes_vol_percent', 'Olefins_vol_percent']
totals = df[vol_cols].sum(axis=1)
for col in vol_cols:
    df[col] = (df[col] / totals) * 100

# Introduce some missing values to demonstrate handling
for col in df.columns:
    mask = np.random.rand(n_samples) < 0.05 # 5% missing
    df.loc[mask, col] = np.nan

# Define Drop-in Compatibility based on strict aviation standard criteria
def is_compatible(row):
    # Skip NA for labeling, we will drop them or just evaluate true conditions
    if pd.isna(row['Kinematic_Viscosity_mms2']) or pd.isna(row['Aromatics_vol_percent']) or pd.isna(row['Density_kgm3']) or pd.isna(row['Flash_Point_C']) or pd.isna(row['Freezing_Point_C']):
        return 0 # Conservative: missing critical properties -> incompatible

    cond1 = row['Kinematic_Viscosity_mms2'] <= 8.0
    cond2 = 8.0 <= row['Aromatics_vol_percent'] <= 25.0
    cond3 = 775 <= row['Density_kgm3'] <= 840
    cond4 = row['Flash_Point_C'] >= 38.0
    cond5 = row['Freezing_Point_C'] <= -40.0

    if cond1 and cond2 and cond3 and cond4 and cond5:
        return 1
    return 0

df['Drop_in_Compatible'] = df.apply(is_compatible, axis=1)

df.to_csv('SAF_Compatibility_Prediction/saf_dataset.csv', index=False)
print(f"Generated {n_samples} samples.")
print("Class distribution:")
print(df['Drop_in_Compatible'].value_counts())
