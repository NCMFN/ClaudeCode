#!/bin/bash
set -e
python3 src/main.py
cp outputs/results.json outputs/results_run1.json
python3 src/main.py
cp outputs/results.json outputs/results_run2.json
diff outputs/results_run1.json outputs/results_run2.json > outputs/reproducibility_diff.txt || true
echo "Status,Details" > src/outputs/tables/reproducibility_diff_summary.csv
if [ -s outputs/reproducibility_diff.txt ]; then echo "Failed,Diff found" >> src/outputs/tables/reproducibility_diff_summary.csv; else echo "Passed,No diff" >> src/outputs/tables/reproducibility_diff_summary.csv; fi
python3 src/reporting/generate_outputs.py
python3 -c "
import json, yaml
with open('config.yaml', 'r') as f: config = yaml.safe_load(f)
with open('outputs/results.json', 'r') as f: results = json.load(f)
st, ts = results['stats'], results['tests']
rep = f\"\"\"# DBS Policy Simulation Report\n## Methodology\n## Results Summary\n- DBS Mean SKR: {st['dbs']['skr_mean']:.4f}\n- Fixed Large Mean SKR: {st['fixed_large']['skr_mean']:.4f}\n- Fixed Small Mean SKR: {st['fixed_small']['skr_mean']:.4f}\n## Statistical Tests (Wilcoxon Signed-Rank)\n- **DBS vs Fixed Large**: p-value = {ts['dbs_vs_large']['p_value']:.4e}, effect size (d) = {ts['dbs_vs_large']['effect_size_cohens_d']:.4f}\n- **DBS vs Fixed Small**: p-value = {ts['dbs_vs_small']['p_value']:.4e}, effect size (d) = {ts['dbs_vs_small']['effect_size_cohens_d']:.4f}\n\"\"\"
with open('outputs/report.md', 'w') as f: f.write(rep)
"
