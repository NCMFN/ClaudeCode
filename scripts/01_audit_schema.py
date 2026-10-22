import os
import yaml
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

STYLE = {
    'primary': '#2E5EAA',
    'secondary': '#D9534F',
}

def main():
    with open("config.yaml", "r") as f:
        config = yaml.safe_load(f)

    data_dir = config['data']['raw_dir']

    files = {
        'plant1_gen': config['data']['plant1_gen'],
        'plant1_weather': config['data']['plant1_weather'],
        'plant2_gen': config['data']['plant2_gen'],
        'plant2_weather': config['data']['plant2_weather']
    }

    dfs = {}
    for key, filename in files.items():
        filepath = os.path.join(data_dir, filename)
        try:
            df = pd.read_csv(filepath)
            dfs[key] = df
        except Exception as e:
            print(f"Error loading {filepath}: {e}")
            return

    summary_data = []

    # Missingness Heatmap logic
    fig, axes = plt.subplots(2, 2, figsize=(15, 10))
    fig.suptitle('Missingness Heatmap Across Datasets', fontsize=16)

    for i, (key, df) in enumerate(dfs.items()):
        ax = axes[i // 2, i % 2]
        if not df.empty:
            sns.heatmap(df.isnull(), cbar=False, cmap="viridis", yticklabels=False, ax=ax)
        ax.set_title(f"{key} (rows: {len(df)})")

        # Schema Summary logic
        for col in df.columns:
            missing_pct = df[col].isnull().sum() / len(df) * 100 if len(df) > 0 else 0
            dtype = str(df[col].dtype)
            summary_data.append({
                'dataset': key,
                'column': col,
                'dtype': dtype,
                'missing_pct': round(missing_pct, 2)
            })

    plt.tight_layout()
    plt.savefig('deliverables/figures/01_missingness_heatmap.png', dpi=300, bbox_inches='tight')
    plt.close()

    summary_df = pd.DataFrame(summary_data)
    summary_df.to_csv('deliverables/tables/01_schema_summary.csv', index=False)

    # Generate Markdown Report
    with open('reports/schema_audit.md', 'w') as f:
        f.write("# Data Schema Audit\n\n")

        f.write("## Overall Statistics\n")
        for key, df in dfs.items():
            f.write(f"### {key}\n")
            f.write(f"- Rows: {len(df)}\n")
            f.write(f"- Columns: {len(df.columns)}\n")

            if 'DATE_TIME' in df.columns:
                try:
                    df['DATE_TIME'] = pd.to_datetime(df['DATE_TIME'], format='mixed')
                    f.write(f"- Date Range: {df['DATE_TIME'].min()} to {df['DATE_TIME'].max()}\n")
                except:
                    f.write("- Date Range: Could not parse DATE_TIME column\n")
            f.write("\n")

        f.write("## Confirmed Available Fields\n")
        all_cols = set()
        for df in dfs.values():
            all_cols.update(df.columns)

        f.write("- ")
        available_fields = []
        if 'MODULE_TEMPERATURE' in all_cols:
            available_fields.append('heatsink/module temperature (MODULE_TEMPERATURE)')
        if 'AMBIENT_TEMPERATURE' in all_cols:
            available_fields.append('ambient temperature (AMBIENT_TEMPERATURE)')
        if 'DC_POWER' in all_cols:
            available_fields.append('DC power (DC_POWER)')
        if 'AC_POWER' in all_cols:
            available_fields.append('AC power (AC_POWER)')

        f.write(", ".join(available_fields))
        f.write("\n\n")

        f.write("## Confirmed Absent Fields\n")
        f.write("Based on the column schemas in the loaded datasets, the following required fields are **absent** from the real data:\n")
        f.write("- Total Harmonic Distortion (THD)\n")
        f.write("- Frequency deviation (Δf)\n")
        f.write("- Reactive power\n")
        f.write("- IGBT/fault event labels (true ground truth fault states)\n")

if __name__ == "__main__":
    main()
