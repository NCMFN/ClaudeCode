with open("src/phase2_features.py", "r") as f:
    content = f.read()

content = content.replace("sub_df = df.head(10000)", "sub_df = df.sample(n=min(50000, len(df)), random_state=42)")

with open("src/phase2_features.py", "w") as f:
    f.write(content)
