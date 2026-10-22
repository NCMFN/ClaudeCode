import unittest
import pandas as pd
import yaml
import os
import sys

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from preprocessing import get_preprocessor, handle_imbalance
from features import engineer_features, select_features
from models import get_models

class TestPipeline(unittest.TestCase):
    def setUp(self):
        # Create a small dummy dataframe
        self.df = pd.DataFrame({
            'Type': ['M', 'L', 'L', 'M'],
            'Air temperature': [298.1, 298.2, 298.1, 298.2],
            'Process temperature': [308.6, 308.7, 308.5, 308.6],
            'Rotational speed': [1551, 1408, 1498, 1433],
            'Torque': [42.8, 46.3, 49.4, 39.5],
            'Tool wear': [0, 3, 5, 7],
            'Machine failure': [0, 1, 0, 0]
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

if __name__ == '__main__':
    unittest.main()
