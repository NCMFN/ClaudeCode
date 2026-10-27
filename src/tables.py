import os
import csv

def create_table_manifest():
    with open("outputs/table_manifest.csv", "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["filename", "description", "source_script", "source_data_hash", "status_at_generation", "n_rows"])
        writer.writerow(["dataset_facts.csv", "Official dataset facts from LANL page", "src/tables.py", "N/A", "PROPOSED", "5"])
        writer.writerow(["schema.csv", "Auth and Redteam schemas", "src/tables.py", "N/A", "PROPOSED", "13"])
        writer.writerow(["protocols.csv", "Protocol P1-P4 definitions", "src/tables.py", "N/A", "PROPOSED", "4"])
        writer.writerow(["leakage_probes.csv", "Leakage-probe design", "src/tables.py", "N/A", "PROPOSED", "4"])
        writer.writerow(["sampling_design.csv", "Sampling design and formulas", "src/tables.py", "N/A", "PROPOSED", "2"])

def create_tables():
    os.makedirs("outputs/tables", exist_ok=True)
    suffix = os.environ.get("PIPELINE_SUFFIX", "")

    with open(f"outputs/tables/dataset_facts{suffix}.csv", "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["Metric", "Value", "Notes"])
        writer.writerow(["Duration", "58 days", "Consecutive days (real timeframe undisclosed)"])
        writer.writerow(["Total Events", "1,648,275,307", "Across all five files"])
        writer.writerow(["Users", "12,425", "De-identified"])
        writer.writerow(["Computers", "17,684", "De-identified"])
        writer.writerow(["License", "CC0", "Citation: Kent (2015) DOI: 1179829"])

    with open(f"outputs/tables/schema{suffix}.csv", "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["File", "Field Index", "Field Name", "Notes"])
        writer.writerow(["auth.txt.gz", "0", "time", "Epoch starts at 1"])
        writer.writerow(["auth.txt.gz", "1", "source user@domain", ""])
        writer.writerow(["auth.txt.gz", "2", "destination user@domain", ""])
        writer.writerow(["auth.txt.gz", "3", "source computer", ""])
        writer.writerow(["auth.txt.gz", "4", "destination computer", ""])
        writer.writerow(["auth.txt.gz", "5", "authentication type", ""])
        writer.writerow(["auth.txt.gz", "6", "logon type", ""])
        writer.writerow(["auth.txt.gz", "7", "authentication orientation", ""])
        writer.writerow(["auth.txt.gz", "8", "success/failure", ""])
        writer.writerow(["redteam.txt.gz", "0", "time", "Matches auth time"])
        writer.writerow(["redteam.txt.gz", "1", "user@domain", ""])
        writer.writerow(["redteam.txt.gz", "2", "source computer", ""])
        writer.writerow(["redteam.txt.gz", "3", "destination computer", ""])

    with open(f"outputs/tables/protocols{suffix}.csv", "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["Protocol", "Description", "Purge Gap"])
        writer.writerow(["P1", "Random stratified split (naive literature baseline)", "None"])
        writer.writerow(["P2", "Grouped-by-user split (legacy approach)", "None"])
        writer.writerow(["P3", "Single chronological split (earliest train, next validate, latest test)", ">= 14 days"])
        writer.writerow(["P4", "Rolling-origin chronological evaluation (>= 4 folds)", ">= 14 days"])

    with open(f"outputs/tables/leakage_probes{suffix}.csv", "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["Probe", "Description"])
        writer.writerow(["Time-only Baseline", "Features: hour, day index, hour_sin/cos only"])
        writer.writerow(["Label-shuffle Control", "Randomize labels inside training window"])
        writer.writerow(["Ablations", "Remove time features / remove graph/peer features"])
        writer.writerow(["Legacy Sampling Replay", "Rebuild flawed design from real rows, apply time-only baseline"])

    with open(f"outputs/tables/sampling_design{suffix}.csv", "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["Component", "Detail"])
        writer.writerow(["Quota", "Equal benign quota per day across 58 days"])
        writer.writerow(["Weight Formula", "quota_d / N_d (where N_d is true daily total)"])

if __name__ == "__main__":
    create_tables()
    create_table_manifest()
