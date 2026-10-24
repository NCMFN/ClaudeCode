import yaml
import os

with open('config.yaml', 'r') as f:
    _config = yaml.safe_load(f)

SEED = _config.get('seed', 42)
N_BENIGN_USERS = _config.get('N_BENIGN_USERS', 50)
MAX_LINES = _config.get('max_lines', 5000000)
MAX_SECONDS = _config.get('max_seconds', 5000000)
PURGE_GAP_SECONDS = _config.get('PURGE_GAP_SECONDS', 86400)
MIN_POSITIVES_PER_TEST_FOLD = _config.get('MIN_POSITIVES_PER_TEST_FOLD', 5)
MIN_PAIRED_UNITS_FOR_WILCOXON = _config.get('MIN_PAIRED_UNITS_FOR_WILCOXON', 5)
N_BOOTSTRAP = _config.get('N_BOOTSTRAP', 100)
K_ALERTS = _config.get('K_ALERTS', 10)

MODE_REAL = "REAL"
MODE_PROTOCOL_ONLY = "PROTOCOL_ONLY"

def get_run_mode():
    run_mode_path = os.path.join("outputs", "run_mode.json")
    if os.path.exists(run_mode_path):
        import json
        with open(run_mode_path, "r") as f:
            data = json.load(f)
            return data.get("mode", MODE_PROTOCOL_ONLY)
    return MODE_PROTOCOL_ONLY

def set_run_mode(mode, reason=""):
    import json
    run_mode_path = os.path.join("outputs", "run_mode.json")
    with open(run_mode_path, "w") as f:
        json.dump({"mode": mode, "reason": reason}, f)
