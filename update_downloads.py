import os

figures_dir = 'deliverables/figures'
tables_dir = 'deliverables/tables'

figures = [f for f in os.listdir(figures_dir) if f.endswith('.png')]
tables = [f for f in os.listdir(tables_dir) if f.endswith('.csv')]

with open('downloads.md', 'w') as f:
    f.write("# Downloads\n\n")
    f.write("## Figures\n")
    for fig in sorted(figures):
        f.write(f"- [{fig}]({figures_dir}/{fig})\n")
    f.write("\n## Tables\n")
    for tab in sorted(tables):
        f.write(f"- [{tab}]({tables_dir}/{tab})\n")

    f.write("\n## Manifest\n")
    f.write(f"- [MANIFEST.md](deliverables/MANIFEST.md)\n")

    f.write("\n## Reports\n")
    f.write(f"- [schema_audit.md](reports/schema_audit.md)\n")
    f.write(f"- [label_construction.md](reports/label_construction.md)\n")
    f.write(f"- [limitations.md](reports/limitations.md)\n")
    f.write(f"- [telfor_draft_results_section.md](reports/telfor_draft_results_section.md)\n")
