import pandas as pd
import numpy as np

def prep_b2b():
    for f in ['data/kaggle_b2b_clean.csv', 'data/kaggle_b2b_noisy.csv']:
        df = pd.read_csv(f)
        # Handle noisy file where Campaign_Response_Rate might be parsed as string
        df['Campaign_Response_Rate (%)'] = pd.to_numeric(df['Campaign_Response_Rate (%)'], errors='coerce').fillna(0)

        # Create target 'y'
        df['y'] = (df['Campaign_Response_Rate (%)'] > 0).astype(int)
        df.to_csv(f, index=False)
        print(f"Updated {f} with target 'y', sum:", df['y'].sum(), "out of", len(df))

if __name__ == '__main__':
    prep_b2b()
