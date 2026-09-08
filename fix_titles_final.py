with open('run_pipeline.py', 'r') as f:
    lines = f.readlines()

new_lines = []
for line in lines:
    if "set_title" in line or "plt.title" in line or "suptitle" in line:
        if "Source: WSN_Dataset" not in line:
            # Reconstruct string by manually appending
            # E.g. ax.set_title('Figure 1: Feature Completeness per Source Dataset')
            # Split by quote.
            parts = line.split("'")
            if len(parts) >= 3: # at least two quotes
                # The actual string is in parts[1] (assuming single quotes used for string)
                # If there are multiple quotes like in f-strings: f'outputs/figures/Figure_{38+i}_shap_dep_{feature}.png'
                # But wait, titles don't have multiple quotes inside them usually except f-strings which we don't have quotes inside.
                parts[-2] = parts[-2] + ". Source: WSN_Dataset"
                line = "'".join(parts)

    new_lines.append(line)

with open('run_pipeline.py', 'w') as f:
    f.writelines(new_lines)
