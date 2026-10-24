import os
import csv
from config import get_run_mode, MODE_REAL, MODE_PROTOCOL_ONLY

def generate_paper():
    mode = get_run_mode()

    with open("paper/manuscript.md", "r") as f:
        template = f.read()

    claims = []

    if mode == MODE_PROTOCOL_ONLY:
        results = "### Proposed evaluation protocol – not executed\nData could not be acquired or validated. The proposed pipeline prevents temporal leakage through chronological splitting."
    else:
        results = "### Real Evaluation Results\n"
        # Extract metrics and build claims ledger
        if os.path.exists("outputs/tables/evaluation_chronological.csv"):
            with open("outputs/tables/evaluation_chronological.csv", "r") as f:
                reader = csv.DictReader(f)
                for row in reader:
                    metric = row["metric"]
                    val = row["value"]
                    results += f"- {metric}: {val}\n"
                    claims.append([f"outputs/tables/evaluation_chronological.csv", row, metric, val])
        else:
            results += "No metrics found.\n"

    final_text = template.replace("{RESULTS_SECTION}", results)
    with open("paper/manuscript.md", "w") as f:
        f.write(final_text)

    with open("paper/claims_ledger.csv", "w", newline='') as f:
        w = csv.writer(f)
        w.writerow(["source_file", "row", "column", "value"])
        for c in claims:
            w.writerow(c)

if __name__ == "__main__":
    generate_paper()
