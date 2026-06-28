# Data paths
RAW_DATA_DIR = "data/raw/"
PROCESSED_DATA_DIR = "data/processed/"

# UCI dataset URL
UCI_URL = "https://archive.ics.uci.edu/static/public/316/condition+based+maintenance+of+naval+propulsion+plants.zip"

# Feature names (all 16 inputs)
FEATURE_NAMES = [
    "Lp",       # Lever position
    "v",        # Ship speed (knots)
    "GTT",      # Gas Turbine shaft torque (kN·m)
    "GTn",      # Gas Turbine rate of revolutions (rpm)
    "GGn",      # Gas Generator rate of revolutions (rpm)
    "Ts",       # Starboard Propeller Torque (kN)
    "Tp",       # Port Propeller Torque (kN)
    "T48",      # HP Turbine exit temperature (°C)
    "T1",       # GT Compressor inlet air temperature (°C)
    "T2",       # GT Compressor outlet air temperature (°C)
    "P48",      # HP Turbine exit pressure (bar)
    "P1",       # GT Compressor inlet air pressure (bar)
    "P2",       # GT Compressor outlet air pressure (bar)
    "Pexh",     # GT exhaust pressure (bar)
    "TIC",      # Turbine Injection Control (%)
    "mf",       # Fuel flow (kg/s)
]

# Target names
TARGET_NAMES = ["kMc", "kMt"]   # Compressor decay, Turbine decay

# Splits and seeds
TEST_SIZE = 0.2
VAL_SIZE = 0.1     # From training set, for early stopping
RANDOM_SEED = 42

# Target precision goal
MAE_TARGET = 0.005

# Optuna
OPTUNA_TRIALS = 100
OPTUNA_TIMEOUT_SECONDS = 3600   # 1 hour max per model

# Output directories
MODEL_DIR = "outputs/models/"
FIGURE_DIR = "outputs/figures/"
RESULTS_DIR = "outputs/results/"

HEALTH_THRESHOLDS = {
    "NOMINAL":   (0.990, 1.000),   # < 1% decay
    "WATCH":     (0.980, 0.990),   # 1-2% decay — monitor closely
    "DEGRADED":  (0.970, 0.980),   # 2-3% decay — schedule maintenance
    "CRITICAL":  (0.000, 0.970),   # > 3% decay — immediate inspection
}
