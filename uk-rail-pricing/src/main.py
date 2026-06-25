import subprocess
import sys

def run_step(script_name):
    print(f"Running {script_name}...")
    try:
        subprocess.run([sys.executable, f"uk-rail-pricing/src/{script_name}"], check=True)
    except subprocess.CalledProcessError as e:
        print(f"Error running {script_name}: {e}")
        sys.exit(1)

if __name__ == "__main__":
    run_step("download_data.py")
    run_step("data_loader.py")
    run_step("feature_engineering.py")
    run_step("eda.py")
    run_step("model.py")
    run_step("anomaly_detection.py")
    run_step("equity_analysis.py")
    run_step("route_elasticity.py")
    run_step("report_generator.py")
    print("Pipeline complete!")
