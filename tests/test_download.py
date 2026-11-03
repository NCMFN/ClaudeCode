import pytest
import os
import subprocess

def test_no_verify_false():
    res = subprocess.run(["grep", "-rn", "verify=False", "src/"], capture_output=True, text=True).stdout
    assert res.strip() == "", "verify=False found in src/"

    res2 = subprocess.run(["grep", "-rn", "--insecure", "src/"], capture_output=True, text=True).stdout
    assert res2.strip() == "", "--insecure found in src/"

    res3 = subprocess.run(["grep", "-rn", "curl -k", "src/"], capture_output=True, text=True).stdout
    assert res3.strip() == "", "curl -k found in src/"
