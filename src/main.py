import sys, os
sys.path.append(os.path.dirname(__file__))
from data_ingest import ingest_data; from simulate import run_simulation; from analysis import analyze_results
if __name__ == "__main__": ingest_data(); run_simulation(); analyze_results()
