import pandas as pd
import numpy as np
from sklearn.base import BaseEstimator, TransformerMixin
from sklearn.pipeline import Pipeline
from sklearn.compose import ColumnTransformer
from sklearn.preprocessing import StandardScaler, OneHotEncoder
import category_encoders as ce

class InteractionTermAdder(BaseEstimator, TransformerMixin):
    """
    Custom transformer to add interaction terms.
    Specifically: age_x_comorbidities = Age * comorbidities_count
    """
    def __init__(self, col1='Age', col2='comorbidities_count', new_col='age_x_comorbidities'):
        self.col1 = col1
        self.col2 = col2
        self.new_col = new_col
        self.feature_names_in_ = None

    def fit(self, X, y=None):
        if hasattr(X, "columns"):
            self.feature_names_in_ = np.array(X.columns)
        return self

    def transform(self, X):
        X_out = X.copy()
        if isinstance(X_out, pd.DataFrame):
            X_out[self.new_col] = X_out[self.col1] * X_out[self.col2]
        else:
            col1_idx = np.where(self.feature_names_in_ == self.col1)[0][0]
            col2_idx = np.where(self.feature_names_in_ == self.col2)[0][0]
            new_col_val = X_out[:, col1_idx] * X_out[:, col2_idx]
            X_out = np.column_stack((X_out, new_col_val))
        return X_out

    def get_feature_names_out(self, input_features=None):
        if input_features is None:
            input_features = self.feature_names_in_
        if input_features is not None:
            return np.append(input_features, self.new_col)
        return None

def build_preprocessor() -> Pipeline:
    """
    Builds and returns the full feature engineering pipeline.
    """
    interaction = InteractionTermAdder()

    te_cols = ['primary_diagnosis']
    ohe_cols = ['treatment_type', 'admission_season']

    # Updated numeric columns list containing ONLY those in the restricted dataset
    numeric_cols = [
        'Age', 'comorbidities_count', 'medications_count', 'age_x_comorbidities',
        'admission_month', 'admission_dayofweek'
    ]

    col_transformer = ColumnTransformer(
        transformers=[
            ('woe_equivalent', ce.TargetEncoder(), te_cols),
            ('ohe', OneHotEncoder(drop='first', sparse_output=False), ohe_cols),
            ('scaler', StandardScaler(), numeric_cols)
        ],
        remainder='drop'
    )

    pipeline = Pipeline(steps=[
        ('interaction', interaction),
        ('preprocessor', col_transformer)
    ])

    return pipeline

def get_feature_names(pipeline, ohe_cols=['treatment_type', 'admission_season']):
    try:
        ohe_feature_names = pipeline.named_steps['preprocessor'].named_transformers_['ohe'].get_feature_names_out(input_features=ohe_cols)
    except Exception:
        ohe_feature_names = ['treatment_type_Surgical', 'admission_season_Spring', 'admission_season_Summer', 'admission_season_Winter']

    numeric_cols = [
        'Age', 'comorbidities_count', 'medications_count', 'age_x_comorbidities',
        'admission_month', 'admission_dayofweek'
    ]

    feature_names = ['primary_diagnosis_woe'] + list(ohe_feature_names) + numeric_cols
    return feature_names

def evaluate_feature_importance(data_path: str):
    """
    Temporary function to fit preprocessor, extract features, and print correlation with target.
    """
    df = pd.read_csv(data_path)
    X = df.drop(columns=['lengthofstay'])
    y = df['lengthofstay']

    pipeline = build_preprocessor()
    X_transformed = pipeline.fit_transform(X, y)

    feature_names = get_feature_names(pipeline)

    transformed_df = pd.DataFrame(X_transformed, columns=feature_names)
    transformed_df['target_los'] = y.values

    correlations = transformed_df.corr()['target_los'].sort_values(ascending=False)
    print("\nFeature Correlation with Target (LengthOfStay):")
    print(correlations.drop('target_los'))

if __name__ == "__main__":
    evaluate_feature_importance("data/processed_data.csv")
