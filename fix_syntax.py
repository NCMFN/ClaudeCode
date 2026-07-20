with open("src/phase3_modeling.py", "r") as f:
    content = f.read()

content = content.replace("f\\\"{k}: {v:.2f}s\\n\\\"", "f\"{k}: {v:.2f}s\\n\"")
content = content.replace("f\\\"{k}: {v:.2f}s\\n\"", "f\"{k}: {v:.2f}s\\n\"")
content = content.replace("f\"{k}: {v:.2f}s\n", "f\"{k}: {v:.2f}s\\n\"")

with open("src/phase3_modeling.py", "w") as f:
    f.write(content)
