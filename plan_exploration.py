import pandas as pd
import numpy as np

# Looking into outputs/datasets/features/tabular_features.parquet
df = pd.read_parquet("outputs/datasets/features/tabular_features.parquet")
print(f"Total entries: {len(df)}")
print(f"Malicious count: {sum(df['label'] == 'malicious')}")
print(df.columns)
