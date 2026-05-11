import pandas as pd
import os
from sklearn.datasets import fetch_openml
import openml

openml.config.cache_directory = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'data', 'raw'))

def load_data():
    datasets = {}
    names = ['jm1', 'pc1', 'kc1', 'kc2', 'pc2', 'pc3']
    for name in names:
        print(f"Fetching {name}...")
        try:
            # First try OpenML
            data = fetch_openml(name=name, version=1, as_frame=True, parser='auto')
            df = data.frame
            # Lowercase columns for consistency
            df.columns = [col.lower() for col in df.columns]
            df['source_project'] = name
            datasets[name] = df
            print(f"Successfully fetched {name} from OpenML.")
        except Exception as e:
            print(f"Error fetching {name} from OpenML: {e}")

    # Need to normalize column names across datasets
    if not datasets:
        raise RuntimeError("Failed to fetch any datasets")

    combined_df = pd.concat(datasets.values(), ignore_index=True)

    # Clean up column names slightly (e.g. handle v(g) vs v_g if any)
    def clean_col_name(col):
        col = col.replace('(', '_').replace(')', '')
        col = col.replace(' ', '_')
        return col

    combined_df.columns = [clean_col_name(col) for col in combined_df.columns]

    out_path = os.path.join(os.path.dirname(__file__), '..', 'data', 'raw', 'combined_nasa_mdp.csv')
    combined_df.to_csv(out_path, index=False)
    print(f"Saved combined data to {out_path} with shape {combined_df.shape}")

if __name__ == '__main__':
    load_data()
