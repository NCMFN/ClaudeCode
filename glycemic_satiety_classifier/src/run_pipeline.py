import os
import subprocess

def run_phase(script_name):
    print(f"Running {script_name}...")
    subprocess.run(["python3", script_name], check=True)

if __name__ == "__main__":
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    scripts = [
        "data_loader.py",
        "visualise.py",
        "feature_engineering.py",
        "models.py",
        "evaluate.py",
        "interpretability.py",
        "report.py"
    ]

    for script in scripts:
        if os.path.exists(script):
            run_phase(script)
        else:
            print(f"Error: {script} not found!")
            exit(1)

    print("Pipeline completed successfully.")
