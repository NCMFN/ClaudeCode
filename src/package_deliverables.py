import os
import shutil
import hashlib
from datetime import datetime

def sha256_file(filepath):
    h = hashlib.sha256()
    try:
        with open(filepath, 'rb') as f:
            for chunk in iter(lambda: f.read(4096), b""):
                h.update(chunk)
        return h.hexdigest()
    except Exception:
        return "N/A"

def create_deliverables():
    if os.path.exists("deliverables"):
        shutil.rmtree("deliverables")

    os.makedirs("deliverables/figures", exist_ok=True)
    os.makedirs("deliverables/tables", exist_ok=True)
    os.makedirs("deliverables/paper", exist_ok=True)
    os.makedirs("deliverables/meta", exist_ok=True)

    # Copy files
    shutil.copy("outputs/figures/concept_methodology.pdf", "deliverables/figures/")
    shutil.copy("outputs/figures/concept_methodology.png", "deliverables/figures/")
    shutil.copy("outputs/figure_manifest.csv", "deliverables/meta/")
    shutil.copy("outputs/table_manifest.csv", "deliverables/meta/")
    shutil.copy("outputs/provenance.json", "deliverables/meta/")
    shutil.copy("STATUS.md", "deliverables/meta/")

    # Copy tables
    for filename in os.listdir("outputs/tables"):
        shutil.copy(f"outputs/tables/{filename}", "deliverables/tables/")

    # Create revision log
    with open("deliverables/meta/revision_log.md", "w") as f:
        f.write("# Revision Log\nRemoved all legacy synthetic-derived artifacts and text.\n")

    # Copy paper fragments
    for filename in os.listdir("paper_revision"):
        shutil.copy(f"paper_revision/{filename}", "deliverables/paper/")

    # Zip deliverables deterministically
    os.system("cd deliverables && find . -type f | sort | zip -X leakage_audit_bundle.zip -@")
    bundle_hash = sha256_file("deliverables/leakage_audit_bundle.zip")
    with open("deliverables/meta/bundle_sha256.txt", "w") as f:
        f.write(bundle_hash + "\n")

    with open("STATUS.md", "r") as f:
        status_line = f.readline().strip()

    try:
        commit_hash = os.popen("git rev-parse HEAD").read().strip()
    except Exception:
        commit_hash = "Unknown"

    # Create downloads.md
    with open("downloads.md", "w") as f:
        f.write(f"Status: {status_line}\n")
        f.write(f"Commit: {commit_hash}\n")
        f.write(f"Date: {datetime.now().isoformat()}\n\n")

        f.write("## Bundle\n")
        f.write("- [leakage_audit_bundle.zip](deliverables/leakage_audit_bundle.zip) - Complete deliverables package (CONCEPTUAL)\n\n")

        f.write("## Figures\n")
        f.write("- [concept_methodology.pdf](deliverables/figures/concept_methodology.pdf) - Conceptual methodology diagram (CONCEPTUAL)\n")
        f.write("- [concept_methodology.png](deliverables/figures/concept_methodology.png) - Conceptual methodology diagram (CONCEPTUAL)\n\n")

        f.write("## Tables\n")
        for filename in sorted(os.listdir("deliverables/tables")):
            f.write(f"- [{filename}](deliverables/tables/{filename}) - Protocol definition (CONCEPTUAL)\n")

        f.write("\n## Paper Fragments\n")
        for filename in sorted(os.listdir("deliverables/paper")):
            f.write(f"- [{filename}](deliverables/paper/{filename}) - LaTeX fragment (CONCEPTUAL)\n")

        f.write("\n## Metadata\n")
        f.write("- [STATUS.md](deliverables/meta/STATUS.md) - Pipeline status (CONCEPTUAL)\n")
        f.write("- [provenance.json](deliverables/meta/provenance.json) - Pipeline provenance (CONCEPTUAL)\n")
        f.write("- [figure_manifest.csv](deliverables/meta/figure_manifest.csv) - Figure manifest (CONCEPTUAL)\n")
        f.write("- [table_manifest.csv](deliverables/meta/table_manifest.csv) - Table manifest (CONCEPTUAL)\n")
        f.write("- [revision_log.md](deliverables/meta/revision_log.md) - Revision log (CONCEPTUAL)\n")
        f.write("- [bundle_sha256.txt](deliverables/meta/bundle_sha256.txt) - Bundle checksum (CONCEPTUAL)\n")

    print("\nFiles in deliverables/:")
    os.system("find deliverables/ -type f | sort")
    print("\nAll files are CONCEPTUAL based on the PROPOSED METHODOLOGY status.")

if __name__ == "__main__":
    create_deliverables()
