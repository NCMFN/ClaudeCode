import pandas as pd
import numpy as np
import os
import matplotlib.pyplot as plt
import seaborn as plt_sns
from sklearn.model_selection import TimeSeriesSplit, GridSearchCV
from sklearn.tree import DecisionTreeRegressor
from sklearn.ensemble import RandomForestRegressor
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
import pickle
import time
import json

def train_and_evaluate():
    os.makedirs('uk-rail-pricing/outputs/figures', exist_ok=True)
    os.makedirs('uk-rail-pricing/outputs/tables', exist_ok=True)
    os.makedirs('uk-rail-pricing/outputs/models', exist_ok=True)
    plt.rcParams.update({'font.size': 11, 'axes.titlesize': 13, 'axes.labelsize': 11, 'xtick.labelsize': 10, 'ytick.labelsize': 10, 'figure.dpi': 300, 'savefig.dpi': 300})

    # Load processed features
    df = pd.read_csv('uk-rail-pricing/data/processed/features_full.csv')

    # Sort chronologically for TimeSeriesSplit
    df['transaction_datetime'] = pd.to_datetime(df['transaction_datetime'])
    df = df.sort_values('transaction_datetime').reset_index(drop=True)

    # Define features and target
    drop_cols = ['Transaction_ID', 'Date_of_Purchase', 'Time_of_Purchase', 'Payment_Method',
                 'Departure_Station', 'Arrival_Destination', 'Date_of_Journey', 'Departure_Time',
                 'Arrival_Time', 'Actual_Arrival_Time', 'Journey_Status', 'Refund_Request',
                 'Purchase_Type', 'transaction_datetime', 'journey_datetime', 'price_gbp',
                 'dep_match', 'arr_match', 'Price', 'actual_delay_mins', 'is_delayed']

    features = [c for c in df.columns if c not in drop_cols]

    X = df[features]
    y = df['price_gbp']

    # 4a. Temporal Cross-Validation Split
    tscv = TimeSeriesSplit(n_splits=4)
    folds = list(tscv.split(X))
    with open('uk-rail-pricing/data/processed/cv_folds.pkl', 'wb') as f:
        pickle.dump(folds, f)

    # 4b & 4c. Model Training and Baselines
    models = {
        'Decision Tree (Baseline)': DecisionTreeRegressor(criterion='squared_error', max_depth=None, random_state=42),
        'Linear Regression': LinearRegression(),
        'Random Forest (100 trees)': RandomForestRegressor(n_estimators=100, random_state=42, n_jobs=-1)
    }

    results = []

    for name, model in models.items():
        print(f"Training {name}...")
        start_time = time.time()

        fold_maes, fold_rmses, fold_r2s = [], [], []
        for train_idx, test_idx in folds:
            X_train, X_test = X.iloc[train_idx], X.iloc[test_idx]
            y_train, y_test = y.iloc[train_idx], y.iloc[test_idx]

            # Handle NaNs
            X_train = X_train.fillna(0)
            X_test = X_test.fillna(0)

            model.fit(X_train, y_train)
            preds = model.predict(X_test)

            fold_maes.append(mean_absolute_error(y_test, preds))
            fold_rmses.append(np.sqrt(mean_squared_error(y_test, preds)))
            fold_r2s.append(r2_score(y_test, preds))

        train_time = time.time() - start_time

        results.append({
            'Model': name,
            'MAE': np.mean(fold_maes),
            'RMSE': np.mean(fold_rmses),
            'R²': np.mean(fold_r2s),
            'Train Time': train_time
        })

    # 4d. Hyperparameter Tuning for Decision Tree
    print("Tuning Decision Tree...")
    param_grid = {
        'max_depth': [3, 5, 8, 12, 20],
        'min_samples_split': [2, 10, 50, 100]
    }
    dt = DecisionTreeRegressor(criterion='squared_error', random_state=42)
    grid_search = GridSearchCV(dt, param_grid, cv=tscv, scoring='r2', n_jobs=-1)

    X_filled = X.fillna(0)
    start_time = time.time()
    grid_search.fit(X_filled, y)
    tune_time = time.time() - start_time

    best_dt = grid_search.best_estimator_
    with open('uk-rail-pricing/outputs/models/dt_regressor.pkl', 'wb') as f:
        pickle.dump(best_dt, f)

    with open('uk-rail-pricing/outputs/tables/best_hyperparams.json', 'w') as f:
        json.dump(grid_search.best_params_, f)

    results.append({
        'Model': 'Decision Tree (Tuned)',
        'MAE': mean_absolute_error(y, best_dt.predict(X_filled)),
        'RMSE': np.sqrt(mean_squared_error(y, best_dt.predict(X_filled))),
        'R²': r2_score(y, best_dt.predict(X_filled)),
        'Train Time': tune_time
    })

    results_df = pd.DataFrame(results)
    results_df.to_csv('uk-rail-pricing/outputs/tables/model_comparison_metrics.csv', index=False)
    print("Table 1 generated.")

    # Use best tuned DT for test predictions on the last fold for plotting
    train_idx, test_idx = folds[-1]
    X_train, X_test = X_filled.iloc[train_idx], X_filled.iloc[test_idx]
    y_train, y_test = y.iloc[train_idx], y.iloc[test_idx]

    best_dt.fit(X_train, y_train)
    y_pred = best_dt.predict(X_test)

    # Figure 9: Actual vs Predicted price scatter
    plt.figure(figsize=(8, 6))
    plt_sns.scatterplot(x=y_test, y=y_pred, alpha=0.5)
    plt.plot([y_test.min(), y_test.max()], [y_test.min(), y_test.max()], 'r--')
    r2_val = r2_score(y_test, y_pred)
    plt.text(0.05, 0.95, f'R² = {r2_val:.3f}', transform=plt.gca().transAxes, fontsize=12, verticalalignment='top')
    plt.title('Figure 9: Actual vs Predicted Price\nSource: 2024 National Rail Ticket Data (Maven Analytics).')
    plt.xlabel('Actual Price (GBP)')
    plt.ylabel('Predicted Price (GBP)')
    plt.tight_layout()
    plt.savefig('uk-rail-pricing/outputs/figures/Figure_9.png')
    plt.close()

    # Figure 10: Residual distribution histogram
    residuals = y_test - y_pred
    plt.figure(figsize=(8, 6))
    plt_sns.histplot(residuals, bins=50, kde=True)
    plt.title('Figure 10: Residual Distribution\nSource: 2024 National Rail Ticket Data (Maven Analytics).')
    plt.xlabel('Residual (Actual - Predicted) GBP')
    plt.tight_layout()
    plt.savefig('uk-rail-pricing/outputs/figures/Figure_10.png')
    plt.close()

    # Figure 11: Learning Curve
    from sklearn.model_selection import learning_curve
    train_sizes, train_scores, test_scores = learning_curve(best_dt, X_filled, y, cv=tscv, scoring='neg_root_mean_squared_error', n_jobs=-1, train_sizes=np.linspace(0.1, 1.0, 5))
    train_mean = -np.mean(train_scores, axis=1)
    test_mean = -np.mean(test_scores, axis=1)

    plt.figure(figsize=(8, 6))
    plt.plot(train_sizes, train_mean, label='Training RMSE')
    plt.plot(train_sizes, test_mean, label='Cross-Validation RMSE')
    plt.title('Figure 11: Learning Curve\nSource: 2024 National Rail Ticket Data (Maven Analytics).')
    plt.xlabel('Training Examples')
    plt.ylabel('RMSE')
    plt.legend(loc='best')
    plt.tight_layout()
    plt.savefig('uk-rail-pricing/outputs/figures/Figure_11.png')
    plt.close()

    # Figure 12: Heatmap of R² scores across hyperparameter grid
    scores_matrix = grid_search.cv_results_['mean_test_score'].reshape(len(param_grid['max_depth']), len(param_grid['min_samples_split']))
    plt.figure(figsize=(8, 6))
    plt_sns.heatmap(scores_matrix, annot=True, xticklabels=param_grid['min_samples_split'], yticklabels=param_grid['max_depth'], cmap='viridis')
    plt.title('Figure 12: Grid Search R² Heatmap\nSource: 2024 National Rail Ticket Data (Maven Analytics).')
    plt.xlabel('min_samples_split')
    plt.ylabel('max_depth')
    plt.tight_layout()
    plt.savefig('uk-rail-pricing/outputs/figures/Figure_12.png')
    plt.close()

    # Feature Importance (Step 5)
    importances = best_dt.feature_importances_
    feat_imp_df = pd.DataFrame({'Feature': X.columns, 'Importance Score': importances})
    feat_imp_df = feat_imp_df.sort_values('Importance Score', ascending=False).reset_index(drop=True)
    feat_imp_df['Rank'] = feat_imp_df.index + 1
    feat_imp_df.to_csv('uk-rail-pricing/outputs/tables/feature_importances.csv', index=False)

    # Figure 13: Horizontal bar chart of top 20 features
    plt.figure(figsize=(10, 8))
    plt_sns.barplot(data=feat_imp_df.head(20), x='Importance Score', y='Feature')
    plt.title('Figure 13: Top 20 Features by Importance\nSource: 2024 National Rail Ticket Data (Maven Analytics).')
    plt.tight_layout()
    plt.savefig('uk-rail-pricing/outputs/figures/Figure_13.png')
    plt.close()

    # Figure 14: Partial dependence plots for top 3 features
    top_3_features = feat_imp_df['Feature'].head(3).tolist()
    from sklearn.inspection import PartialDependenceDisplay
    fig, ax = plt.subplots(figsize=(12, 4))
    PartialDependenceDisplay.from_estimator(best_dt, X_filled, top_3_features, ax=ax)
    fig.suptitle('Figure 14: Partial Dependence Plots for Top 3 Features\nSource: 2024 National Rail Ticket Data (Maven Analytics).')
    plt.tight_layout()
    plt.savefig('uk-rail-pricing/outputs/figures/Figure_14.png')
    plt.close()

    # Save a full predicted vs actual dataset for downstream scripts
    df['predicted_price'] = best_dt.predict(X_filled)
    df.to_csv('uk-rail-pricing/data/processed/predictions_full.csv', index=False)

if __name__ == "__main__":
    train_and_evaluate()
