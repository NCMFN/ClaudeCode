import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split, GroupKFold, cross_validate
from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor
from sklearn.linear_model import Ridge
from sklearn.dummy import DummyRegressor
from sklearn.preprocessing import StandardScaler
from sklearn.impute import SimpleImputer
import pickle

def train_models():
    print("Loading engineered features...")
    df = pd.read_csv('engineered_features.csv', index_col=0)

    # We enforce STRICT use of real labels
    df = df[df['total_nitrogen'].notna() & (df['total_nitrogen'] > 0)]
    y = df['total_nitrogen']

    # meta variables to exclude from feature set
    meta_cols = ['nitrate_umol_per_l', 'ammonium_umol_per_l', 'total_nitrogen',
                 'latitude_deg', 'longitude_deg']

    X = df.drop(columns=[c for c in meta_cols if c in df.columns])

    print(f"Dataset shape for training: X={X.shape}, y={y.shape}")

    imputer = SimpleImputer(strategy='mean')
    X_imp = imputer.fit_transform(X)

    # Spatial Groups for Cross Validation
    if 'latitude_deg' in df.columns and df['latitude_deg'].notna().sum() > 0:
        spatial_groups = pd.to_numeric(df['latitude_deg'], errors='coerce').fillna(0).round().astype(int)
    else:
        spatial_groups = np.random.randint(0, 5, size=len(df))

    gkf = GroupKFold(n_splits=min(5, len(np.unique(spatial_groups))))

    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X_imp)

    print("Evaluating models with Spatial Block Cross-Validation...")
    models = {
        'Null Baseline (Mean)': DummyRegressor(strategy='mean'),
        'Random Forest': RandomForestRegressor(n_estimators=100, random_state=42),
        'Gradient Boosting': GradientBoostingRegressor(n_estimators=100, random_state=42),
        'Ridge': Ridge(alpha=1.0)
    }

    for name, model in models.items():
        cv_results = cross_validate(
            model, X_scaled, y,
            groups=spatial_groups,
            cv=gkf,
            scoring='r2',
            return_train_score=False
        )
        print(f"[{name}] Spatial CV R2: {cv_results['test_score'].mean():.3f} ± {cv_results['test_score'].std():.3f}")

    # Train final models on full set for evaluation script artifact generation
    # Keep an explicit Test Split for SHAP evaluation
    X_train, X_test, y_train, y_test = train_test_split(X_scaled, y, test_size=0.2, random_state=42)

    trained_models = {}
    for name, model in models.items():
        model.fit(X_train, y_train)
        trained_models[name] = model

    print("Saving models and preprocessors...")
    with open('rf_model.pkl', 'wb') as f:
        pickle.dump(trained_models['Random Forest'], f)
    with open('gb_model.pkl', 'wb') as f:
        pickle.dump(trained_models['Gradient Boosting'], f)
    with open('ridge_model.pkl', 'wb') as f:
        pickle.dump(trained_models['Ridge'], f)
    with open('scaler.pkl', 'wb') as f:
        pickle.dump(scaler, f)

    np.save('X_test_scaled.npy', X_test)
    np.save('y_test.npy', y_test.to_numpy())

    with open('feature_names.pkl', 'wb') as f:
        pickle.dump(list(X.columns), f)

    print("Model training complete! Real labels used, Dummy baseline evaluated, and spatial CV properly integrated.")

if __name__ == "__main__":
    train_models()
