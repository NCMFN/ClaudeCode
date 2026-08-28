import pandas as pd
import yaml
import os

def load_config(config_path="config.yaml"):
    with open(config_path, "r") as f:
        return yaml.safe_load(f)

def audit_schema():
    config = load_config()
    raw_dir = config["data"]["raw_dir"]
    files = config["data"]["files"]
    report_path = config["reports"]["schema_audit"]

    os.makedirs(os.path.dirname(report_path), exist_ok=True)

    # We will accumulate the report content in a string
    report_content = "# Schema Audit Report\n\n"

    # Store all columns seen to check for specific fields later
    all_columns = set()

    for key, filename in files.items():
        filepath = os.path.join(raw_dir, filename)
        report_content += f"## {filename}\n\n"

        try:
            df = pd.read_csv(filepath)

            # Row counts
            report_content += f"- **Row count**: {len(df)}\n"

            # Date ranges
            if 'DATE_TIME' in df.columns:
                try:
                    df['DATE_TIME'] = pd.to_datetime(df['DATE_TIME'], format="mixed", dayfirst=True)
                    min_date = df['DATE_TIME'].min()
                    max_date = df['DATE_TIME'].max()
                    report_content += f"- **Date range**: {min_date} to {max_date}\n"
                except Exception as e:
                    report_content += f"- **Date range**: Error parsing DATE_TIME: {e}\n"
            else:
                report_content += f"- **Date range**: No DATE_TIME column found.\n"

            report_content += "\n### Columns\n"
            report_content += "| Column Name | Data Type | Missing Values (%) | Summary Statistics |\n"
            report_content += "|-------------|-----------|--------------------|--------------------|\n"

            for col in df.columns:
                all_columns.add(col)
                dtype = str(df[col].dtype)
                missing_pct = (df[col].isnull().sum() / len(df)) * 100

                # Summary statistics
                if pd.api.types.is_numeric_dtype(df[col]):
                    summary = f"min: {df[col].min():.2f}, max: {df[col].max():.2f}, mean: {df[col].mean():.2f}"
                else:
                    summary = f"unique: {df[col].nunique()}"

                report_content += f"| {col} | {dtype} | {missing_pct:.2f}% | {summary} |\n"

            report_content += "\n"
        except Exception as e:
            report_content += f"Error reading file: {e}\n\n"

    # Check for specific fields
    available_fields = []
    absent_fields = []

    # Specific fields requested to check
    # heatsink/module temperature, ambient temperature, THD, frequency deviation, reactive power, and IGBT/fault event labels

    if 'MODULE_TEMPERATURE' in all_columns:
        available_fields.append("MODULE_TEMPERATURE (heatsink/module temperature)")
    else:
        absent_fields.append("MODULE_TEMPERATURE (heatsink/module temperature)")

    if 'AMBIENT_TEMPERATURE' in all_columns:
        available_fields.append("AMBIENT_TEMPERATURE (ambient temperature)")
    else:
        absent_fields.append("AMBIENT_TEMPERATURE (ambient temperature)")

    # Checking other typically known columns or patterns
    if any('THD' in col.upper() for col in all_columns):
        available_fields.append("THD (Total Harmonic Distortion)")
    else:
        absent_fields.append("THD (Total Harmonic Distortion)")

    if any('FREQ' in col.upper() for col in all_columns):
        available_fields.append("Frequency deviation")
    else:
        absent_fields.append("Frequency deviation")

    if any('REACTIVE' in col.upper() for col in all_columns):
        available_fields.append("Reactive power")
    else:
        absent_fields.append("Reactive power")

    if any(any(k in col.upper() for k in ['IGBT', 'FAULT', 'EVENT', 'ALARM']) for col in all_columns):
        available_fields.append("IGBT/fault event labels")
    else:
        absent_fields.append("IGBT/fault event labels")

    report_content += "## Data Characteristics\n\n"
    report_content += "### Confirmed available fields\n"
    for field in available_fields:
        report_content += f"- {field}\n"
    if not available_fields:
        report_content += "- None\n"

    report_content += "\n### Confirmed absent fields\n"
    for field in absent_fields:
        report_content += f"- {field}\n"
    if not absent_fields:
        report_content += "- None\n"

    with open(report_path, "w") as f:
        f.write(report_content)

    print(f"Schema audit report written to {report_path}")

if __name__ == "__main__":
    audit_schema()
