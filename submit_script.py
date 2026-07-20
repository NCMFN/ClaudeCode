import json
import urllib.request
import os

req = urllib.request.Request(
    'http://localhost:8000/submit',
    data=json.dumps({
        "branch_name": "jules-12849808128917581953-a4be04c2",
        "commit_message": "feat: restored actual figures and tables to output artifacts",
        "description": "Restored actual figures and tables to output artifacts",
        "title": "feat: scalable ML pipeline outputs"
    }).encode(),
    headers={'Content-Type': 'application/json'}
)
try:
    response = urllib.request.urlopen(req)
    print(response.read().decode())
except Exception as e:
    print(f"Error: {e}")
