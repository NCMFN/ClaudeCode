# Resuming the Pipeline Locally

Because the official LANL dataset is gated behind a web form, the data cannot be downloaded automatically by the pipeline script. To run the full analysis on your own machine or a cloud VM, follow these steps.

## 1. Environment Setup
Install the Python requirements.
```bash
pip install -r requirements.txt
```

## 2. Data Placement
Download the data manually from [https://csr.lanl.gov/data/cyber1/](https://csr.lanl.gov/data/cyber1/).
You only need the authentication and red-team event files. Place them into the `data/lanl/` directory:
- `data/lanl/auth.txt.gz` (~7.2 GB)
- `data/lanl/redteam.txt.gz` (~4.8 KB)

Alternatively, set the `LANL_DATA_DIR` environment variable to the directory containing these files.

## 3. Running the Pipeline
**Partial Dry Run:**
To run a small slice of the data and verify throughput/memory, use the `--days` argument. For example, to run days 1 through 5:
```bash
python3 src/run_pipeline.py --days 1-5
```
Outputs from partial runs will have the coverage suffix appended (e.g., `_days01-05`).

**Full Run:**
To run the entire 58-day pipeline:
```bash
python3 src/run_pipeline.py
```

## 4. Where the Outputs Land
Outputs are automatically packaged into:
- `deliverables/leakage_audit_bundle.zip`
- View individual files under `deliverables/figures/`, `deliverables/tables/`, and `deliverables/paper/`.
