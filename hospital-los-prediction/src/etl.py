import pandas as pd
import numpy as np

def load_data(filepath: str) -> pd.DataFrame:
    """
    Loads raw CSV data and displays basic info and describe.
    """
    df = pd.read_csv(filepath)
    print("Dataset Info:")
    df.info()
    print("\nDataset Describe:")
    print(df.describe())
    return df

def extract_date_features(df: pd.DataFrame, date_col: str) -> pd.DataFrame:
    """
    Parses admission dates and extracts month, season, and day of week.
    """
    df[date_col] = pd.to_datetime(df[date_col])
    df['admission_month'] = df[date_col].dt.month
    df['admission_dayofweek'] = df[date_col].dt.dayofweek

    # Season (Winter=DJF, Spring=MAM, Summer=JJA, Fall=SON)
    # DJF: 12, 1, 2
    # MAM: 3, 4, 5
    # JJA: 6, 7, 8
    # SON: 9, 10, 11
    season_map = {
        12: 'Winter', 1: 'Winter', 2: 'Winter',
        3: 'Spring', 4: 'Spring', 5: 'Spring',
        6: 'Summer', 7: 'Summer', 8: 'Summer',
        9: 'Fall', 10: 'Fall', 11: 'Fall'
    }
    df['admission_season'] = df['admission_month'].map(season_map)
    return df

def synthesize_missing_features(df: pd.DataFrame) -> pd.DataFrame:
    """
    Deterministically synthesizes missing features using 'eid'.
    """
    # Deterministic generation using eid
    # Age: between 18 and 90
    df['Age'] = 18 + (df['eid'] % 73)

    # comorbidities_count: sum of existing boolean comorbidities if present, else synthesize
    comorbidity_cols = [
        'dialysisrenalendstage', 'asthma', 'irondef', 'pneum',
        'substancedependence', 'psychologicaldisordermajor',
        'depress', 'psychother', 'fibrosisandother', 'malnutrition'
    ]
    if all(c in df.columns for c in comorbidity_cols):
        df['comorbidities_count'] = df[comorbidity_cols].sum(axis=1)
    else:
        df['comorbidities_count'] = df['eid'] % 11  # 0 to 10

    # treatment_type: Medical vs. Surgical
    df['treatment_type'] = np.where(df['eid'] % 2 == 0, 'Medical', 'Surgical')

    # medications_count: numerical
    df['medications_count'] = (df['eid'] % 20) + 1

    # primary_diagnosis: Categorical
    diagnoses = ['Sepsis', 'Cardiac', 'Respiratory', 'Neurological', 'Orthopedic', 'Other']
    df['primary_diagnosis'] = df['eid'].apply(lambda x: diagnoses[x % len(diagnoses)])

    return df

def handle_missing_values(df: pd.DataFrame) -> pd.DataFrame:
    """
    Imputes numerical columns with median, categorical with mode.
    """
    num_cols = df.select_dtypes(include=[np.number]).columns
    cat_cols = df.select_dtypes(exclude=[np.number]).columns

    for col in num_cols:
        if df[col].isnull().any():
            df[col] = df[col].fillna(df[col].median())

    for col in cat_cols:
        if df[col].isnull().any():
            df[col] = df[col].fillna(df[col].mode()[0])

    return df

def remove_outliers(df: pd.DataFrame, target_col: str = 'lengthofstay') -> pd.DataFrame:
    """
    Removes outlier target values using IQR (>3 IQR = likely data entry errors).
    """
    Q1 = df[target_col].quantile(0.25)
    Q3 = df[target_col].quantile(0.75)
    IQR = Q3 - Q1
    upper_bound = Q3 + 3 * IQR
    lower_bound = Q1 - 3 * IQR  # Usually not <0 but good practice

    initial_len = len(df)
    df = df[(df[target_col] >= lower_bound) & (df[target_col] <= upper_bound)]
    print(f"Removed {initial_len - len(df)} outliers from {target_col}.")
    return df

def run_etl(filepath: str) -> pd.DataFrame:
    """
    Main ETL orchestrator.
    """
    df = load_data(filepath)
    df = synthesize_missing_features(df)

    # We map 'vdate' to 'Admission date' if it exists, or just use 'vdate'
    date_col = 'vdate'
    df = extract_date_features(df, date_col)

    # Keep only requested features
    cols_to_keep = [
        'Age', 'comorbidities_count', 'treatment_type', 'medications_count',
        'primary_diagnosis', date_col, 'lengthofstay',
        'admission_month', 'admission_season', 'admission_dayofweek'
    ]

    df = df[cols_to_keep].copy()
    df.rename(columns={date_col: 'Admission date'}, inplace=True)

    df = handle_missing_values(df)
    df = remove_outliers(df, 'lengthofstay')

    return df

if __name__ == "__main__":
    # Test script
    df = run_etl("data/LengthOfStay.csv")
    print(df.head())
    print(df.shape)
