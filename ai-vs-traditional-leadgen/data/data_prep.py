import pandas as pd
import numpy as np
from ucimlrepo import fetch_ucirepo
import kagglehub
import os

def prep_uci_bank():
    print("Preparing UCI Bank dataset...")
    # fetch dataset
    bank_marketing = fetch_ucirepo(id=222)

    # data (as pandas dataframes)
    X = bank_marketing.data.features
    y = bank_marketing.data.targets

    # y contains 'yes'/'no'
    y = (y['y'] == 'yes').astype(int)

    df = pd.concat([X, y.rename('y')], axis=1)
    df.to_csv('data/uci_bank.csv', index=False)
    print("Saved data/uci_bank.csv, shape:", df.shape)

def prep_kaggle_lead_scoring():
    print("Preparing Kaggle Lead Scoring dataset...")
    path = kagglehub.dataset_download("amritachatterjee09/lead-scoring-dataset")
    df = pd.read_csv(os.path.join(path, "Lead Scoring.csv"))
    df.to_csv('data/kaggle_lead_scoring.csv', index=False)
    print("Saved data/kaggle_lead_scoring.csv, shape:", df.shape)

def prep_kaggle_b2b():
    print("Preparing Kaggle B2B CRM dataset...")
    path = kagglehub.dataset_download("ezogngrd/synthetic-b2b-crm-and-marketing-data")

    df_clean = pd.read_csv(os.path.join(path, "employees_clean_5234.csv"))
    df_noisy = pd.read_csv(os.path.join(path, "employees_noisy_5234.csv"))

    df_clean.to_csv('data/kaggle_b2b_clean.csv', index=False)
    df_noisy.to_csv('data/kaggle_b2b_noisy.csv', index=False)
    print("Saved data/kaggle_b2b_clean.csv, shape:", df_clean.shape)
    print("Saved data/kaggle_b2b_noisy.csv, shape:", df_noisy.shape)

if __name__ == "__main__":
    prep_uci_bank()
    prep_kaggle_lead_scoring()
    prep_kaggle_b2b()
