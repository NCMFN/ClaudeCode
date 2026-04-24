import os
import subprocess
import sys

def run_script(script_name):
    script_path = os.path.join(os.path.dirname(__file__), 'src', script_name)
    print(f"\n{'='*50}\nRunning {script_name}...\n{'='*50}")
    result = subprocess.run([sys.executable, script_path], check=True)
    if result.returncode != 0:
        print(f"Error running {script_name}")
        sys.exit(1)

if __name__ == "__main__":
    scripts = [
        # "01_data_processing.py", # Skipping this since it takes several minutes and downloads data we already processed.
        "02_model_training.py",
        "03_validation.py",
        "04_visualization.py",
        "05_architecture.py"
    ]

    print("Starting End-to-End Pipeline Verification (Skipping Step 1 Download for speed)...")
    for script in scripts:
        run_script(script)

    print("\n✅ End-to-End Pipeline Verification Complete.")
