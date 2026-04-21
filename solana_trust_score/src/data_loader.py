import pandas as pd
import glob
import os
import sys

def load_and_audit_data(data_dir: str, output_audit_path: str) -> pd.DataFrame:
    csv_files = glob.glob(os.path.join(data_dir, "*.csv"))
    if not csv_files:
        raise FileNotFoundError(f"No CSV files found in {data_dir}")

    dfs = []
    for f in csv_files:
        print(f"Loading {f}...")
        df = pd.read_csv(f)
        dfs.append(df)

    df_full = pd.concat(dfs, ignore_index=True)
    print("Data loaded successfully.")

    audit_lines = []
    audit_lines.append("=== Data Audit Report ===\n")
    audit_lines.append(f"Shape: {df_full.shape}\n")

    audit_lines.append("--- Dtypes ---\n")
    audit_lines.append(str(df_full.dtypes) + "\n\n")

    audit_lines.append("--- Null Counts ---\n")
    audit_lines.append(str(df_full.isnull().sum()) + "\n\n")

    audit_lines.append("--- Target Class Distribution ---\n")
    if 'INACTIVITY_STATUS' in df_full.columns:
        audit_lines.append(str(df_full['INACTIVITY_STATUS'].value_counts(dropna=False)) + "\n\n")
    else:
        audit_lines.append("INACTIVITY_STATUS column not found.\n\n")

    audit_lines.append("--- Descriptive Statistics ---\n")
    audit_lines.append(str(df_full.describe()) + "\n\n")

    audit_lines.append("--- Duplicates ---\n")
    if 'LIQUIDITY_POOL_ADDRESS' in df_full.columns:
        n_duplicates = df_full.duplicated(subset=['LIQUIDITY_POOL_ADDRESS']).sum()
        audit_lines.append(f"Duplicate LIQUIDITY_POOL_ADDRESS entries: {n_duplicates}\n")
        if n_duplicates > 0:
            df_full = df_full.drop_duplicates(subset=['LIQUIDITY_POOL_ADDRESS']).reset_index(drop=True)
            audit_lines.append(f"Dropped duplicates. New shape: {df_full.shape}\n")
    else:
        audit_lines.append("LIQUIDITY_POOL_ADDRESS column not found.\n")

    audit_text = "".join(audit_lines)
    print(audit_text)

    os.makedirs(os.path.dirname(output_audit_path), exist_ok=True)
    with open(output_audit_path, "w") as f:
        f.write(audit_text)

    return df_full
