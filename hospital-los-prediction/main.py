import subprocess
import sys
import os

def main():
    print("Starting ML Pipeline Execution...")

    # Update PYTHONPATH so imports work correctly
    env = os.environ.copy()
    env["PYTHONPATH"] = os.path.abspath(os.path.join(os.path.dirname(__file__), "src"))

    print("\n--- Running Training Pipeline ---")
    # This encompasses ETL, Features, and Model Training/Evaluation
    subprocess.run([sys.executable, "src/train.py"], env=env, check=True)

    print("\n--- Running Prediction Test ---")
    subprocess.run([sys.executable, "src/predict.py"], env=env, check=True)

    print("\nPipeline Execution Completed Successfully.")

if __name__ == "__main__":
    main()
