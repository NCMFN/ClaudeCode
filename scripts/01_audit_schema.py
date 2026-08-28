import pandas as pd
import yaml
import seaborn as sns
import matplotlib.pyplot as plt
import os

with open('config.yaml', 'r') as f:
    config = yaml.safe_load(f)

p1_gen = pd.read_csv(config['data']['raw']['plant_1_gen'])
p1_weather = pd.read_csv(config['data']['raw']['plant_1_weather'])
p2_gen = pd.read_csv(config['data']['raw']['plant_2_gen'])
p2_weather = pd.read_csv(config['data']['raw']['plant_2_weather'])

def process_df(df, name):
    return {
        'Dataset': name,
        'Rows': len(df),
        'Columns': df.columns.tolist(),
        'Date_Range': f"{df['DATE_TIME'].min()} to {df['DATE_TIME'].max()}" if 'DATE_TIME' in df.columns else "N/A",
        'df': df
    }

datasets = [
    process_df(p1_gen, 'Plant 1 Generation'),
    process_df(p1_weather, 'Plant 1 Weather'),
    process_df(p2_gen, 'Plant 2 Generation'),
    process_df(p2_weather, 'Plant 2 Weather')
]

schema_summary_list = []
heatmap_df = pd.DataFrame()

with open(config['outputs']['reports']['schema_audit'], 'w') as f:
    f.write("# Schema Audit Report\n\n")

    all_columns = set()
    for d in datasets:
        all_columns.update(d['Columns'])
        f.write(f"## {d['Dataset']}\n")
        f.write(f"- **Rows**: {d['Rows']}\n")
        f.write(f"- **Date Range**: {d['Date_Range']}\n\n")

        df = d['df']
        f.write("### Column Details\n")
        for col in df.columns:
            missing_pct = df[col].isnull().mean() * 100
            dtype = str(df[col].dtype)
            f.write(f"- **{col}**: Dtype: `{dtype}`, Missing: {missing_pct:.2f}%\n")
            schema_summary_list.append({
                'Dataset': d['Dataset'],
                'Column': col,
                'Dtype': dtype,
                'Missing_%': f"{missing_pct:.2f}%"
            })
        f.write("\n")

    # Compile schema audit table
    f.write("## Summary Statistics\n")
    for d in datasets:
        f.write(f"### {d['Dataset']}\n")
        f.write(d['df'].describe().to_markdown())
        f.write("\n\n")

    f.write("## Data Characteristics\n")

    # Check for requested fields
    required_fields = {
        'Module Temperature': ['MODULE_TEMPERATURE'],
        'Ambient Temperature': ['AMBIENT_TEMPERATURE'],
        'DC Power': ['DC_POWER'],
        'AC Power': ['AC_POWER'],
        'THD': ['THD'],
        'Frequency Deviation': ['FREQUENCY_DEVIATION', 'DELTA_F'],
        'Reactive Power': ['REACTIVE_POWER'],
        'Fault/IGBT Labels': ['FAULT', 'IGBT', 'LABEL', 'STATUS']
    }

    f.write("### Confirmed available fields\n")
    available_found = False
    for field, cols in required_fields.items():
        if any(col in all_columns for col in cols):
            f.write(f"- {field}\n")
            available_found = True
    if not available_found: f.write("- None\n")

    f.write("\n### Confirmed absent fields\n")
    absent_found = False
    for field, cols in required_fields.items():
        if not any(col in all_columns for col in cols):
            f.write(f"- {field}\n")
            absent_found = True
    if not absent_found: f.write("- None\n")


schema_df = pd.DataFrame(schema_summary_list)
schema_df.to_csv(config['outputs']['tables']['schema_summary'], index=False)

# Missingness heatmap
missing_dfs = []
for d in datasets:
    missing_df = d['df'].isnull().mean().reset_index()
    missing_df.columns = ['Column', 'Missing_Ratio']
    missing_df['Dataset'] = d['Dataset']
    missing_dfs.append(missing_df)

all_missing = pd.concat(missing_dfs)
heatmap_data = all_missing.pivot(index='Dataset', columns='Column', values='Missing_Ratio')
heatmap_data = heatmap_data.fillna(-0.1) # Differentiate missing from 0% missing

plt.figure(figsize=(12, 6))
sns.heatmap(heatmap_data, annot=True, cmap='viridis', fmt='.2f', cbar_kws={'label': 'Missing Ratio'})
plt.title('Missingness Heatmap Across Datasets')
plt.tight_layout()
plt.savefig(config['outputs']['figures']['missingness_heatmap'], dpi=300, bbox_inches='tight')

print("Schema audit complete.")
