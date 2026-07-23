import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.impute import SimpleImputer
from sklearn.preprocessing import StandardScaler
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import LabelEncoder

def load_data(filepath='data/telegraph_faults.csv'):
    """Loads the synthetic dataset."""
    df = pd.read_csv(filepath)
    return df

def feature_engineering(df):
    """
    Applies feature engineering:
    - Creates R*C interaction term
    """
    df_eng = df.copy()
    # Create R*C interaction term (part of Kelvin's law: t ~ R*C*L^2)
    # R * C represents the time constant per unit length squared
    if 'resistance_ohm_per_mi' in df_eng.columns and 'capacitance_uf_per_mi' in df_eng.columns:
        df_eng['RC_interaction'] = df_eng['resistance_ohm_per_mi'] * df_eng['capacitance_uf_per_mi']

    return df_eng

def get_preprocessor(numeric_features):
    """
    Returns a ColumnTransformer for preprocessing.
    Imputes missing values with median and scales using StandardScaler.
    """
    numeric_transformer = Pipeline(steps=[
        ('imputer', SimpleImputer(strategy='median')),
        ('scaler', StandardScaler())
    ])

    preprocessor = ColumnTransformer(
        transformers=[
            ('num', numeric_transformer, numeric_features)
        ], remainder='passthrough')

    return preprocessor

def prepare_data(df, test_size=0.2, random_state=42):
    """
    Prepares data for modeling.
    - Encodes labels
    - Splits into train/test with stratification
    - Returns X_train, X_test, y_train, y_test, preprocessor, and label_encoder
    """
    df = feature_engineering(df)

    X = df.drop('fault_class', axis=1)
    y_raw = df['fault_class']

    le = LabelEncoder()
    y = le.fit_transform(y_raw)

    numeric_features = X.columns.tolist()

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=test_size, random_state=random_state, stratify=y
    )

    preprocessor = get_preprocessor(numeric_features)

    return X_train, X_test, y_train, y_test, preprocessor, le, numeric_features
