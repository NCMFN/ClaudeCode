import os
import glob
import pandas as pd

def update_downloads():
    figures = sorted(glob.glob("outputs/figures/*.png"))
    tables = sorted(glob.glob("outputs/tables/*.csv"))

    with open("downloads.md", "w") as f:
        f.write("# Downloads\n\n")
        f.write("## Figures\n")
        for fig in figures:
            name = os.path.basename(fig)
            f.write(f"- [{name}](./{fig})\n")

        f.write("\n## Tables\n")
        for tab in tables:
            name = os.path.basename(tab)
            f.write(f"- [{name}](./{tab})\n")

update_downloads()
