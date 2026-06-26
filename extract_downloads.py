import re

def extract_downloads(file_path):
    with open(file_path, 'r') as f:
        content = f.read()

    images_section = re.search(r'## Images(.*?)## Notebooks', content, re.DOTALL)
    research_files_section = re.search(r'## Research Files(.*)', content, re.DOTALL)

    extracted_text = "Extracted Figures and Tables:\n\n"

    if images_section:
        extracted_text += "Images (Figures):\n"
        extracted_text += images_section.group(1).strip() + "\n\n"

    if research_files_section:
        extracted_text += "Research Files (Tables/CSV):\n"
        extracted_text += research_files_section.group(1).strip() + "\n"

    with open('extracted_downloads.txt', 'w') as f:
        f.write(extracted_text)

if __name__ == "__main__":
    extract_downloads('downloads.md')
