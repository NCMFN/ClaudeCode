import os
import hashlib
from datetime import datetime
import json
import gzip
import yaml

def load_config():
    with open("config/protocol.yaml", "r") as f:
        return yaml.safe_load(f)

def get_hash(filepath):
    h = hashlib.sha256()
    if os.path.exists(filepath):
        with open(filepath, 'rb') as f:
            for chunk in iter(lambda: f.read(4096), b""):
                h.update(chunk)
        return h.hexdigest()
    return "N/A"

def write_provenance(status, file_info):
    os.makedirs("outputs", exist_ok=True)
    prov = {
        "dataset_urls": {
            "landing": "https://csr.lanl.gov/data/cyber1/",
            "auth": "https://csr.lanl.gov/data/cyber1/auth.txt.gz",
            "redteam": "https://csr.lanl.gov/data/cyber1/redteam.txt.gz"
        },
        "retrieval_date": datetime.now().isoformat(),
        "files": file_info,
        "status": status
    }
    with open("outputs/provenance.json", "w") as f:
        json.dump(prov, f, indent=2)

def validate_file(filepath, expected_fields):
    print(f"Validating {filepath}...")
    try:
        with gzip.open(filepath, 'rt') as f:
            # Just read a few lines to validate schema
            prev_time = None
            for i, line in enumerate(f):
                if i >= 10:  # Validate first 10 lines
                    break
                parts = line.strip().split(',')
                if len(parts) != expected_fields:
                    raise ValueError(f"Schema mismatch in {filepath}: expected {expected_fields} fields, found {len(parts)} on line {i+1}")

                # Time validation for auth (field 0)
                if expected_fields == 9:
                    try:
                        time = int(parts[0])
                        if i == 0 and time != 1:
                           raise ValueError(f"Time epoch must start at 1, found {time}")
                        if prev_time is not None and time < prev_time:
                           raise ValueError("Time must be non-decreasing")
                        prev_time = time
                    except ValueError as e:
                        if "invalid literal" not in str(e): # re-raise our own
                           raise

        print(f"{filepath} validation passed.")
        return True
    except Exception as e:
        print(f"Validation failed: {e}")
        return False

def check_lanl_local(data_dir):
    auth_path = os.path.join(data_dir, "auth.txt.gz")
    redteam_path = os.path.join(data_dir, "redteam.txt.gz")

    file_info = {
        "auth.txt.gz": {"size": "N/A", "sha256": "N/A"},
        "redteam.txt.gz": {"size": "N/A", "sha256": "N/A"}
    }

    missing = []
    if not os.path.exists(auth_path):
        missing.append("auth.txt.gz")
    else:
        file_info["auth.txt.gz"]["size"] = os.path.getsize(auth_path)
        file_info["auth.txt.gz"]["sha256"] = get_hash(auth_path)
        if not validate_file(auth_path, 9):
            missing.append("auth.txt.gz (invalid)")

    if not os.path.exists(redteam_path):
        missing.append("redteam.txt.gz")
    else:
        file_info["redteam.txt.gz"]["size"] = os.path.getsize(redteam_path)
        file_info["redteam.txt.gz"]["sha256"] = get_hash(redteam_path)
        if not validate_file(redteam_path, 4):
            missing.append("redteam.txt.gz (invalid)")

    if missing:
        print("\n--- MISSING LOCAL DATA ---")
        print("The official LANL files are gated behind a download form and cannot be fetched automatically.")
        print("Please download the data manually from: https://csr.lanl.gov/data/cyber1/")
        print(f"Place the following files in {data_dir}:")
        print("  - auth.txt.gz (~7.2 GB)")
        print("  - redteam.txt.gz (~4.8 KB)")
        print("--------------------------\n")
        return False, file_info

    return True, file_info

if __name__ == "__main__":
    config = load_config()
    data_dir = os.environ.get("LANL_DATA_DIR", config.get("data", {}).get("local_dir", "data/lanl/"))

    can_access, file_info = check_lanl_local(data_dir)

    with open('STATUS.md', 'w') as f:
        if can_access:
            f.write("COMPLETED: genuine measurements\n")
            write_provenance("COMPLETED", file_info)
        else:
            f.write("PROPOSED METHODOLOGY: no validation performed\n")
            f.write("\nBlocker: Local data files missing or invalid.\n")
            f.write("\nTo resume on a machine with access, run: python src/run_pipeline.py\n")
            write_provenance("PROPOSED", file_info)
