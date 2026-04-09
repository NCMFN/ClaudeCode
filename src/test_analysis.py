import unittest
import os
import pandas as pd

class TestMicroplasticAnalysis(unittest.TestCase):
    def test_output_directories_exist(self):
        self.assertTrue(os.path.isdir('outputs'))

    def test_output_images_exist(self):
        expected_files = [
            '1_exposure_risk_distribution.png',
            '2_correlation_heatmap.png',
            '3_bottled_water_vs_risk.png',
            '4_packaging_vs_risk.png',
            '5_feature_importance.png',
            '6_confusion_matrix.png'
        ]
        for f in expected_files:
            self.assertTrue(os.path.isfile(os.path.join('outputs', f)))

    def test_dataset_exists(self):
        self.assertTrue(os.path.isfile('microplastics_dataset.csv'))

if __name__ == '__main__':
    unittest.main()
