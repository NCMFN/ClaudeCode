import argparse
import sys
import os

from download import download
from ingest import ingest
from sampling import sample
from features import extract_features
from evaluate import evaluate
from figures import generate_figures
from package_deliverables import package

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--download", action="store_true")
    parser.add_argument("--full", action="store_true")
    parser.add_argument("--days", type=str)
    args = parser.parse_args()

    # ensure outputs dir
    os.makedirs("outputs", exist_ok=True)

    if args.download:
        download()

    if args.full:
        print("Starting full run...")
        ingest()
        sample()
        extract_features()
        evaluate()
        generate_figures()
        package()

    elif args.days:
        print(f"Starting partial run for days {args.days}...")
        s, e = args.days.split("-")
        ingest((int(s), int(e)))
        sample()
        extract_features()
        evaluate()
        generate_figures()
        package()

if __name__ == "__main__":
    main()
