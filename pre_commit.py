import subprocess
import os

print("Running Pre-Commit checks...")

# 1. Formatting Check (flake8/black ideally, using what we have)
print("1. Checking code syntax...")
res = subprocess.run(["python3", "-m", "py_compile", "src/analysis.py"])
if res.returncode == 0:
    print("Syntax check passed.")

# 2. Testing Execution
print("\n2. Running Unit Tests...")
res = subprocess.run(["python3", "-m", "unittest", "discover", "-s", "src", "-p", "*.py"])
if res.returncode == 0:
    print("Unit tests passed.")

print("\nPre-commit checks complete.")
