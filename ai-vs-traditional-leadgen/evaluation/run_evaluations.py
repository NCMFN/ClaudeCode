import pandas as pd
import numpy as np
import os
import sys
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, roc_auc_score

# Add parent directory to path to import models
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from models.rule_based import predict_uci_bank, predict_kaggle_lead, predict_kaggle_b2b
from models.ml_models import get_models, get_preprocessor, train_and_predict

# Configuration
DATASETS = {
    'UCI_Bank': {
        'path': 'data/uci_bank.csv',
        'rule_func': predict_uci_bank,
        'target': 'y'
    },
    'Kaggle_Lead': {
        'path': 'data/kaggle_lead_scoring.csv',
        'rule_func': predict_kaggle_lead,
        'target': 'y'
    },
    'Kaggle_B2B_Clean': {
        'path': 'data/kaggle_b2b_clean.csv',
        'rule_func': predict_kaggle_b2b,
        'target': 'y'
    },
    'Kaggle_B2B_Noisy': {
        'path': 'data/kaggle_b2b_noisy.csv',
        'rule_func': predict_kaggle_b2b,
        'target': 'y'
    }
}

os.makedirs('evaluation', exist_ok=True)

def evaluate_model(y_true, y_pred, y_proba):
    """
    Computes standard ML classification metrics.
    Maps to Objective 1: Evaluating Technical Accuracy between ML and Rule-Based methods.
    """
    return {
        'Accuracy': accuracy_score(y_true, y_pred),
        'Precision': precision_score(y_true, y_pred, zero_division=0),
        'Recall': recall_score(y_true, y_pred, zero_division=0),
        'F1': f1_score(y_true, y_pred, zero_division=0),
        'ROC-AUC': roc_auc_score(y_true, y_proba)
    }

def run_pipeline():
    obj1_results = []
    obj2_results = []
    obj3_results = []
    obj4_results = []

    for name, config in DATASETS.items():
        print(f"Processing {name}...")
        df = pd.read_csv(config['path'])

        # We need to drop completely uninformative columns for ML models
        # Also drop the target from X
        target_col = config['target']
        if target_col not in df.columns:
            print(f"Target '{target_col}' not found in {name}. Skipping.")
            continue

        y = df[target_col]
        X = df.drop(columns=[target_col])
        if 'Converted' in X.columns:
            X = X.drop(columns=['Converted'])
        if 'Campaign_Response_Rate (%)' in X.columns:
            X = X.drop(columns=['Campaign_Response_Rate (%)'])

        # Pre-calculate overall conversion rate for Baseline
        overall_cr = y.mean()

        # Splitting
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, stratify=y, random_state=42)

        # 1. Rule-Based Baseline
        rule_test_df = X_test.copy()
        y_pred_rule = config['rule_func'](rule_test_df)

        # Rule metrics - maps to Objective 1
        rule_metrics = evaluate_model(y_test, y_pred_rule, y_pred_rule)

        obj1_results.append({
            'Dataset': name,
            'Model': 'Rule-Based',
            **rule_metrics
        })

        # Business metrics - maps to Objective 2 (Business Outcomes)
        rule_pos_idx = (y_pred_rule == 1)
        if rule_pos_idx.sum() > 0:
            cr_rule = y_test[rule_pos_idx].mean()
        else:
            cr_rule = 0

        lift_rule = (cr_rule - overall_cr) / overall_cr if overall_cr > 0 else 0

        obj2_results.append({
            'Dataset': name,
            'Model': 'Rule-Based',
            'Overall_CR': overall_cr,
            'Model_CR': cr_rule,
            'Relative_Lift_vs_Baseline': lift_rule,
            'Relative_Lift_vs_Rule': 0.0
        })

        # Efficiency metrics - maps to Objective 3 (Operational Efficiency)
        tpq_rule = 1.0 / rule_metrics['Precision'] if rule_metrics['Precision'] > 0 else np.nan
        obj3_results.append({
            'Dataset': name,
            'Model': 'Rule-Based',
            'Time_per_Qualified_Lead_Proxy': tpq_rule,
            'Inference_Time_per_1000_ms': 0
        })

        # 2. ML Models
        preprocessor = get_preprocessor(X_train)
        models = get_models()

        for model_name, model in models.items():
            y_pred, y_proba, _, inf_time_1000 = train_and_predict(X_train, y_train, X_test, model_name, model, preprocessor)

            ml_metrics = evaluate_model(y_test, y_pred, y_proba)

            obj1_results.append({
                'Dataset': name,
                'Model': model_name,
                **ml_metrics
            })

            ml_pos_idx = (y_pred == 1)
            if ml_pos_idx.sum() > 0:
                cr_ml = y_test[ml_pos_idx].mean()
            else:
                cr_ml = 0

            lift_ml = (cr_ml - overall_cr) / overall_cr if overall_cr > 0 else 0
            lift_ml_vs_rule = (cr_ml - cr_rule) / cr_rule if cr_rule > 0 else (cr_ml - cr_rule)

            obj2_results.append({
                'Dataset': name,
                'Model': model_name,
                'Overall_CR': overall_cr,
                'Model_CR': cr_ml,
                'Relative_Lift_vs_Baseline': lift_ml,
                'Relative_Lift_vs_Rule': lift_ml_vs_rule
            })

            tpq_ml = 1.0 / ml_metrics['Precision'] if ml_metrics['Precision'] > 0 else np.nan
            obj3_results.append({
                'Dataset': name,
                'Model': model_name,
                'Time_per_Qualified_Lead_Proxy': tpq_ml,
                'Inference_Time_per_1000_ms': inf_time_1000 * 1000 # to ms
            })

        # 3. Data Volume experiments - maps to Objective 4 (Contextual Factors)
        if name == 'Kaggle_B2B_Clean':
            for frac in [0.25, 0.50, 0.75, 1.0]:
                if frac == 1.0:
                    X_tr_frac, y_tr_frac = X_train, y_train
                else:
                    X_tr_frac, _, y_tr_frac, _ = train_test_split(X_train, y_train, train_size=frac, stratify=y_train, random_state=42)

                frac_preprocessor = get_preprocessor(X_tr_frac)
                y_pred, y_proba, _, _ = train_and_predict(X_tr_frac, y_tr_frac, X_test, 'XGBoost', models['XGBoost'], frac_preprocessor)

                metrics = evaluate_model(y_test, y_pred, y_proba)
                obj4_results.append({
                    'Dataset': name,
                    'Model': 'XGBoost',
                    'Training_Data_Fraction': frac,
                    'Accuracy': metrics['Accuracy'],
                    'F1': metrics['F1']
                })

    pd.DataFrame(obj1_results).to_csv('evaluation/objective1_metrics.csv', index=False)
    pd.DataFrame(obj2_results).to_csv('evaluation/objective2_business.csv', index=False)
    pd.DataFrame(obj3_results).to_csv('evaluation/objective3_efficiency.csv', index=False)
    pd.DataFrame(obj4_results).to_csv('evaluation/objective4_contextual.csv', index=False)

    print("Evaluations completed. CSVs generated in evaluation/")

if __name__ == '__main__':
    run_pipeline()
