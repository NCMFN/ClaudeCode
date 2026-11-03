import os
import sys
import shutil
import zipfile
import hashlib

def get_hash(filepath):
    h = hashlib.sha256()
    with open(filepath, "rb") as f:
        while chunk := f.read(8192):
            h.update(chunk)
    return h.hexdigest()

def package():
    deliverables = "deliverables"
    # we don't rmtree deliverables entirely to avoid removing all_tables.xlsx if we placed it there, but for safety
    if os.path.exists(deliverables):
        shutil.rmtree(deliverables)
    os.makedirs(f"{deliverables}/figures", exist_ok=True)
    os.makedirs(f"{deliverables}/tables", exist_ok=True)
    os.makedirs(f"{deliverables}/paper", exist_ok=True)
    os.makedirs(f"{deliverables}/meta", exist_ok=True)
    os.makedirs(f"{deliverables}/plans", exist_ok=True)

    if os.path.exists("outputs/figures"):
        for f in os.listdir("outputs/figures"):
            shutil.copy(os.path.join("outputs/figures", f), f"{deliverables}/figures/{f}")

    if os.path.exists("outputs/tables"):
        for f in os.listdir("outputs/tables"):
            shutil.copy(os.path.join("outputs/tables", f), f"{deliverables}/tables/{f}")

    if os.path.exists("paper_revision"):
        for f in os.listdir("paper_revision"):
            shutil.copy(os.path.join("paper_revision", f), f"{deliverables}/paper/{f}")

    if os.path.exists("outputs/plans"):
        for f in os.listdir("outputs/plans"):
            shutil.copy(os.path.join("outputs/plans", f), f"{deliverables}/plans/{f}")

    for m in ["STATUS.md", "outputs/provenance.json", "outputs/run_state.json", "outputs/figure_manifest.csv", "outputs/table_manifest.csv"]:
        if os.path.exists(m):
            shutil.copy(m, f"{deliverables}/meta/{os.path.basename(m)}")

    if os.path.exists("all_tables.xlsx"):
        shutil.copy("all_tables.xlsx", f"{deliverables}/all_tables.xlsx")

    with zipfile.ZipFile(f"{deliverables}/leakage_audit_bundle.zip", 'w', zipfile.ZIP_DEFLATED) as zf:
        for root, _, files in sorted(os.walk(deliverables)):
            for file in sorted(files):
                if file == "leakage_audit_bundle.zip": continue
                filepath = os.path.join(root, file)
                zf.write(filepath, os.path.relpath(filepath, deliverables))

    h = get_hash(f"{deliverables}/leakage_audit_bundle.zip")
    with open(f"{deliverables}/meta/bundle_sha256.txt", "w") as f:
        f.write(h)

    print("Package built successfully.")

if __name__ == "__main__":
    package()
