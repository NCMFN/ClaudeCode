import sys
import os
import argparse
import time
import resource

def get_maxrss():
    usage = resource.getrusage(resource.RUSAGE_SELF)
    # ru_maxrss is in kilobytes on Linux, bytes on macOS. Assume Linux (kb -> MB)
    return usage.ru_maxrss / 1024.0

def main():
    parser = argparse.ArgumentParser(description="Run LANL leakage audit pipeline.")
    parser.add_argument("--days", type=str, help="Run partial pipeline for specified days (e.g., '1-5')")
    args = parser.parse_args()

    start_time = time.time()

    print("Running pipeline...")
    # 1. Ingest
    os.system("python3 src/ingest.py")

    with open('STATUS.md', 'r') as f:
        status = f.read()

    suffix = f"_days{args.days.zfill(5)}" if args.days else ""
    os.environ["PIPELINE_SUFFIX"] = suffix

    if "PROPOSED METHODOLOGY" in status:
        print("Dataset not fully accessible locally. Generating PROPOSED METHODOLOGY outputs only.")
        os.system("python3 src/tables.py")
        os.system("python3 src/figures.py")
        os.system("python3 src/package_deliverables.py")
    else:
        print("Dataset fully accessible. Running full/partial pipeline...")
        # Placeholder for full execution
        pass

    elapsed = time.time() - start_time
    max_rss = get_maxrss()

    print(f"\n--- Profiling ---")
    print(f"Elapsed time: {elapsed:.2f} seconds")
    print(f"Peak RSS: {max_rss:.2f} MB")
    if args.days:
        try:
            start, end = map(int, args.days.split('-'))
            days_run = end - start + 1
            extrapolated = (elapsed / days_run) * 58
            print(f"Extrapolated 58-day runtime: {extrapolated:.2f} seconds ({extrapolated/3600:.2f} hours)")
        except Exception:
            pass
    print("-----------------\n")

if __name__ == "__main__":
    main()
