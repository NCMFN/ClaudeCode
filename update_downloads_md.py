import re

with open("downloads.md", "r") as f:
    content = f.read()

# Check if any link is missing "outputs/figures/" or "outputs/tables/"
links = re.findall(r'- \[(.*?)\]\((.*?)\)', content)
dirty = False

new_lines = []
for line in content.split('\n'):
    match = re.search(r'- \[(.*?)\]\((.*?)\)', line)
    if match:
        alt, path = match.groups()
        if 'outputs/figures' in path or 'outputs/tables' in path:
            new_lines.append(line)
        else:
            dirty = True
            if path.endswith('.png'):
                new_path = f"outputs/figures/{path}"
            elif path.endswith('.csv'):
                new_path = f"outputs/tables/{path}"
            else:
                new_path = path
            new_lines.append(f"- [{alt}]({new_path})")
    else:
        new_lines.append(line)

if dirty:
    with open("downloads.md", "w") as f:
        f.write('\n'.join(new_lines))
    print("Updated downloads.md")
else:
    print("downloads.md is already correct.")
