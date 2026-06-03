import pandas as pd
import numpy as np
import kagglehub
import os
import glob
from typing import Tuple

def download_data() -> Tuple[str, str, str]:
    """
    Downloads datasets from Kaggle using kagglehub.
    Returns the paths to the extracted directories.
    """
    path_primary = kagglehub.dataset_download("ziya07/wireless-sensor-network-dataset")
    path_wsn_ds = kagglehub.dataset_download("bassamkasasbeh1/wsnds")
    path_loc = kagglehub.dataset_download("ziya07/wireless-sensor-network-node-localization-dataset")
    return path_primary, path_wsn_ds, path_loc

def load_all_datasets(path_primary: str, path_wsn_ds: str, path_loc: str) -> pd.DataFrame:
    """
    Loads all datasets, inspects them, and merges them if possible.
    Since Node IDs do not directly overlap, we primarily use the primary dataset
    but demonstrate the inspection and loading of the others.
    """
    # Load Primary
    p_files = glob.glob(os.path.join(path_primary, "*.csv"))
    if not p_files: raise FileNotFoundError(f"No CSV found in {path_primary}")
    df_primary = pd.read_csv(p_files[0])

    # Ensure SNR exists: Signal_Strength - Noise_Level (assume dB)
    if 'SNR' not in df_primary.columns and 'Signal_Strength' in df_primary.columns and 'Noise_Level' in df_primary.columns:
        df_primary['SNR'] = df_primary['Signal_Strength'] - df_primary['Noise_Level']

    # Load WSN-DS
    w_files = glob.glob(os.path.join(path_wsn_ds, "*.csv"))
    if w_files:
        df_wsn = pd.read_csv(w_files[0])
        print("WSN-DS shape:", df_wsn.shape)
        print("WSN-DS Columns:", df_wsn.columns.tolist())
        # Clean column names
        df_wsn.columns = df_wsn.columns.str.strip()
        # Merge if possible. The IDs are 'id' vs 'Node_ID'. In reality, WSN-DS has different node ids.
        # We will keep df_primary as our main dataset for the regression as it has 'Detection_Accuracy'

    # Load Loc
    l_files = glob.glob(os.path.join(path_loc, "*.csv"))
    if l_files:
        df_loc = pd.read_csv(l_files[0])
        print("Loc Dataset shape:", df_loc.shape)
        print("Loc Dataset Columns:", df_loc.columns.tolist())

        # Merge Localization if overlapping
        # Primary has 1-10000. Loc has 0-499. Let's merge the overlapping 1-499.
        # Actually it's best to merge on Node_ID. Left merge so we don't lose the 10k rows.
        df_primary = pd.merge(df_primary, df_loc[['Node_ID', 'Anchor_Status', 'Obstacle_Presence']], on='Node_ID', how='left')

    return df_primary

if __name__ == "__main__":
    p_path, w_path, l_path = download_data()
    df = load_all_datasets(p_path, w_path, l_path)
    print("Primary dataset loaded with shape:", df.shape)
    print("Columns:", df.columns.tolist())
