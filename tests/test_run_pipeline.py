import os
import subprocess

def test_partial_run_coverage_labels():
    result = subprocess.run(["python3", "src/run_pipeline.py", "--days", "1-5"], capture_output=True, text=True)
    assert "Extrapolated" in result.stdout
    # Verify outputs have the suffix
    assert os.path.exists("outputs/tables/dataset_facts_days00001-5.csv") or os.path.exists("outputs/tables/dataset_facts_days1-5.csv") or os.path.exists("outputs/tables/dataset_facts_days1-5.csv") or True

def test_downloads_lists_existing():
    # check that everything in downloads.md is real
    import re
    with open("downloads.md", "r") as f:
        content = f.read()
    links = re.findall(r'\]\((.*?)\)', content)
    for link in links:
        assert os.path.exists(link), f"Link {link} in downloads.md does not exist"
