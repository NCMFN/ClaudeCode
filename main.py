import subprocess
import sys
import os

def run_step(script_path):
    print(f"Running {script_path}...")
    result = subprocess.run([sys.executable, script_path], check=True)
    return result

def main():
    print("Starting QKD DBS Simulation Pipeline (Run 1)...")
    run_step("src/data_ingest.py")
    run_step("src/simulate.py")
    os.rename("outputs/results.json", "outputs/results_run1.json")

    print("Starting QKD DBS Simulation Pipeline (Run 2)...")
    run_step("src/data_ingest.py")
    run_step("src/simulate.py")
    os.rename("outputs/results.json", "outputs/results_run2.json")

    # Diff outputs
    try:
        subprocess.run(["diff", "outputs/results_run1.json", "outputs/results_run2.json"], check=True, stdout=open("outputs/reproducibility_diff.txt", "w"))
        print("Reproducibility check passed. Diff saved to outputs/reproducibility_diff.txt.")
    except subprocess.CalledProcessError as e:
        print("Reproducibility check failed! Output differs between runs. See outputs/reproducibility_diff.txt.")
        # It writes the diff output in the file anyway

    # Copy one back for the rest of pipeline
    os.rename("outputs/results_run1.json", "outputs/results.json")
    os.remove("outputs/results_run2.json")

    print("Generating analysis and reporting layer...")
    run_step("src/analysis.py")
    run_step("reporting/generate_outputs.py")
    print("Pipeline completed successfully.")

if __name__ == "__main__":
    main()
