import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import yaml
import os
import glob

# Load config
with open("config.yaml", "r") as f:
    config = yaml.safe_load(f)

# Create directories
os.makedirs(config["paths"]["reports_dir"], exist_ok=True)
os.makedirs(config["paths"]["figures_dir"], exist_ok=True)
os.makedirs(config["paths"]["tables_dir"], exist_ok=True)

raw_data_dir = config["paths"]["raw_data_dir"]

# Load raw files
files = glob.glob(os.path.join(raw_data_dir, "*.csv"))
files.sort()

dfs = {}
for file in files:
    name = os.path.basename(file)
    df = pd.read_csv(file)

    # Try parsing DATE_TIME
    if 'DATE_TIME' in df.columns:
        df['DATE_TIME'] = pd.to_datetime(df['DATE_TIME'], dayfirst=False, format='mixed')
    dfs[name] = df

schema_summaries = []
all_columns = set()

# Process each dataframe
for name, df in dfs.items():
    print(f"Processing {name}...")
    for col in df.columns:
        all_columns.add(col)
        missing_count = df[col].isnull().sum()
        missing_pct = (missing_count / len(df)) * 100
        schema_summaries.append({
            'File': name,
            'Column': col,
            'Dtype': str(df[col].dtype),
            'Non-Null Count': len(df) - missing_count,
            'Missing Percentage': round(missing_pct, 4)
        })

schema_summary_df = pd.DataFrame(schema_summaries)

# Save schema summary table
schema_summary_df.to_csv(config["paths"]["schema_summary_csv"], index=False)

# Generate Missingness Heatmap
plt.figure(figsize=(15, 10))
# Let's create a combined dataframe for missingness. Since row counts differ,
# we will plot a heatmap of missing percentage per column per file.
heatmap_data = schema_summary_df.pivot(index="File", columns="Column", values="Missing Percentage")
sns.heatmap(heatmap_data, annot=True, cmap="YlOrRd", fmt=".2f", cbar_kws={'label': 'Missing Percentage'})
plt.title("Missingness Heatmap by File and Column")
plt.tight_layout()
plt.savefig(config["paths"]["missingness_heatmap_png"], dpi=300, bbox_inches='tight')
plt.close()

# Generate Markdown Report
with open(config["paths"]["schema_audit_md"], "w") as f:
    f.write("# Stage 1 Schema Audit Report\n\n")

    f.write("## Files Audited\n")
    for name, df in dfs.items():
        f.write(f"- **{name}**: {len(df)} rows, {len(df.columns)} columns\n")
        if 'DATE_TIME' in df.columns:
            f.write(f"  - Date Range: {df['DATE_TIME'].min()} to {df['DATE_TIME'].max()}\n")

    f.write("\n## Summary Statistics\n")
    for name, df in dfs.items():
        f.write(f"\n### {name}\n")
        f.write("```\n")
        # Ensure only numeric columns are described for summary stats to avoid long text
        f.write(df.describe(include=[np.number]).to_string())
        f.write("\n```\n")

    f.write("\n## Field Availability Analysis\n")
    f.write("Based on the data characteristics requested for the project, we evaluated the presence of specific channels:\n\n")

    # Check specific fields
    target_fields = {
        'MODULE_TEMPERATURE': 'heatsink/module temperature',
        'AMBIENT_TEMPERATURE': 'ambient temperature',
        'THD': 'THD (Total Harmonic Distortion)',
        'FREQUENCY_DEVIATION': 'frequency deviation (Δf)',
        'REACTIVE_POWER': 'reactive power',
        'FAULT_LABEL': 'IGBT/fault event labels',
        'AC_POWER': 'AC power',
        'DC_POWER': 'DC power',
    }

    available = []
    absent = []

    # Simple check: if a column name matches or contains the key (case-insensitive)
    all_cols_upper = {c.upper() for c in all_columns}

    for key, desc in target_fields.items():
        # strict check for key
        found = False
        for col in all_cols_upper:
            if key in col:
                found = True
                break
        if found:
            available.append(desc)
        else:
            absent.append(desc)

    f.write("### Confirmed available fields\n")
    if available:
        for a in available:
            f.write(f"- {a}\n")
    else:
        f.write("- None\n")

    f.write("\n### Confirmed absent fields\n")
    if absent:
        for a in absent:
            f.write(f"- {a}\n")
    else:
        f.write("- None\n")

print("Stage 1 execution complete.")
