import os
import io
import pandas as pd
import numpy as np
import requests
import kagglehub
from sklearn.datasets import load_breast_cancer
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler

DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data')
os.makedirs(DATA_DIR, exist_ok=True)

# Configuration for downsampling large datasets in fast mode
DATASET_CONFIG = {
    "CC_Fraud": {"max_rows": 1000, "stratify": True},
    "Loan_Default": {"max_rows": 1000, "stratify": True},
    # others: None (use full dataset)
}

def fetch_breast_cancer():
    """Fetches Breast Cancer Wisconsin dataset."""
    try:
        data = load_breast_cancer()
        df = pd.DataFrame(data.data, columns=data.feature_names)
        df['target'] = data.target
        return df
    except Exception as e:
        print(f"Error fetching Breast Cancer: {e}")
        return pd.DataFrame()

def fetch_heart_disease():
    """Fetches Heart Disease dataset from UCI."""
    try:
        url = "https://archive.ics.uci.edu/ml/machine-learning-databases/heart-disease/processed.cleveland.data"
        response = requests.get(url, timeout=10)
        response.raise_for_status()

        cols = ['age', 'sex', 'cp', 'trestbps', 'chol', 'fbs', 'restecg', 'thalach',
                'exang', 'oldpeak', 'slope', 'ca', 'thal', 'target']
        df = pd.read_csv(io.StringIO(response.text), names=cols, na_values="?")
        # Convert target to binary (0 = no disease, 1 = disease)
        df['target'] = (df['target'] > 0).astype(int)
        return df
    except Exception as e:
        print(f"Error fetching Heart Disease: {e}")
        return pd.DataFrame()

def fetch_pima_diabetes():
    """Fetches Pima Indians Diabetes dataset."""
    try:
        # Pima Diabetes is readily available on GitHub/UCI mirrors
        url = "https://raw.githubusercontent.com/jbrownlee/Datasets/master/pima-indians-diabetes.data.csv"
        cols = ['Pregnancies', 'Glucose', 'BloodPressure', 'SkinThickness', 'Insulin',
                'BMI', 'DiabetesPedigreeFunction', 'Age', 'target']
        df = pd.read_csv(url, names=cols)
        return df
    except Exception as e:
        print(f"Error fetching Pima Diabetes: {e}")
        return pd.DataFrame()

def fetch_kaggle_dataset(handle, filename, target_col):
    """Generic function to fetch a Kaggle dataset using kagglehub."""
    try:
        # Download dataset
        path = kagglehub.dataset_download(handle)

        # Find the CSV file
        csv_path = None
        for root, _, files in os.walk(path):
            for file in files:
                if file.endswith(filename) or (filename == "" and file.endswith('.csv')):
                    csv_path = os.path.join(root, file)
                    break

        if csv_path:
            df = pd.read_csv(csv_path)
            if target_col in df.columns and target_col != 'target':
                df = df.rename(columns={target_col: 'target'})
            return df
        else:
            print(f"CSV file {filename} not found in {path}")
            return pd.DataFrame()

    except Exception as e:
        print(f"Error fetching Kaggle dataset {handle}: {e}")
        return pd.DataFrame()

def fetch_credit_card_fraud():
    """Fetches Credit Card Fraud Detection."""
    return fetch_kaggle_dataset("mlg-ulb/creditcardfraud", "creditcard.csv", "Class")

def fetch_loan_default():
    """Fetches Loan Default Dataset."""
    return fetch_kaggle_dataset("yasserh/loan-default-dataset", "Loan_Default.csv", "Status")

def fetch_financial_distress():
    """Fetches Financial Distress Dataset."""
    return fetch_kaggle_dataset("shebrahimi/financial-distress", "Financial Distress.csv", "Financial Distress")

def load_all_datasets(fast_mode=False):
    """Loads all datasets into a dictionary."""
    print(f"Loading datasets... (Fast Mode: {fast_mode})")
    datasets = {
        'Breast_Cancer': fetch_breast_cancer(),
        'Heart_Disease': fetch_heart_disease(),
        'Pima_Diabetes': fetch_pima_diabetes(),
        'CC_Fraud': fetch_credit_card_fraud(),
        'Loan_Default': fetch_loan_default(),
        'Financial_Distress': fetch_financial_distress()
    }

    # Filter out empty datasets
    loaded_datasets = {k: v for k, v in datasets.items() if not v.empty}
    print(f"Successfully loaded {len(loaded_datasets)} datasets.")

    for k, df in loaded_datasets.items():
        if k == 'Financial_Distress':
            # Needs specific processing for target: > -0.5 is healthy (0), <= -0.5 is distress (1)
            df['target'] = (df['target'] <= -0.5).astype(int)

        # Downsample if fast_mode is enabled
        if fast_mode and k in DATASET_CONFIG:
            config = DATASET_CONFIG[k]
            max_rows = config['max_rows']
            if len(df) > max_rows:
                print(f"[{k}] Downsampling from {len(df)} to {max_rows} rows...")
                if config.get('stratify') and 'target' in df.columns:
                    # Stratified downsampling
                    try:
                        _, df = train_test_split(df, test_size=max_rows, stratify=df['target'], random_state=42)
                    except ValueError:
                        # Fallback if stratification fails (e.g. single class)
                        df = df.sample(n=max_rows, random_state=42)
                else:
                    df = df.sample(n=max_rows, random_state=42)
                loaded_datasets[k] = df.reset_index(drop=True)

    return loaded_datasets

def preprocess_dataset(df, dataset_name):
    """
    Handles missing values, creates an 80/20 train-test split,
    and applies StandardScaler (fitted ONLY on train data).
    Returns X_train_scaled, X_test_scaled, y_train, y_test, feature_names.
    """
    # 1. Handle missing values
    # For simplicity and robust fallback, we impute numeric with median
    if df.isnull().sum().sum() > 0:
        print(f"[{dataset_name}] Imputing missing values with median.")
        for col in df.columns:
            if df[col].isnull().any():
                if pd.api.types.is_numeric_dtype(df[col]):
                    df[col] = df[col].fillna(df[col].median())
                else:
                    df[col] = df[col].fillna(df[col].mode()[0])

    # Identify non-numeric columns and convert them using dummy encoding if any
    non_numeric = df.select_dtypes(exclude=[np.number]).columns
    if len(non_numeric) > 0:
        print(f"[{dataset_name}] One-hot encoding categorical variables: {list(non_numeric)}")
        df = pd.get_dummies(df, columns=non_numeric, drop_first=True)

    # Separate X and y
    y = df['target'].values
    X = df.drop(columns=['target'])
    feature_names = X.columns.tolist()
    X = X.values

    # 2. 80/20 Train-test split (stratified, random_state=42)
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.20, stratify=y, random_state=42
    )

    # 3. StandardScaler (fit ONLY on training data)
    scaler = StandardScaler()
    X_train_scaled = scaler.fit_transform(X_train)
    X_test_scaled = scaler.transform(X_test)

    # We also return X_train before scaling for metrics that need mean of train data
    return {
        'X_train': X_train_scaled,
        'X_test': X_test_scaled,
        'X_train_unscaled': X_train,
        'y_train': y_train,
        'y_test': y_test,
        'feature_names': feature_names,
        'scaler': scaler
    }
