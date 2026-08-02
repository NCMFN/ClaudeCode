import json
import os
import subprocess
from pathlib import Path

def run_pipeline():
    print("Running pipeline...")
    # 1. Data Ingest
    subprocess.run(["python3", "data_ingest.py"], check=True)

    # 2-5 are imported and run via simulate.py
    # 6. Simulate
    print("Running simulation...")
    import simulate
    import analysis
    config = simulate.load_config()
    from data_ingest import ingest_data
    rtt_series = ingest_data() # it's already cached from step 1 but this loads it
    df_results = simulate.simulate(rtt_series, config)

    # 7. Analysis
    print("Running analysis...")
    results_json = analysis.analyze_and_export(df_results, config)
    return results_json

def check_reproducibility():
    print("\n--- Running Reproducibility Check ---")
    out_dir = Path("outputs")

    # Run 1
    res1 = run_pipeline()
    with open(out_dir / "results_run1.json", "w") as f:
        json.dump(res1, f, indent=4)

    # Run 2
    res2 = run_pipeline()
    with open(out_dir / "results_run2.json", "w") as f:
        json.dump(res2, f, indent=4)

    # Diff
    import filecmp
    is_same = filecmp.cmp(out_dir / "results_run1.json", out_dir / "results_run2.json")
    diff_text = "" if is_same else "Differences found between run 1 and run 2!"

    with open(out_dir / "reproducibility_diff.txt", "w") as f:
        f.write(diff_text)

    if not is_same:
        raise ValueError("Reproducibility check failed! Output differs between runs with same seed.")
    else:
        print("Reproducibility check passed.")

def generate_report():
    out_dir = Path("outputs")
    with open(out_dir / "results.json", "r") as f:
        res = json.load(f)

    with open("config.yaml", "r") as f:
        import yaml
        config = yaml.safe_load(f)

    report = f"""# Dynamic Post-Processing Block-Sizer (DBS) for Time-Constrained QKD
## Simulation Report

### Methodology
This simulation evaluates a Dynamic Block-Sizer (DBS) policy against fixed-block baselines.
The network RTT dataset is sourced from {config['rtt_data_source']}.
Finite-size secure key rates (SKR) are calculated using the pedagogical finite-size correction term
from Tomamichel et al. (Nat. Commun. 3, 634, 2012), implemented as `7 * sqrt(log2(2/eps) / N)`.
Error correction efficiency f(E) is set to {config['error_correction_efficiency_f']} (Standard LDPC assumption).
A Time-to-Key (T2K) proxy metric is modeled as illustrative constants: `T2K = {config['c1']} * block_size + {config['c2']} * rtt`.

### Results Summary
**Mean Secure Key Rate (bits/block):**
- DBS: {res['SKR_Means']['DBS']:.4f} (95% CI: +/- {res['SKR_CIs_95']['DBS']:.4f})
- Fixed Large: {res['SKR_Means']['Fixed_Large']:.4f} (95% CI: +/- {res['SKR_CIs_95']['Fixed_Large']:.4f})
- Fixed Small: {res['SKR_Means']['Fixed_Small']:.4f} (95% CI: +/- {res['SKR_CIs_95']['Fixed_Small']:.4f})

**Mean Time-to-Key proxy:**
- DBS: {res['T2K_Means']['DBS']:.2f} (95% CI: +/- {res['T2K_CIs_95']['DBS']:.2f})
- Fixed Large: {res['T2K_Means']['Fixed_Large']:.2f} (95% CI: +/- {res['T2K_CIs_95']['Fixed_Large']:.2f})
- Fixed Small: {res['T2K_Means']['Fixed_Small']:.2f} (95% CI: +/- {res['T2K_CIs_95']['Fixed_Small']:.2f})

### Statistical Validation (Wilcoxon Signed-Rank)
**DBS vs Fixed Large:**
- SKR Difference: W = {res['Statistics']['DBS_vs_Large']['SKR']['W']}, p = {res['Statistics']['DBS_vs_Large']['SKR']['p_value']:.4e} (Effect Size r: {res['Statistics']['DBS_vs_Large']['SKR']['effect_size_r']:.2f})
- T2K Difference: W = {res['Statistics']['DBS_vs_Large']['T2K']['W']}, p = {res['Statistics']['DBS_vs_Large']['T2K']['p_value']:.4e} (Effect Size r: {res['Statistics']['DBS_vs_Large']['T2K']['effect_size_r']:.2f})

**DBS vs Fixed Small:**
- SKR Difference: W = {res['Statistics']['DBS_vs_Small']['SKR']['W']}, p = {res['Statistics']['DBS_vs_Small']['SKR']['p_value']:.4e} (Effect Size r: {res['Statistics']['DBS_vs_Small']['SKR']['effect_size_r']:.2f})
- T2K Difference: W = {res['Statistics']['DBS_vs_Small']['T2K']['W']}, p = {res['Statistics']['DBS_vs_Small']['T2K']['p_value']:.4e} (Effect Size r: {res['Statistics']['DBS_vs_Small']['T2K']['effect_size_r']:.2f})
"""
    with open(out_dir / "report.md", "w") as f:
        f.write(report)

    print("Report generated at outputs/report.md")

if __name__ == "__main__":
    check_reproducibility()
    generate_report()
