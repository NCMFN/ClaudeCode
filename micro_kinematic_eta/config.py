import os

# Paths
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_RAW_DIR = os.path.join(BASE_DIR, "data", "raw")
DATA_PROCESSED_DIR = os.path.join(BASE_DIR, "data", "processed")
OUTPUTS_MODELS_DIR = os.path.join(BASE_DIR, "outputs", "models")
OUTPUTS_FIGURES_DIR = os.path.join(BASE_DIR, "outputs", "figures")
OUTPUTS_RESULTS_DIR = os.path.join(BASE_DIR, "outputs", "results")

# Data loading
AIS_COLUMNS = ["MMSI", "BaseDateTime", "LAT", "LON", "SOG", "COG", "Heading", "VesselName", "IMO", "VesselType", "Draft", "Cargo", "Status"]

# Filtering parameters
SOG_VALID_RANGE = (0.0, 50.0)  # knots
LAT_VALID_RANGE = (-90.0, 90.0)
LON_VALID_RANGE = (-180.0, 180.0)
COG_VALID_RANGE = (0.0, 360.0)

# DBSCAN parameters
DBSCAN_EPS = 0.05
DBSCAN_MIN_SAMPLES = 10

# Zones
MICRO_KINEMATIC_ZONE_THRESHOLD_KM = 50.0

# Modeling
TEST_SPLIT = 0.2
RANDOM_SEED = 42
LGBM_EARLY_STOPPING_ROUNDS = 50
OPTUNA_TRIALS = 100
