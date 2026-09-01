import re
import os
import shutil

with open("downloads.md", "r") as f:
    content = f.read()

# The prompt asks to extract ![alt](path) for figures and markdown tables for tables.
# But downloads.md currently only contains links [alt](path), not image tags ![alt](path),
# and no actual markdown tables `| ... |`.
# So I should update downloads.md to actually match the requested formats if they want to extract them,
# or simply output that they aren't there based on the instructions.

# Ah wait, the prompt specifically said:
# Parse `downloads.md` and extract every figure and table it contains into two new folders: `outputs/figures/` and `outputs/tables/`.
# Figures: ![alt](path) or <img>
# Tables: | ... | ... | or <table>
# If downloads.md contains no figures or no tables, state that explicitly.

# The current downloads.md only has `- [alt](path)` links. That's why the script found 0.
# I will run the script again and just capture the output to show the user.
