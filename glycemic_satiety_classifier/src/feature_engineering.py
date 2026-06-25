import pandas as pd
import numpy as np
import os
from imblearn.over_sampling import SMOTE

def feature_engineering(df, out_tab_dir):
    # Step 3.1 - Glycemic Load Calculation

    # Identify missing GI
    missing_gi = df['GI_value'].isna()

    if missing_gi.any():
        # Impute using category median
        gi_medians = df.groupby('Category')['GI_value'].median()
        # Fallback to global median if category median is missing
        global_median = df['GI_value'].median()

        imputation_log = []

        def impute_gi(row):
            if pd.isna(row['GI_value']):
                cat = row['Category']
                val = gi_medians.get(cat, global_median)
                if pd.isna(val):
                    val = global_median
                imputation_log.append({'Food': row['Food'], 'Category': cat, 'Imputed_GI': val})
                return val
            return row['GI_value']

        df['GI_value'] = df.apply(impute_gi, axis=1)

        if imputation_log:
            pd.DataFrame(imputation_log).to_csv(os.path.join(out_tab_dir, 'gi_imputation_log.csv'), index=False)

    df['Avail_Carb_g'] = df['Carbohydrate_g'] - df['Fiber_g']
    df['Avail_Carb_g'] = df['Avail_Carb_g'].clip(lower=0)
    df['GL'] = (df['GI_value'] * df['Avail_Carb_g']) / 100

    # Step 3.2 - Derived Features
    df['Fiber_to_Carb_Ratio'] = df['Fiber_g'] / (df['Carbohydrate_g'] + 1e-6)
    df['Energy_Density'] = df['Energy_kcal'] / 100
    df['Protein_Energy_Fraction'] = (df['Protein_g'] * 4) / (df['Energy_kcal'] + 1e-6)
    df['Water_Energy_Ratio'] = df['Water_g'] / (df['Energy_kcal'] + 1e-6)

    # Step 3.3 - Categorical Encoding

    # Category (OHE)
    df = pd.get_dummies(df, columns=['Category'], prefix='cat')

    # Extract prep method from Food name
    # {Raw, Boiled, Roasted, Fried, Ultra-processed, Unknown}
    def get_prep(name):
        name = str(name).lower()
        if 'raw' in name: return 'Raw'
        if 'boil' in name: return 'Boiled'
        if 'roast' in name: return 'Roasted'
        if 'fri' in name or 'fried' in name: return 'Fried'
        if 'commercial' in name or 'ultra' in name or 'process' in name: return 'Ultra-processed'
        return 'Unknown'

    df['preparation_method'] = df['Food'].apply(get_prep)

    # Flag boiling effect
    # Note: Boiling significantly increases starch crystallisation (retrograde starch),
    # which reduces GI and increases physical bulk

    df = pd.get_dummies(df, columns=['preparation_method'], prefix='prep')

    # Step 3.4 - Target Variable
    def get_tier(si):
        if si < 80: return 'LOW'
        if si <= 150: return 'MEDIUM'
        return 'HIGH'

    df['Satiety_Tier'] = df['Satiety_Index'].apply(get_tier)

    print("Class distribution before SMOTE:")
    print(df['Satiety_Tier'].value_counts())

    # Apply SMOTE if needed (will do this during model training split to avoid data leakage)
    # The prompt says: "apply SMOTE if any class is under-represented (<20% of total)."
    # We will compute the flag here but apply SMOTE strictly on training data in models.py

    return df

def main():
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    proc_dir = os.path.join(base_dir, 'data', 'processed')
    out_tab_dir = os.path.join(base_dir, 'outputs', 'tables')

    df = pd.read_csv(os.path.join(proc_dir, 'satiety_features.csv'))

    df_engineered = feature_engineering(df, out_tab_dir)

    df_engineered.to_csv(os.path.join(proc_dir, 'satiety_features_engineered.csv'), index=False)

    print("Engineered dataset saved.")
    print("Final features list:", df_engineered.columns.tolist())
    print("Shape:", df_engineered.shape)

if __name__ == "__main__":
    main()
