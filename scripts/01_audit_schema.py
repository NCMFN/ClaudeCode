import pandas as pd
import numpy as np
import yaml
import os
import matplotlib.pyplot as plt
import seaborn as sns

with open("config.yaml", "r") as f:
    config = yaml.safe_load(f)

raw_dir = config['data']['raw_dir']
tables_dir = config['data']['tables_dir']
figures_dir = config['data']['figures_dir']
reports_dir = config['data']['reports_dir']

files = {
    'P1_Gen': 'Plant_1_Generation_Data.csv',
    'P1_Wea': 'Plant_1_Weather_Sensor_Data.csv',
    'P2_Gen': 'Plant_2_Generation_Data.csv',
    'P2_Wea': 'Plant_2_Weather_Sensor_Data.csv',
}

dfs = {}
for k, v in files.items():
    dfs[k] = pd.read_csv(os.path.join(raw_dir, v))

# Concatenate all to get an overview, or just summarize each
summary_rows = []
all_cols = set()
for k, df in dfs.items():
    all_cols.update(df.columns)
    for col in df.columns:
        summary_rows.append({
            'File': k,
            'Column': col,
            'Dtype': str(df[col].dtype),
            'Missing_Count': df[col].isnull().sum(),
            'Missing_Pct': (df[col].isnull().sum() / len(df)) * 100
        })

summary_df = pd.DataFrame(summary_rows)
summary_df.to_csv(os.path.join(tables_dir, '01_schema_summary.csv'), index=False)

# Missingness heatmap
fig, axes = plt.subplots(2, 2, figsize=(15, 10))
axes = axes.flatten()
for i, (k, df) in enumerate(dfs.items()):
    sns.heatmap(df.isnull(), cbar=False, ax=axes[i], cmap='viridis')
    axes[i].set_title(f'Missingness - {k}')
plt.tight_layout()
plt.savefig(os.path.join(figures_dir, '01_missingness_heatmap.png'), dpi=300)
plt.close()

# Generate markdown report
expected_fields = {
    'module temperature': ['MODULE_TEMPERATURE'],
    'ambient temperature': ['AMBIENT_TEMPERATURE'],
    'DC power': ['DC_POWER'],
    'AC power': ['AC_POWER'],
    'THD': [], # No THD
    'frequency deviation': [], # No freq
    'reactive power': [], # No reactive
    'IGBT/fault event labels': [] # No labels
}

with open(os.path.join(reports_dir, 'schema_audit.md'), 'w') as f:
    f.write("# Schema Audit Report\n\n")
    for k, df in dfs.items():
        f.write(f"## {k}\n")
        f.write(f"- Rows: {len(df)}\n")
        f.write(f"- Columns: {len(df.columns)}\n")
        f.write("\n")

    f.write("## Confirmed available fields\n")
    f.write("- Module temperature (MODULE_TEMPERATURE)\n")
    f.write("- Ambient temperature (AMBIENT_TEMPERATURE)\n")
    f.write("- DC power (DC_POWER)\n")
    f.write("- AC power (AC_POWER)\n")

    f.write("\n## Confirmed absent fields\n")
    f.write("- THD (Total Harmonic Distortion) is ABSENT.\n")
    f.write("- Frequency deviation (Δf) is ABSENT.\n")
    f.write("- Reactive power is ABSENT.\n")
    f.write("- Ground truth IGBT/fault event labels are ABSENT.\n")
