import re

with open("src/phase2_features.py", "r") as f:
    content = f.read()

# Make sure df.sample(n=min(50000, len(df))) is in place
content = re.sub(r"df_sample = df\.head\(\d+\)", "df_sample = df.sample(n=min(50000, len(df)), random_state=42)", content)
content = re.sub(r"df_sample = df\.sample\(n=min\(50000, len\(df\)\), random_state=42\)", "df_sample = df.sample(n=min(50000, len(df)), random_state=42)", content) # Idempotent check

# To ensure the graph logic actually works and completes quickly, limit betweenness to k=50
content = content.replace("betweenness = nx.betweenness_centrality(G, k=min(100, len(G.nodes)), random_state=42)", "betweenness = nx.betweenness_centrality(G, k=min(50, len(G.nodes)), random_state=42)")

with open("src/phase2_features.py", "w") as f:
    f.write(content)
