import os
import glob

def get_markdown_link(filepath):
    filename = os.path.basename(filepath)
    return f"- **{filename}**\n  - Download Link: [Download {filename}]({filepath})\n"

def main():
    with open("downloads.md", "w") as f:
        f.write("# Downloads\n\n")
        f.write("## Tables\n")
        for file in glob.glob("outputs/tables/*"):
            if os.path.isfile(file):
                f.write(get_markdown_link(file))

        f.write("\n## Figures\n")
        for file in glob.glob("outputs/figures/*"):
            if os.path.isfile(file):
                f.write(get_markdown_link(file))

        f.write("\n## Paper Assets\n")
        for file in glob.glob("outputs/paper_assets/*"):
            if os.path.isfile(file):
                f.write(get_markdown_link(file))

if __name__ == "__main__":
    main()
