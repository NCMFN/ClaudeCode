import pandas as pd
print("Ingestion data:")
try:
    df1 = pd.read_parquet("outputs/datasets/harmonized_events")
    print(df1.columns)
except Exception as e:
    print(e)
print("Features data:")
try:
    df2 = pd.read_parquet("outputs/datasets/features/tabular_features.parquet")
    print(df2.columns)
except Exception as e:
    print(e)
