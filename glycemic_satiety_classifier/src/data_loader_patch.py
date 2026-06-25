import pandas as pd
import os

proc_dir = os.path.join('glycemic_satiety_classifier', 'data', 'processed')
df = pd.read_csv(os.path.join(proc_dir, 'satiety_features.csv'))

# Fill missing Fiber_g with 0
df['Fiber_g'] = df['Fiber_g'].fillna(0)

# Check for any other NA
print(df.isnull().sum())
df.to_csv(os.path.join(proc_dir, 'satiety_features.csv'), index=False)
