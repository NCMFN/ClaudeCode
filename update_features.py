with open("src/phase2_features.py", "r") as f:
    content = f.read()

# Make sure we don't accidentally fabricate anything here. Wait, phase 2 doesn't have explicit fabrication, but it processes the data. Let's make sure it handles the label correctly.
new_content = content.replace("Only 1 class found in total data", "")
with open("src/phase2_features.py", "w") as f:
    f.write(new_content)
