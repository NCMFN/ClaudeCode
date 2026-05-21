"""Configuration parameters, file paths, and constants."""
import os

# Base Directories
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(BASE_DIR, 'data')
RAW_DATA_DIR = os.path.join(DATA_DIR, 'raw')
PROCESSED_DATA_DIR = os.path.join(DATA_DIR, 'processed')
OUTPUTS_DIR = os.path.join(BASE_DIR, 'outputs')
MODELS_DIR = os.path.join(OUTPUTS_DIR, 'models')
PLOTS_DIR = os.path.join(OUTPUTS_DIR, 'plots')

# Create necessary directories
for d in [PROCESSED_DATA_DIR, MODELS_DIR, PLOTS_DIR]:
    os.makedirs(d, exist_ok=True)

# Datasets
DATASETS = {
    'smart_ag': os.path.join(RAW_DATA_DIR, 'cropdata_updated.csv'),
    'smart_farming': os.path.join(RAW_DATA_DIR, 'Smart_Farming_Crop_Yield_2024.csv'),
    'hydroponics': os.path.join(RAW_DATA_DIR, 'feeds.csv'),
    'soil_ph': os.path.join(RAW_DATA_DIR, 'dataset_soilph_soilmoisture_temperature.xlsx'),
    'crop_rec': os.path.join(RAW_DATA_DIR, 'Crop_recommendation.csv')
}

# Unified Dataset Path
UNIFIED_DATA_PATH = os.path.join(PROCESSED_DATA_DIR, 'unified_data.csv')
FEATURE_DATA_PATH = os.path.join(PROCESSED_DATA_DIR, 'feature_data.csv')

# Result Paths
RESULTS_SUMMARY_PATH = os.path.join(OUTPUTS_DIR, 'results_summary.csv')

# Model Parameters
RANDOM_STATE = 42
CV_FOLDS = 5
SMOOTHING_WINDOW = 5
