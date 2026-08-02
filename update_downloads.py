import os

downloads_file = "downloads.md"

figures = os.listdir("src/outputs/figures")
tables = os.listdir("src/outputs/tables")

with open(downloads_file, "a") as f:
    f.write("\n## Generated Output Figures\n")
    for fig in figures:
        f.write(f"- [{fig}](./src/outputs/figures/{fig})\n")

    f.write("\n## Generated Output Tables\n")
    for tab in tables:
        f.write(f"- [{tab}](./src/outputs/tables/{tab})\n")

    f.write("\n## Generated Raw Data and Manifest\n")
    f.write("- [run_results.json](./src/outputs/raw/run_results.json)\n")
    f.write("- [local_calibration.csv](./src/outputs/raw/local_calibration.csv)\n")
    f.write("- [source_manifest.json](./src/outputs/source_manifest.json)\n")
