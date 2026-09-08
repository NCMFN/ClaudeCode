import re

with open('run_pipeline.py', 'r') as f:
    content = f.read()

# Restore original state first
with open('run_pipeline.py', 'w') as f:
    f.write(content)
