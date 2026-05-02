import pandas as pd
import numpy as np
import os
from sklearn.impute import SimpleImputer
from sklearn.preprocessing import OrdinalEncoder

def preprocess_data(data_path, output_dir):
    """
    Load NHIS data, filter for age 20-39, extract features,
    handle missing values, and encode categorical variables.
    """
    raw_file = os.path.join(data_path, 'adult22.csv')
    if not os.path.exists(raw_file):
        raise FileNotFoundError(f"Raw data file not found at {raw_file}")

    print("Loading raw data...")
    df = pd.read_csv(raw_file)

    # 1. Filter Age (20-39)
    # NHIS 2022 age variable is AGEP_A. Top coded at 85.
    df = df[(df['AGEP_A'] >= 20) & (df['AGEP_A'] <= 39)].copy()
    print(f"Filtered for age 20-39. Rows remaining: {len(df)}")

    # 2. Define binary target: High Risk (1) if CVDMI_A == 1 OR CHDEV_A == 1
    # 1=Yes, 2=No, 7=Refused, 8=Not Ascertained, 9=Don't Know
    def create_label(row):
        # MIEV_A: Ever told you had a heart attack
        # CHDEV_A: Ever told you had coronary heart disease
        mi = row.get('MIEV_A', 2)
        chd = row.get('CHDEV_A', 2)
        if mi == 1 or chd == 1:
            return 1
        return 0

    df['label'] = df.apply(create_label, axis=1)

    # 3. Extract key features
    # Mental health: ANXEV_A (anxiety), DEPEV_A (depression)
    # Cardiac: CHDEV_A, MIEV_A
    # Vitals proxies: BMICAT_A (BMI cat), HYPEV_A (hypertension), DIBEV_A (diabetes)
    # Behavioral: SMKNOW_A (smoking), DRKSTAT_A (alcohol), WLKLEIS_A (walk for leisure proxy)
    # Socioeconomic: POVRATTC_A (poverty ratio), EDUCP_A (education), SEX_A, HISPALLP_A (race/eth)
    # Also grab WTFA_A for survey weights if needed, but the prompt says
    # "sample without replacement using WTFA_A weights" - will do in features.py or train.py if needed.

    cols_to_keep = [
        'AGEP_A', 'SEX_A', 'HISPALLP_A', 'EDUCP_A', 'POVRATTC_A',
        'BMICAT_A', 'HYPEV_A', 'DIBEV_A',
        'SMKNOW_A', 'DRKSTAT_A', 'WLKLEIS_A',
        'ANXEV_A', 'DEPEV_A', 'RX12M_A', # RX12M_A as a proxy if psych medication isn't specific
        'WTFA_A', 'label'
    ]

    # Only keep available columns
    available_cols = [c for c in cols_to_keep if c in df.columns]
    df = df[available_cols].copy()

    # 4. Handle missing values & codes
    # In NHIS, 7=Refused, 8=Not Ascertained, 9=Don't Know are typically missing.
    # For some columns like BMICAT_A, 9 is unknown.
    def replace_missing_codes(val):
        if pd.isna(val):
            return np.nan
        if val in [7, 8, 9, 97, 98, 99]:
            return np.nan
        return val

    # Apply missing code replacement to categorical/ordinal columns
    cat_cols = ['SEX_A', 'HISPALLP_A', 'EDUCP_A', 'BMICAT_A', 'HYPEV_A', 'DIBEV_A',
                'SMKNOW_A', 'DRKSTAT_A', 'WLKLEIS_A', 'ANXEV_A', 'DEPEV_A', 'RX12M_A']
    for col in cat_cols:
        if col in df.columns:
            df[col] = df[col].apply(replace_missing_codes)

    # POVRATTC_A and AGEP_A are continuous/ordinal, but 99 might be missing for some.
    # But POVRATTC_A is ratio, usually imputed already.

    print("Imputing missing values...")
    # Impute categorical with mode
    existing_cat_cols = [c for c in cat_cols if c in df.columns]
    cat_imputer = SimpleImputer(strategy='most_frequent')
    df[existing_cat_cols] = cat_imputer.fit_transform(df[existing_cat_cols])

    # Impute continuous with median
    cont_cols = ['AGEP_A', 'POVRATTC_A']
    existing_cont_cols = [c for c in cont_cols if c in df.columns]
    cont_imputer = SimpleImputer(strategy='median')
    df[existing_cont_cols] = cont_imputer.fit_transform(df[existing_cont_cols])

    # 5. Encode categoricals with OrdinalEncoder (excluding features that will be One-Hot Encoded later,
    # but prompt step 1 says "Encode categoricals with OrdinalEncoder".
    # Let's ordinal encode everything for now, except those we specifically want to OHE in features.py
    # or just ordinal encode everything to be safe).
    # Since Step 2 says "One-hot encode race/ethnicity and education", let's keep them as is
    # or ordinal encode them and then OHE them later. It's fine to ordinal encode first.
    print("Ordinal encoding categorical variables...")
    encoder = OrdinalEncoder()
    df[existing_cat_cols] = encoder.fit_transform(df[existing_cat_cols])

    # Output to csv
    os.makedirs(os.path.dirname(os.path.join(output_dir, 'nhis_processed.csv')), exist_ok=True)
    out_file = os.path.join(output_dir, 'nhis_processed.csv')
    df.to_csv(out_file, index=False)
    print(f"Preprocessing complete. Saved to {out_file}. Positive class ratio: {df['label'].mean():.4f}")

    return df

if __name__ == "__main__":
    preprocess_data('heart_mind_cvd/data/nhis_raw/', 'heart_mind_cvd/data/')
