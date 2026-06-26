import subprocess
import sys

def run_step(script_name: str, description: str):
    print(f"\n{'='*50}")
    print(f"Executing: {description} ({script_name})")
    print(f"{'='*50}")
    try:
        # Use subprocess.run with check=True to halt on failure
        subprocess.run([sys.executable, f"src/{script_name}"], check=True)
    except subprocess.CalledProcessError as e:
        print(f"\n[ERROR] Step {script_name} failed with exit code {e.returncode}.")
        sys.exit(1)

def main():
    print("Starting Hospital LOS Prediction Pipeline...\n")

    # Run the ETL phase
    run_step("etl.py", "Data Loading and ETL")

    # Feature Engineering (Evaluate/Test Phase)
    run_step("features.py", "Feature Engineering Evaluation")

    # Model Training
    run_step("train.py", "Model Training and Evaluation")

    print("\n[SUCCESS] Pipeline executed completely.")

if __name__ == "__main__":
    main()
