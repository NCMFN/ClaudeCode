import sys
import os
import glob
import pandas as pd
from config import get_run_mode, set_run_mode, MODE_REAL, MODE_PROTOCOL_ONLY
import acquire
import ingest
import splits
import leakage_audit
import evaluate
import robustness
import explain
import artifacts
import paper_numbers

def run():
    print("Running pipeline...")
    acquire.main()

    mode = get_run_mode()

    if mode == MODE_REAL:
        print("REAL Mode: Running full pipeline.")
        ingest.ingest()

        # Check if mode fell back to PROTOCOL_ONLY after ingest
        mode = get_run_mode()
        if mode == MODE_REAL:
            df = pd.read_parquet("outputs/datasets/ingested.parquet")

            s = splits.generate_splits(df)
            leakage_audit.run_leakage_audit(df, s)
            evaluate.run_evaluation(df, s['chronological_holdout'])
            robustness.run_robustness(df, s['chronological_holdout'])
            explain.run_explainability(df, s['chronological_holdout'])

    if mode == MODE_PROTOCOL_ONLY:
        print("PROTOCOL_ONLY Mode: Skipping data generation.")

    artifacts.generate_figures()
    paper_numbers.generate_paper()
    artifacts.generate_manifest()

    # Regenerate downloads.md
    with open("downloads.md", "w") as f:
        f.write("# Downloads\n\n")
        f.write("Files generated:\n")
        for file in glob.glob("outputs/**/*", recursive=True):
            if os.path.isfile(file):
                f.write(f"- {file}\n")

    print("Pipeline finished.")

if __name__ == "__main__":
    run()
