import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import os
import json
import joblib
from sklearn.model_selection import TimeSeriesSplit, GridSearchCV
from sklearn.tree import DecisionTreeRegressor
from sklearn.linear_model import LinearRegression
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
from sklearn.inspection import PartialDependenceDisplay
import time

STYLE = {
    'primary': '#2E5EAA',
    'secondary': '#D9534F'
}

def train_models():
    os.makedirs('outputs/models', exist_ok=True)
    os.makedirs('outputs/tables', exist_ok=True)
    os.makedirs('outputs/figures', exist_ok=True)

    df = pd.read_csv('data/processed/features_full.csv')
    df['transaction_datetime'] = pd.to_datetime(df['transaction_datetime'])
    df = df.sort_values(by='transaction_datetime').reset_index(drop=True)

    # 4a. Temporal Cross-Validation Split
    drop_cols = [c for c in df.columns if c.endswith('_raw') or c in [
        'Transaction ID', 'Date of Purchase', 'Time of Purchase', 'Purchase Type', 'Payment Method',
        'Departure Station', 'Arrival Destination', 'Date of Journey', 'Departure Time',
        'Arrival Time', 'Actual Arrival Time', 'Journey Status', 'Refund Request',
        'transaction_datetime', 'journey_datetime', 'Arrival Time DT', 'Actual Arrival DT',
        'Departure_Mapped', 'Arrival_Mapped', 'price_gbp', 'Price'
    ]]

    X = df.drop(columns=drop_cols)
    X = X.select_dtypes(include=[np.number])
    X = X.fillna(X.median()) # Impute any NaNs in X
    y = df['price_gbp']
    y = y.fillna(y.median())

    tscv = TimeSeriesSplit(n_splits=4)
    cv_folds = list(tscv.split(X))

    import pickle
    with open('data/processed/cv_folds.pkl', 'wb') as f:
        pickle.dump(cv_folds, f)

    # 4b. Decision Tree Regressor
    dt_depths = [3, 5, 8, 12, 20]
    dt_splits = [2, 10, 50, 100]

    param_grid = {
        'max_depth': dt_depths,
        'min_samples_split': dt_splits
    }

    grid = GridSearchCV(DecisionTreeRegressor(criterion='squared_error', random_state=42), param_grid, cv=tscv, scoring='neg_mean_squared_error', n_jobs=-1)
    grid.fit(X, y)

    with open('outputs/tables/best_hyperparams.json', 'w') as f:
        json.dump(grid.best_params_, f)

    grid_r2 = GridSearchCV(DecisionTreeRegressor(criterion='squared_error', random_state=42), param_grid, cv=tscv, scoring='r2', n_jobs=-1)
    grid_r2.fit(X, y)

    results = pd.DataFrame(grid_r2.cv_results_)
    pivot_r2 = results.pivot(index='param_max_depth', columns='param_min_samples_split', values='mean_test_score')

    plt.figure(figsize=(8, 6))
    sns.heatmap(pivot_r2.astype(float), annot=True, cmap='viridis')
    plt.title('Figure 36: GridSearchCV R² heatmap. Source: 2024 National Rail Ticket Data (Maven Analytics).', wrap=True)
    plt.xlabel('min_samples_split')
    plt.ylabel('max_depth')
    plt.tight_layout()
    plt.savefig('outputs/figures/figure_36.png', dpi=300)
    plt.close()

    train_idx, test_idx = cv_folds[-1]
    X_train, X_test = X.iloc[train_idx], X.iloc[test_idx]
    y_train, y_test = y.iloc[train_idx], y.iloc[test_idx]

    best_dt = grid.best_estimator_
    best_dt.fit(X_train, y_train)
    joblib.dump(best_dt, 'outputs/models/dt_regressor.pkl')

    y_pred_dt = best_dt.predict(X_test)
    dt_r2 = r2_score(y_test, y_pred_dt)

    df.loc[test_idx, 'predicted_price_dt'] = y_pred_dt
    df.loc[test_idx, 'residual_dt'] = y_test - y_pred_dt
    df.to_csv('data/processed/features_full_with_preds.csv', index=False)

    plt.figure(figsize=(8, 6))
    plt.scatter(y_test, y_pred_dt, alpha=0.3, color=STYLE['primary'])
    plt.plot([0, y_test.max()], [0, y_test.max()], color='red', linestyle='--')
    plt.title(f'Figure 25: Actual vs Predicted price, Decision Tree (test fold). R²={dt_r2:.2f}. Source: 2024 National Rail Ticket Data (Maven Analytics).', wrap=True)
    plt.xlabel('Actual Price (GBP)')
    plt.ylabel('Predicted Price (GBP)')
    plt.tight_layout()
    plt.savefig('outputs/figures/figure_25.png', dpi=300)
    plt.close()

    residuals = y_test - y_pred_dt
    plt.figure(figsize=(10, 6))
    sns.histplot(residuals, bins=50, color=STYLE['secondary'])
    plt.title('Figure 26: Residual distribution histogram, Decision Tree. Source: 2024 National Rail Ticket Data (Maven Analytics).', wrap=True)
    plt.xlabel('Residual (Actual - Predicted)')
    plt.tight_layout()
    plt.savefig('outputs/figures/figure_26.png', dpi=300)
    plt.close()

    from sklearn.model_selection import learning_curve
    train_sizes, train_scores, test_scores = learning_curve(best_dt, X, y, cv=tscv, scoring='neg_root_mean_squared_error', train_sizes=np.linspace(0.1, 1.0, 5), n_jobs=-1)
    plt.figure(figsize=(10, 6))
    plt.plot(train_sizes, -train_scores.mean(axis=1), 'o-', color='blue', label='Training Error')
    plt.plot(train_sizes, -test_scores.mean(axis=1), 'o-', color='orange', label='Validation Error')
    plt.title('Figure 27: Learning curve, Decision Tree. Source: 2024 National Rail Ticket Data (Maven Analytics).', wrap=True)
    plt.xlabel('Training Size')
    plt.ylabel('RMSE')
    plt.legend()
    plt.tight_layout()
    plt.savefig('outputs/figures/figure_27.png', dpi=300)
    plt.close()

    results['rmse'] = np.sqrt(np.abs(results['mean_test_score'])) # Use abs to handle neg MSE

    plt.figure(figsize=(8, 6))
    sns.lineplot(data=results, x='param_max_depth', y='rmse', hue='param_min_samples_split', marker='o')
    plt.title('Figure 28: RMSE vs max_depth line chart. Source: 2024 National Rail Ticket Data (Maven Analytics).', wrap=True)
    plt.tight_layout()
    plt.savefig('outputs/figures/figure_28.png', dpi=300)
    plt.close()

    plt.figure(figsize=(8, 6))
    sns.lineplot(data=results, x='param_min_samples_split', y='rmse', hue='param_max_depth', marker='o')
    plt.title('Figure 29: RMSE vs min_samples_split line chart. Source: 2024 National Rail Ticket Data (Maven Analytics).', wrap=True)
    plt.tight_layout()
    plt.savefig('outputs/figures/figure_29.png', dpi=300)
    plt.close()

    models = {
        'Decision Tree': best_dt,
        'Linear Regression': LinearRegression(),
        'Random Forest': RandomForestRegressor(n_estimators=100, random_state=42, n_jobs=-1)
    }

    metrics = []

    for name, model in models.items():
        start_time = time.time()
        model.fit(X_train, y_train)
        train_time = time.time() - start_time

        y_pred = model.predict(X_test)

        if name == 'Linear Regression':
            plt.figure(figsize=(8, 6))
            plt.scatter(y_test, y_pred, alpha=0.3, color=STYLE['primary'])
            plt.plot([0, y_test.max()], [0, y_test.max()], color='red', linestyle='--')
            plt.title(f'Figure 30: Actual vs Predicted, Linear Regression baseline. Source: 2024 National Rail Ticket Data (Maven Analytics).', wrap=True)
            plt.tight_layout()
            plt.savefig('outputs/figures/figure_30.png', dpi=300)
            plt.close()
        elif name == 'Random Forest':
            rf_model = model
            plt.figure(figsize=(8, 6))
            plt.scatter(y_test, y_pred, alpha=0.3, color=STYLE['primary'])
            plt.plot([0, y_test.max()], [0, y_test.max()], color='red', linestyle='--')
            plt.title(f'Figure 31: Actual vs Predicted, Random Forest baseline. Source: 2024 National Rail Ticket Data (Maven Analytics).', wrap=True)
            plt.tight_layout()
            plt.savefig('outputs/figures/figure_31.png', dpi=300)
            plt.close()

        metrics.append({
            'Model': name,
            'MAE': mean_absolute_error(y_test, y_pred),
            'RMSE': np.sqrt(mean_squared_error(y_test, y_pred)),
            'R²': r2_score(y_test, y_pred),
            'Train Time': train_time
        })

    metrics_df = pd.DataFrame(metrics)
    metrics_df.to_csv('outputs/tables/model_comparison_metrics.csv', index=False)

    plt.figure(figsize=(8, 6))
    sns.barplot(data=metrics_df, x='Model', y='MAE', color=STYLE['primary'])
    plt.title('Figure 32: MAE comparison across 3 models (bar). Source: 2024 National Rail Ticket Data (Maven Analytics).', wrap=True)
    plt.tight_layout()
    plt.savefig('outputs/figures/figure_32.png', dpi=300)
    plt.close()

    plt.figure(figsize=(8, 6))
    sns.barplot(data=metrics_df, x='Model', y='RMSE', color=STYLE['primary'])
    plt.title('Figure 33: RMSE comparison across 3 models (bar). Source: 2024 National Rail Ticket Data (Maven Analytics).', wrap=True)
    plt.tight_layout()
    plt.savefig('outputs/figures/figure_33.png', dpi=300)
    plt.close()

    plt.figure(figsize=(8, 6))
    sns.barplot(data=metrics_df, x='Model', y='R²', color=STYLE['primary'])
    plt.title('Figure 34: R² comparison across 3 models (bar). Source: 2024 National Rail Ticket Data (Maven Analytics).', wrap=True)
    plt.tight_layout()
    plt.savefig('outputs/figures/figure_34.png', dpi=300)
    plt.close()

    plt.figure(figsize=(8, 6))
    sns.barplot(data=metrics_df, x='Model', y='Train Time', color=STYLE['primary'])
    plt.title('Figure 35: Training time comparison (bar). Source: 2024 National Rail Ticket Data (Maven Analytics).', wrap=True)
    plt.tight_layout()
    plt.savefig('outputs/figures/figure_35.png', dpi=300)
    plt.close()

    dt_importances = pd.DataFrame({
        'Feature': X.columns,
        'Importance Score': best_dt.feature_importances_
    }).sort_values(by='Importance Score', ascending=False)
    dt_importances['Rank'] = np.arange(1, len(dt_importances) + 1)

    dt_importances.to_csv('outputs/tables/feature_importances.csv', index=False)

    plt.figure(figsize=(10, 8))
    sns.barplot(data=dt_importances.head(20), x='Importance Score', y='Feature', color=STYLE['primary'])
    plt.title('Figure 37: Top 20 feature importances, Decision Tree (bar). Source: 2024 National Rail Ticket Data (Maven Analytics).', wrap=True)
    plt.tight_layout()
    plt.savefig('outputs/figures/figure_37.png', dpi=300)
    plt.close()

    rf_importances = pd.DataFrame({
        'Feature': X.columns,
        'Importance Score': rf_model.feature_importances_
    }).sort_values(by='Importance Score', ascending=False)

    plt.figure(figsize=(10, 8))
    sns.barplot(data=rf_importances.head(20), x='Importance Score', y='Feature', color=STYLE['secondary'])
    plt.title('Figure 38: Top 20 feature importances, Random Forest (bar). Source: 2024 National Rail Ticket Data (Maven Analytics).', wrap=True)
    plt.tight_layout()
    plt.savefig('outputs/figures/figure_38.png', dpi=300)
    plt.close()

    top_3_features = dt_importances['Feature'].head(3).tolist()

    fig, ax = plt.subplots(figsize=(15, 5))
    PartialDependenceDisplay.from_estimator(best_dt, X_train, top_3_features, ax=ax)
    plt.suptitle('Figure 39: Partial dependence plots, top 3 features. Source: 2024 National Rail Ticket Data (Maven Analytics).')
    plt.tight_layout()
    plt.savefig('outputs/figures/figure_39.png', dpi=300)
    plt.close()

    print("Model training and evaluation complete.")

if __name__ == '__main__':
    train_models()
