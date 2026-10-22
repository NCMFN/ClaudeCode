import os
import re
import csv
import shutil
import urllib.parse
from bs4 import BeautifulSoup

def slugify(text):
    if not text:
        return "figure"
    text = text.lower()
    text = re.sub(r'[^a-z0-9]+', '-', text)
    return text.strip('-')

def main():
    if not os.path.exists("downloads.md"):
        print("Error: downloads.md does not exist.")
        return

    with open("downloads.md", 'r', encoding='utf-8') as f:
        content = f.read()

    os.makedirs("outputs/figures", exist_ok=True)
    os.makedirs("outputs/tables", exist_ok=True)

    figures_found = []
    skipped_figures = []
    tables_found = []

    # Regex for ![alt](path)
    md_img_matches = re.finditer(r'!\[(.*?)\]\((.*?)\)', content)
    for match in md_img_matches:
        alt = match.group(1)
        path = match.group(2)
        figures_found.append({"alt": alt, "path": path})

    # Regex for <img>
    soup = BeautifulSoup(content, 'html.parser')
    for img in soup.find_all('img'):
        path = img.get('src')
        alt = img.get('alt', '')
        if path:
            figures_found.append({"alt": alt, "path": path})

    # Extract Markdown tables
    lines = content.split('\n')
    table_blocks = []
    current_block = []
    for line in lines:
        if line.strip().startswith('|') and line.strip().endswith('|'):
            current_block.append(line)
        else:
            if current_block:
                table_blocks.append(current_block)
                current_block = []
    if current_block:
        table_blocks.append(current_block)

    for block in table_blocks:
        parsed = []
        for i, line in enumerate(block):
            if i == 1 and re.match(r'^\|[\-\s\|:]+\|$', line.strip()):
                continue # skip markdown separator
            row = line.strip().strip('|').split('|')
            parsed.append([c.strip() for c in row])
        tables_found.append(parsed)

    # HTML tables
    for table in soup.find_all('table'):
        parsed = []
        for tr in table.find_all('tr'):
            row = [td.get_text(strip=True) for td in tr.find_all(['td', 'th'])]
            parsed.append(row)
        if parsed:
            tables_found.append(parsed)

    # Process figures
    extracted_figures = []
    for i, fig in enumerate(figures_found, 1):
        alt_slug = slugify(fig['alt'])
        if not alt_slug or alt_slug == '-':
            alt_slug = "figure"

        ext = os.path.splitext(fig['path'])[1]
        if not ext:
            ext = ".png"

        new_name = f"{i:02d}_{alt_slug}{ext}"
        dest_path = os.path.join("outputs/figures", new_name)

        src_path = urllib.parse.unquote(fig['path'])

        if os.path.exists(src_path):
            shutil.copy2(src_path, dest_path)
            extracted_figures.append(new_name)
        else:
            skipped_figures.append((fig['path'], "File not found"))

    # Process tables
    extracted_tables = []
    for i, tbl in enumerate(tables_found, 1):
        new_name = f"{i:02d}_table.csv"
        dest_path = os.path.join("outputs/tables", new_name)

        with open(dest_path, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerows(tbl)

        extracted_tables.append(new_name)

    print(f"Total figures extracted: {len(extracted_figures)}")
    for f in extracted_figures:
        print(f" - {f}")

    print(f"\nTotal tables extracted: {len(extracted_tables)}")
    for t in extracted_tables:
        print(f" - {t}")

    if skipped_figures:
        print(f"\nItems skipped:")
        for path, reason in skipped_figures:
            print(f" - {path}: {reason}")

    if len(extracted_figures) == 0 and len(extracted_tables) == 0:
        print("\ndownloads.md contains no figures or tables to extract.")

if __name__ == '__main__':
    main()
