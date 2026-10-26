import pytest
import os
import glob

def test_no_forbidden_strings_in_deliverables():
    # Only test what's explicitly asked
    forbidden = ["illustrative", "schematic - not measured", "placeholder", "dummy"]
    # We ignore the allowed files from earlier tests
    for root, dirs, files in os.walk('deliverables'):
        for f in files:
            if f.endswith('.md') or f.endswith('.tex'):
                if f == 'CHANGES.md' or f == 'revision_log.md': continue
                with open(os.path.join(root, f), 'r') as file:
                    content = file.read().lower()
                    for w in forbidden:
                        assert w not in content, f"Forbidden word {w} in {f}"

def test_downloads_md_links():
    if not os.path.exists('downloads.md'):
        return
    with open('downloads.md', 'r') as f:
        content = f.read()

    # Extract links formatted like (deliverables/...)
    import re
    links = re.findall(r'\((deliverables/[^\)]+)\)', content)
    for link in links:
        assert os.path.exists(link), f"Link {link} in downloads.md does not exist"

def test_proposed_status_filters():
    if not os.path.exists('STATUS.md'):
        return
    with open('STATUS.md', 'r') as f:
        status = f.read()

    if "PROPOSED METHODOLOGY" in status:
        # Check no result tables
        tables = glob.glob('deliverables/tables/*.csv')
        for t in tables:
            assert "evaluation_results" not in t

        # Check only conceptual figures
        figs = glob.glob('deliverables/figures/*.*')
        for f in figs:
            assert "concept" in f
