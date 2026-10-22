import pandas as pd
from sklearn.preprocessing import StandardScaler, OneHotEncoder
from sklearn.compose import ColumnTransformer
from imblearn.over_sampling import SMOTE
import yaml

def get_preprocessor():
    numeric_cols = ['Air temperature', 'Process temperature', 'Rotational speed', 'Torque', 'Tool wear', 'Thermal_delta', 'Mechanical_power']
    categorical_cols = ['Type']

    preprocessor = ColumnTransformer(
        transformers=[
            ('num', StandardScaler(), numeric_cols),
            ('cat', OneHotEncoder(drop='first'), categorical_cols)
        ],
        remainder='passthrough'
    )
    return preprocessor

def handle_imbalance(X_train, y_train, strategy='smote', random_seed=42):
    if strategy == 'smote':
        smote = SMOTE(random_state=random_seed)
        X_res, y_res = smote.fit_resample(X_train, y_train)
        return X_res, y_res
    elif strategy == 'class_weight':
        return X_train, y_train
    else:
        return X_train, y_train
