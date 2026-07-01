import pandas as pd

# Let's standardize the target to 'y' for all files
f1 = 'data/kaggle_lead_scoring.csv'
df = pd.read_csv(f1)
if 'Converted' in df.columns and 'y' not in df.columns:
    df['y'] = df['Converted']
    df.to_csv(f1, index=False)
    print("Standardized target to 'y' in", f1)
