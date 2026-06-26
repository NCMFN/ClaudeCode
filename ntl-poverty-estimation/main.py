import subprocess
import os
import sys
import logging
from datetime import datetime

# Set up strict logging
os.makedirs("results/logs", exist_ok=True)
log_file = os.path.join("results/logs", f"pipeline_run_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log")
logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(levelname)s - %(message)s',
                    handlers=[logging.FileHandler(log_file), logging.StreamHandler(sys.stdout)])
logger = logging.getLogger(__name__)

def run_script(script_path: str):
    logger.info(f"--- Starting {script_path} ---")
    try:
        env = os.environ.copy()
        env['PYTHONPATH'] = os.path.abspath('.')

        result = subprocess.run([sys.executable, script_path],
                                env=env,
                                check=True,
                                capture_output=True,
                                text=True)

        for line in result.stdout.splitlines():
            logger.info(line)
        logger.info(f"--- Completed {script_path} ---")

    except subprocess.CalledProcessError as e:
        logger.error(f"--- FAILED {script_path} ---")
        logger.error(f"Exit code: {e.returncode}")
        for line in e.stdout.splitlines():
            logger.error(f"STDOUT: {line}")
        for line in e.stderr.splitlines():
            logger.error(f"STDERR: {line}")
        sys.exit(1)

def main():
    logger.info("Initializing NTL Poverty Estimation Pipeline...")

    wrapper_path = "pipeline_runner.py"

    wrapper_code = """
import os
import sys
import logging

from src.dhs_loader import load_dhs_data
from src.ntl_utils import download_ntl_data, hdf_to_geotiff, create_annual_median
from src.feature_extraction import extract_features
from src.model_pipeline import train_and_evaluate
from src.poverty_mapper import generate_poverty_heatmap
from src.multimodal_fusion import fetch_ndvi_data, append_ndvi_stats
import geopandas as gpd

print("Starting Pipeline execution...")

# 1. DHS Data
print("Phase 1: Loading DHS data...")
hr_path = "data/raw/dhs/XXHR7DFL.DTA"
ge_path = "data/raw/dhs/XXGE7AFL.shp"
wealth_df, dhs_geo = load_dhs_data(hr_path, ge_path)

# 2. NTL Data Download & Processing
print("Phase 2: NTL Data Processing...")
# Note: For testing without real data, we still call the function to trigger the fallbacks
create_annual_median("data/processed/ntl_rasters", "data/processed/ntl_annual_median.tif")

# 3. Feature Extraction
print("Phase 3: Feature Extraction...")
feature_matrix_path = "data/processed/feature_matrix.csv"
ntl_median_path = "data/processed/ntl_annual_median.tif"
feature_df = extract_features(dhs_geo, wealth_df, ntl_median_path, feature_matrix_path)

# 4. Model Training
print("Phase 4: Model Training...")
model = train_and_evaluate(feature_matrix_path, "outputs/model.joblib", "outputs/figures/feature_importance.png")

# 5. Poverty Heatmap
print("Phase 5: Generating Heatmap...")
generate_poverty_heatmap(model, ntl_median_path, "outputs/poverty_heatmap.tif", "outputs/figures/poverty_heatmap.png")

# 6. Multimodal Fusion
print("Phase 6: Multimodal Fusion...")
fetch_ndvi_data(study_region=None, output_prefix="demo")

# Generate Paper Assets Manifest
print("Generating Paper Assets Manifest...")
import pandas as pd
manifest_data = {
    'Asset Type': ['Figure', 'Figure', 'Figure', 'Table', 'Table', 'Table'],
    'Filename': ['feature_importance.png', 'predicted_vs_actual.png', 'poverty_heatmap.png',
                 'table_1_model_performance.csv', 'table_2_feature_importance.csv', 'table_3_cross_validation_results.csv'],
    'Description': ['Feature Importance Plot', 'Predicted vs Actual Plot', 'Spatial Heatmap',
                    'Model Performance Table', 'Feature Importance Table', 'Cross Validation Results Table']
}
manifest_df = pd.DataFrame(manifest_data)
import os
os.makedirs('outputs/paper_assets', exist_ok=True)
manifest_df.to_csv('outputs/paper_assets/paper_assets_manifest.csv', index=False)

print("Pipeline execution completed gracefully.")
"""

    with open(wrapper_path, "w") as f:
        f.write(wrapper_code.strip())

    run_script(wrapper_path)

    if os.path.exists(wrapper_path):
        os.remove(wrapper_path)

    logger.info("End-to-end pipeline execution finished.")

if __name__ == "__main__":
    main()
