import re
import csv
import os

with open('/app/ventry/REPORT.md', 'r') as f:
    content = f.read()

manifest_entries = [["Asset_Type", "File_Name", "Title"]]

# Extract Tables
table_pattern = re.compile(r'\*\*Table (\d+\.\d+): (.*?)\*\*\n\n(.*?)(?=\n\n|\Z)', re.DOTALL)
for match in table_pattern.finditer(content):
    number = match.group(1).replace('.', '_')
    title = match.group(2)
    table_content = match.group(3).strip()

    file_name = f"table_{number}.csv"
    file_path = f"/app/outputs/tables/{file_name}"

    lines = table_content.split('\n')
    # skip the markdown separator line
    lines = [line for line in lines if not set(line.strip().replace('|', '').replace('-', '').replace(' ', '')) == set()]

    with open(file_path, 'w', newline='') as csvfile:
        writer = csv.writer(csvfile)
        for line in lines:
            row = [cell.strip() for cell in line.split('|')[1:-1]]
            if row:
                writer.writerow(row)

    manifest_entries.append(["Table", file_name, title])

# Extract Figures (diagrams/mockups)
figure_pattern = re.compile(r'\*\*Figure (\d+\.\d+): (.*?)\*\*\n\n```(.*?)\n(.*?)```', re.DOTALL)
for match in figure_pattern.finditer(content):
    number = match.group(1).replace('.', '_')
    title = match.group(2)
    lang = match.group(3)
    fig_content = match.group(4).strip()

    file_name = f"figure_{number}.txt"
    file_path = f"/app/outputs/figures/{file_name}"

    with open(file_path, 'w') as f:
        f.write(f"Title: {title}\n")
        f.write(f"Type: {lang}\n\n")
        f.write(fig_content)

    manifest_entries.append(["Figure", file_name, title])

# Write manifest
with open('/app/outputs/paper_assets/paper_assets_manifest.csv', 'w', newline='') as f:
    writer = csv.writer(f)
    writer.writerows(manifest_entries)

print("Artifact extraction complete.")
