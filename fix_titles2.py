import re

with open('run_pipeline.py', 'r') as f:
    content = f.read()

# I need to fix the title replacements to properly handle the f-strings
content = content.replace("ax.set_title('Figure 1: Feature Completeness per Source Dataset. Source: WSN_Dataset')", "ax.set_title('Figure 1: Feature Completeness per Source Dataset. Source: WSN_Dataset')")

with open('run_pipeline.py', 'w') as f:
    f.write(content)
