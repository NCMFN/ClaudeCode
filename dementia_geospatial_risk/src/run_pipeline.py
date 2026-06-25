import subprocess
import sys
from pathlib import Path
import time

def check_process():
    # Wait for models to finish
    print("Waiting for model training to finish...")
    while True:
        try:
            result = subprocess.run(['pgrep', '-f', 'models.py'], capture_output=True, text=True)
            if not result.stdout.strip():
                print("Models finished training.")
                break
            time.sleep(10)
        except Exception as e:
            print("Error checking process:", e)
            break

def run_phase(script_name):
    print(f"\n{'='*50}\nRunning {script_name}\n{'='*50}")
    try:
        subprocess.run([sys.executable, f"dementia_geospatial_risk/src/{script_name}"], check=True)
    except subprocess.CalledProcessError as e:
        print(f"Error executing {script_name}. Pipeline halted.")
        sys.exit(1)

def main():
    check_process()
    run_phase("evaluation.py")
    run_phase("gis_mapping.py")
    run_phase("report.py")
    print("Pipeline fully executed.")

if __name__ == "__main__":
    main()
