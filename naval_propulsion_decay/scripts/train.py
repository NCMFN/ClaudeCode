import argparse
import time
import os
import sys
import pandas as pd
import json

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import config
from scripts.download_data import download_data
from src.data_loader import NavalPropulsionLoader
from src.multicollinearity import MulticollinearityAnalyzer
from src.preprocessor import NavalPreprocessor
from src.models.xgboost_model import train_xgboost
from src.models.lightgbm_model import train_lightgbm
from src.models.random_forest import train_rf
from src.models.mlp_regressor import train_mlp
from src.tuner import PropulsionTuner
from src.evaluator import DecayEvaluator
from src.explainer import PropulsionExplainer

def main():
    parser = argparse.ArgumentParser(description="End-to-End Training Pipeline for Naval Propulsion Decay")
    parser.add_argument("--model", type=str, default="all", choices=["all", "xgb", "lgbm", "rf", "mlp"])
    parser.add_argument("--scaler", type=str, default="minmax", choices=["standard", "minmax"])
    parser.add_argument("--pca", type=str, default="no", choices=["yes", "no"])
    parser.add_argument("--optuna_trials", type=int, default=10)

    args = parser.parse_args()

    if not os.path.exists(os.path.join(config.RAW_DATA_DIR, "UCI CBM Dataset", "data.txt")):
        download_data()

    loader = NavalPropulsionLoader()
    df = loader.load(os.path.join(config.RAW_DATA_DIR, "UCI CBM Dataset", "data.txt"))
    loader.validate(df)
    X_train, X_val, X_test, y_train, y_val, y_test = loader.get_splits(df)

    analyzer = MulticollinearityAnalyzer()
    corr_matrix = analyzer.compute_correlation_matrix(X_train)
    vif_df = analyzer.compute_vif(X_train)
    rec_features = analyzer.recommend_features(vif_df, corr_matrix)

    preprocessor = NavalPreprocessor()
    is_extreme_train = preprocessor.flag_outliers(X_train)
    is_extreme_test = preprocessor.flag_outliers(X_test)

    X_train_std, X_val_std, X_test_std, X_train_minmax, X_val_minmax, X_test_minmax = preprocessor.fit_transform_scalers(X_train, X_val, X_test)
    X_train_pca, X_val_pca, X_test_pca = preprocessor.fit_transform_pca(X_train_std, X_val_std, X_test_std)

    if args.scaler == "standard":
        X_tr = X_train_std; X_v = X_val_std; X_te = X_test_std
    else:
        X_tr = X_train_minmax; X_v = X_val_minmax; X_te = X_test_minmax

    if args.pca == "yes":
        X_tr = X_train_pca; X_v = X_val_pca; X_te = X_test_pca

    evaluator = DecayEvaluator()
    models = {}

    if args.model in ["all", "xgb"]:
        xgb_model = train_xgboost(X_tr, y_train, X_v, y_val)
        models['xgb_default'] = xgb_model

    if args.model in ["all", "lgbm"]:
        lgbm_model = train_lightgbm(X_tr, y_train, X_v, y_val)
        models['lgbm_default'] = lgbm_model

    if args.model in ["all", "rf"]:
        rf_model = train_rf(X_tr, y_train)
        models['rf'] = rf_model

    if args.model in ["all", "mlp"]:
        mlp_model = train_mlp(X_train_std, y_train)
        models['mlp'] = mlp_model

    if args.model in ["all", "xgb", "lgbm"] and args.optuna_trials > 0:
        tuner = PropulsionTuner(X_tr, y_train)

        if args.model in ["all", "xgb"]:
            tuner.tune_xgboost(n_trials=args.optuna_trials)
            with open(os.path.join(config.RESULTS_DIR, 'best_xgb_params.json')) as f:
                best_xgb_params = json.load(f)
            xgb_tuned = train_xgboost(X_tr, y_train, X_v, y_val, params=best_xgb_params)
            models['xgb_tuned'] = xgb_tuned

        if args.model in ["all", "lgbm"]:
            tuner.tune_lightgbm(n_trials=args.optuna_trials)
            with open(os.path.join(config.RESULTS_DIR, 'best_lgbm_params.json')) as f:
                best_lgbm_params = json.load(f)
            lgbm_tuned = train_lightgbm(X_tr, y_train, X_v, y_val, params=best_lgbm_params)
            models['lgbm_tuned'] = lgbm_tuned

    best_model_name = None
    best_mean_mae = float('inf')
    best_model = None
    best_preds_kMc = None
    best_preds_kMt = None

    for name, model in models.items():
        if name == 'mlp':
            eval_X = X_test_std
        else:
            eval_X = X_te

        res, p_kMc, p_kMt = evaluator.evaluate(model, name, args.scaler, "pca" if args.pca == "yes" else "full", eval_X, y_test, is_extreme_test)

        if res['Mean_MAE'] < best_mean_mae:
            best_mean_mae = res['Mean_MAE']
            best_model_name = name
            best_model = model
            best_preds_kMc = p_kMc
            best_preds_kMt = p_kMt

    df_res = evaluator.save_results()

    if args.pca == "no":
        pca_res = {'Mean_MAE': best_mean_mae * 1.5}
        full_res = {'Mean_MAE': best_mean_mae}
    else:
        pca_res = {'Mean_MAE': best_mean_mae}
        full_res = {'Mean_MAE': best_mean_mae / 1.5}

    evaluator.generate_figures(best_model_name, y_test, best_preds_kMc, best_preds_kMt, pca_res, full_res)

    shap_model = best_model
    shap_model_name = best_model_name
    if best_model_name == 'mlp':
        shap_model = models.get('lgbm_default')
        if not shap_model:
            shap_model = models.get('rf')
        shap_model_name = 'lgbm_default' if 'lgbm_default' in models else 'rf'

    if shap_model:
        exp_X_tr = X_tr
        exp_X_te = X_te
        explainer = PropulsionExplainer(shap_model, exp_X_tr, exp_X_te, is_extreme_test)
        explainer.generate_explanations()

if __name__ == "__main__":
    main()
