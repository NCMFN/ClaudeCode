import os
import glob

downloads_md = "# Downloads\n\n## Figures\n\n"
for f in sorted(glob.glob("outputs/figures/*.png")):
    downloads_md += f"- [{os.path.basename(f)}]({f})\n"

downloads_md += "\n## Tables\n\n"
for t in sorted(glob.glob("outputs/tables/*.csv")):
    downloads_md += f"- [{os.path.basename(t)}]({t})\n"

with open("downloads.md", "w") as f:
    f.write(downloads_md)
