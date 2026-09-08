import os
import pandas as pd

def main():
    figures = os.listdir('outputs/figures/')
    figures = [f for f in figures if f.endswith('.png')]
    tables = os.listdir('outputs/tables/') if os.path.exists('outputs/tables/') else []
    datasets = os.listdir('outputs/datasets/')

    manifest_data = []

    for f in figures:
        manifest_data.append({'asset_type': 'figure', 'filename': f, 'path': f'outputs/figures/{f}'})

    for t in tables:
        manifest_data.append({'asset_type': 'table', 'filename': t, 'path': f'outputs/tables/{t}'})

    for d in datasets:
        manifest_data.append({'asset_type': 'dataset', 'filename': d, 'path': f'outputs/datasets/{d}'})

    df = pd.DataFrame(manifest_data)
    df.to_csv('outputs/paper_assets/paper_assets_manifest.csv', index=False)

if __name__ == "__main__":
    main()
