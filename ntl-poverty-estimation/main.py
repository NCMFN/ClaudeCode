import subprocess
import sys
import os

def run_phase(script_name):
    print(f"\n--- Running {script_name} ---")
    script_path = os.path.join("src", script_name)
    try:
        subprocess.run([sys.executable, script_path], check=True)
    except subprocess.CalledProcessError as e:
        print(f"Error occurred while running {script_name}: {e}")
        sys.exit(1)

def main():
    print("Starting NTL Poverty Estimation Pipeline")

    phases = [
        "dhs_loader.py",
        "ntl_utils.py",
        "feature_extraction.py",
        "model_pipeline.py",
        "poverty_mapper.py",
        "multimodal_fusion.py"
    ]

    for phase in phases:
        run_phase(phase)

    print("\nPipeline complete. All outputs generated.")

if __name__ == "__main__":
    main()
