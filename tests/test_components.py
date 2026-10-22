import unittest
import pandas as pd
import yaml
import os
import sys
import numpy as np
import tempfile
from unittest.mock import patch
from sklearn.ensemble import RandomForestClassifier
from sklearn.inspection import permutation_importance
import shap

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from preprocessing import get_preprocessor, handle_imbalance
from features import engineer_features, select_features
from models import get_models
from evaluate import compute_bootstrap_auc_ci, evaluate_models

class TestPipeline(unittest.TestCase):
    def setUp(self):
        # Create a small dummy dataframe with enough rows for SMOTE
        self.df = pd.DataFrame({
            'Type': ['M', 'L', 'L', 'M'] * 15,
            'Air temperature': [298.1, 298.2, 298.1, 298.2] * 15,
            'Process temperature': [308.6, 308.7, 308.5, 308.6] * 15,
            'Rotational speed': [1551, 1408, 1498, 1433] * 15,
            'Torque': [42.8, 46.3, 49.4, 39.5] * 15,
            'Tool wear': [0, 3, 5, 7] * 15,
            'Machine failure': [0, 1, 0, 0] * 15
        })

    def test_features(self):
        df_feat = engineer_features(self.df)
        self.assertIn('Thermal_delta', df_feat.columns)
        self.assertIn('Mechanical_power', df_feat.columns)

        X, y = select_features(df_feat)
        self.assertEqual(len(X.columns), 8)
        self.assertEqual(y.name, 'Machine failure')

    def test_models(self):
        models = get_models('config.yaml')
        self.assertIn('Logistic Regression', models)
        self.assertIn('Random Forest', models)
        self.assertIn('AdaBoost', models)

    def test_preprocessor(self):
        df_feat = engineer_features(self.df)
        X, y = select_features(df_feat)
        preprocessor = get_preprocessor()
        X_proc = preprocessor.fit_transform(X)
        self.assertGreater(X_proc.shape[1], 0)

    def test_bootstrap_auc_ci(self):
        y_true = [0, 0, 1, 1, 0, 1, 0, 0, 1, 1]
        y_prob_best = [0.1, 0.2, 0.8, 0.9, 0.3, 0.7, 0.1, 0.2, 0.6, 0.85]
        y_prob_comp = [0.4, 0.4, 0.6, 0.6, 0.5, 0.5, 0.4, 0.4, 0.6, 0.6]

        mean_diff, ci_lower, ci_upper = compute_bootstrap_auc_ci(y_true, y_prob_best, y_prob_comp, n_bootstrap=100)

        self.assertIsInstance(mean_diff, float)
        self.assertIsInstance(ci_lower, float)
        self.assertIsInstance(ci_upper, float)
        self.assertLessEqual(ci_lower, mean_diff)
        self.assertLessEqual(mean_diff, ci_upper)

    def test_shap_permutation(self):
        df_feat = engineer_features(self.df)
        X, y = select_features(df_feat)
        preprocessor = get_preprocessor()
        X_proc = preprocessor.fit_transform(X)
        X_res, y_res = handle_imbalance(X_proc, y, strategy='smote', random_seed=42)

        # Fit dummy model
        model = RandomForestClassifier(n_estimators=10, random_state=42)
        model.fit(X_res, y_res)

        # Test permutation importance
        perm_importance = permutation_importance(model, X_res, y_res, n_repeats=2, random_state=42)
        self.assertEqual(len(perm_importance.importances_mean), X_res.shape[1])
        self.assertFalse(np.isnan(perm_importance.importances_mean).any())

        # Test SHAP branch (available)
        explainer = shap.TreeExplainer(model)
        X_res_df = pd.DataFrame(X_res)
        shap_values = explainer.shap_values(X_res_df)

        if isinstance(shap_values, list):
            shap_values_to_check = shap_values[1]
        else:
            shap_values_to_check = shap_values

        self.assertTrue(shap_values_to_check.shape == (X_res.shape[0], X_res.shape[1]) or shap_values_to_check.shape == (X_res.shape[0], X_res.shape[1], 2))

        # Test SHAP branch (unavailable) using evaluate_models
        with patch('evaluate.shap_available', False):
            with tempfile.TemporaryDirectory() as tmpdirname:
                # create a test config
                test_config_path = os.path.join(tmpdirname, 'test_config.yaml')
                with open(test_config_path, 'w') as f:
                    yaml.dump({
                        'random_seed': 42,
                        'cv_folds': 2,
                        'imbalance_strategy': 'smote',
                        'output_paths': {
                            'report_md': os.path.join(tmpdirname, 'final_report.md'),
                            'metrics_summary': os.path.join(tmpdirname, 'metrics_summary.csv'),
                            'roc_curves': os.path.join(tmpdirname, 'roc_curves.png'),
                            'confusion_matrices': os.path.join(tmpdirname, 'confusion_matrices.png'),
                            'feature_importance': os.path.join(tmpdirname, 'feature_importance.png'),
                            'run1_metrics': os.path.join(tmpdirname, 'run1_metrics.json'),
                            'run2_metrics': os.path.join(tmpdirname, 'run2_metrics.json'),
                            'significance_tests': os.path.join(tmpdirname, 'significance_tests.csv'),
                            'bootstrap_auc_ci': os.path.join(tmpdirname, 'bootstrap_auc_ci.csv'),
                            'shap_summary': os.path.join(tmpdirname, 'shap_summary.png')
                        },
                        'models': {
                            'random_forest': {
                                'n_estimators': 2,
                                'max_depth': 2
                            }
                        }
                    }, f)

                # Call evaluate_models
                evaluate_models(X, y, config_path=test_config_path, run_id=1)

                # Check that shap_summary.png does NOT exist
                self.assertFalse(os.path.exists(os.path.join(tmpdirname, 'shap_summary.png')))

if __name__ == '__main__':
    unittest.main()
