import pytest
import os
import subprocess

def test_secret_hygiene():
    res = subprocess.run(["git", "grep", "-i", "csr.lanl.gov/data-fence"], capture_output=True, text=True)
    out = res.stdout
    lines = out.split('\n')
    for line in lines:
        if line.strip() == "": continue
        if "lanl_leakage_audit_prompt" in line: continue
        if "<REDACTED>" in line: continue
        if "csr.lanl.gov/data-fence" in line and ("grep" in line or "get_redacted_url" in line or "in url" in line): continue
        assert False, f"Found unredacted data-fence URL in {line}"
