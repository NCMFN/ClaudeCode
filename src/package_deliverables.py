import os
import shutil
import zipfile
import hashlib
import glob
import pandas as pd
import json

def generate_latex_table(csv_path, tex_path):
    df = pd.read_csv(csv_path)
    # Basic booktabs style conversion
    latex_str = df.to_latex(index=False, escape=True)
    # Very rudimentary insert of booktabs rules if standard to_latex output didn't do it
    # pandas 2+ uses stiler by default but df.to_latex might use tabular
    if 'toprule' not in latex_str:
        latex_str = latex_str.replace('\\hline', '\\toprule', 1)
        latex_str = latex_str.replace('\\hline', '\\bottomrule')
    with open(tex_path, 'w') as f:
        f.write(latex_str)

def get_file_sha256(filepath):
    sha256_hash = hashlib.sha256()
    with open(filepath, "rb") as f:
        for byte_block in iter(lambda: f.read(4096), b""):
            sha256_hash.update(byte_block)
    return sha256_hash.hexdigest()

def package():
    # 1. Clean up
    if os.path.exists('deliverables'):
        shutil.rmtree('deliverables')

    os.makedirs('deliverables/figures', exist_ok=True)
    os.makedirs('deliverables/tables', exist_ok=True)
    os.makedirs('deliverables/paper', exist_ok=True)
    os.makedirs('deliverables/meta', exist_ok=True)

    with open('STATUS.md', 'r') as f:
        status_content = f.read()

    is_proposed = "PROPOSED METHODOLOGY" in status_content
    is_partial = "PARTIAL" in status_content
    status_label = "PROPOSED METHODOLOGY" if is_proposed else ("PARTIAL" if is_partial else "COMPLETED")

    # Check what passed linting
    # Actually figure linting manifest is outputs/figure_manifest.csv
    valid_figures = set()
    manifest_figures = {}
    if os.path.exists('outputs/figure_manifest.csv'):
        df_figs = pd.read_csv('outputs/figure_manifest.csv')
        for _, row in df_figs.iterrows():
            fname = row['filename']
            ftype = row['type']
            valid_figures.add(fname)
            manifest_figures[fname] = ftype

    # Process tables
    table_manifest = []
    for t_path in glob.glob('outputs/tables/*.csv'):
        t_name = os.path.basename(t_path)
        if "TEST_FIXTURE" in t_name: continue

        # In PROPOSED mode, we only allow config/protocol tables, no result tables.
        # redteam_unmatched is a methodology artifact, we allow it.
        # evaluation_results is a result table.
        if is_proposed and "evaluation_results" in t_name:
            continue

        dest_csv = os.path.join('deliverables/tables', t_name)
        shutil.copy(t_path, dest_csv)

        dest_tex = os.path.join('deliverables/tables', t_name.replace('.csv', '.tex'))
        try:
            generate_latex_table(t_path, dest_tex)
        except:
            pass # skip if bad csv format

        df = pd.read_csv(t_path)
        table_manifest.append({
            'filename': t_name,
            'description': f"Data table {t_name}",
            'source_script': 'pipeline',
            'source_data_hash': get_file_sha256(t_path),
            'status_at_generation': status_label,
            'n_rows': len(df)
        })

    df_tm = pd.DataFrame(table_manifest)
    df_tm.to_csv('outputs/table_manifest.csv', index=False)
    if not df_tm.empty:
        shutil.copy('outputs/table_manifest.csv', 'deliverables/meta/table_manifest.csv')

    # Process figures
    for f_path in glob.glob('outputs/figures/*.*'):
        f_name = os.path.basename(f_path)
        if "TEST_FIXTURE" in f_name: continue
        if f_name not in valid_figures: continue

        f_type = manifest_figures.get(f_name, 'MEASURED')
        if is_proposed and f_type != 'CONCEPTUAL':
            continue # Only allow conceptual figures in proposed mode

        shutil.copy(f_path, os.path.join('deliverables/figures', f_name))

    if os.path.exists('outputs/figure_manifest.csv'):
        shutil.copy('outputs/figure_manifest.csv', 'deliverables/meta/figure_manifest.csv')

    # Copy paper fragments
    for p_path in glob.glob('paper_revision/*.*'):
        shutil.copy(p_path, os.path.join('deliverables/paper', os.path.basename(p_path)))

    # Copy meta
    if os.path.exists('outputs/provenance.json'):
        shutil.copy('outputs/provenance.json', 'deliverables/meta/provenance.json')
    if os.path.exists('outputs/revision_log.md'):
        shutil.copy('outputs/revision_log.md', 'deliverables/meta/revision_log.md')
    shutil.copy('STATUS.md', 'deliverables/meta/STATUS.md')

    # Build Zip Deterministically
    zip_path = 'deliverables/leakage_audit_bundle.zip'
    with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
        # Sort files for determinism
        all_files = []
        for root, dirs, files in os.walk('deliverables'):
            if zip_path in root: continue
            for file in files:
                full_path = os.path.join(root, file)
                if full_path == zip_path: continue
                all_files.append(full_path)

        all_files.sort()
        for f in all_files:
            arcname = os.path.relpath(f, 'deliverables')
            zipf.write(f, arcname)

    sha = get_file_sha256(zip_path)
    with open('deliverables/meta/bundle_sha256.txt', 'w') as f:
        f.write(sha)

    # Regenerate downloads.md
    with open('downloads.md', 'w') as f:
        f.write(f"{status_label}\n")

        # Try to get git hash
        import subprocess
        try:
            commit_hash = subprocess.check_output(['git', 'rev-parse', 'HEAD']).decode().strip()
        except:
            commit_hash = "unknown"

        f.write(f"Commit: {commit_hash} | Date: {pd.Timestamp.now().strftime('%Y-%m-%d')}\n\n")
        f.write("# Downloads\n\n")

        f.write("## Bundle\n")
        size = os.path.getsize(zip_path)
        f.write(f"- [leakage_audit_bundle.zip](deliverables/leakage_audit_bundle.zip) - Complete deliverables archive - {size} bytes\n\n")

        f.write("## Figures\n")
        for p in sorted(glob.glob('deliverables/figures/*.*')):
            name = os.path.basename(p)
            size = os.path.getsize(p)
            ft = manifest_figures.get(name, 'UNKNOWN')
            f.write(f"- [{name}](deliverables/figures/{name}) - Figure - {ft} - {size} bytes\n")

        f.write("\n## Tables\n")
        for p in sorted(glob.glob('deliverables/tables/*.*')):
            name = os.path.basename(p)
            size = os.path.getsize(p)
            f.write(f"- [{name}](deliverables/tables/{name}) - Table - {size} bytes\n")

        f.write("\n## Paper Fragments\n")
        for p in sorted(glob.glob('deliverables/paper/*.*')):
            name = os.path.basename(p)
            size = os.path.getsize(p)
            f.write(f"- [{name}](deliverables/paper/{name}) - Paper fragment - {size} bytes\n")

        f.write("\n## Metadata\n")
        for p in sorted(glob.glob('deliverables/meta/*.*')):
            name = os.path.basename(p)
            size = os.path.getsize(p)
            f.write(f"- [{name}](deliverables/meta/{name}) - Metadata - {size} bytes\n")

if __name__ == '__main__':
    package()
