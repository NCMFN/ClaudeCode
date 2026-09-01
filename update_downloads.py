import glob
import os
import re

with open('downloads.md', 'r') as f:
    original = f.read()

# Add all generated CSVs and PNGs back into downloads.md, replacing the current links
lines = original.split('\n')
figures_lines = []
tables_lines = []
for file in sorted(glob.glob('outputs/figures/*.png')):
    figures_lines.append(f'- [{os.path.basename(file)}]({file})')
for file in sorted(glob.glob('outputs/tables/*.csv')):
    tables_lines.append(f'- [{os.path.basename(file)}]({file})')

new_downloads_md = "# Downloads\n\n## Figures\n\n"
new_downloads_md += '\n'.join(figures_lines)
new_downloads_md += "\n\n## Tables\n\n"
new_downloads_md += '\n'.join(tables_lines)
new_downloads_md += "\n"

with open('downloads.md', 'w') as f:
    f.write(new_downloads_md)
