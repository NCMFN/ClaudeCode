import pandas as pd
import numpy as np
from sklearn.linear_model import LogisticRegression
from sklearn.svm import SVC
from sklearn.model_selection import GridSearchCV
from sklearn.pipeline import Pipeline
from statsmodels.stats.outliers_influence import variance_inflation_factor

def train_logistic_regression(X_train, y_train, preprocessor):
    """
    Trains a Multinomial L2-regularized Logistic Regression model.
    """
    lr_pipeline = Pipeline(steps=[
        ('preprocessor', preprocessor),
        ('classifier', LogisticRegression(
            penalty='l2', solver='lbfgs', max_iter=1000, random_state=42
        ))
    ])

    # We can tune C (inverse of regularization strength)
    param_grid = {
        'classifier__C': [0.1, 1.0, 10.0]
    }

    grid_search = GridSearchCV(
        lr_pipeline, param_grid, cv=5, scoring='f1_macro', n_jobs=-1
    )

    grid_search.fit(X_train, y_train)
    return grid_search.best_estimator_

def train_svm_linear(X_train, y_train, preprocessor):
    """
    Trains a Linear SVM model.
    """
    svm_pipeline = Pipeline(steps=[
        ('preprocessor', preprocessor),
        ('classifier', SVC(kernel='linear', probability=True, random_state=42))
    ])

    param_grid = {
        'classifier__C': [0.1, 1.0, 10.0]
    }

    grid_search = GridSearchCV(
        svm_pipeline, param_grid, cv=5, scoring='f1_macro', n_jobs=-1
    )

    grid_search.fit(X_train, y_train)
    return grid_search.best_estimator_

def train_svm_rbf(X_train, y_train, preprocessor):
    """
    Trains an RBF SVM model.
    """
    svm_pipeline = Pipeline(steps=[
        ('preprocessor', preprocessor),
        ('classifier', SVC(kernel='rbf', probability=True, random_state=42))
    ])

    param_grid = {
        'classifier__C': [0.1, 1.0, 10.0],
        'classifier__gamma': ['scale', 'auto', 0.1, 1.0]
    }

    grid_search = GridSearchCV(
        svm_pipeline, param_grid, cv=5, scoring='f1_macro', n_jobs=-1
    )

    grid_search.fit(X_train, y_train)
    return grid_search.best_estimator_

def check_multicollinearity(X, preprocessor):
    """
    Computes VIF for features after preprocessing to verify R-L multicollinearity.
    """
    # Create a dense array after imputation/scaling
    X_processed = preprocessor.fit_transform(X)
    vif_data = pd.DataFrame()
    vif_data["feature"] = preprocessor.get_feature_names_out()
    vif_data["VIF"] = [variance_inflation_factor(X_processed, i)
                       for i in range(X_processed.shape[1])]
    return vif_data
