import pytest
import gzip
import os
import sys
sys.path.append('src')
from acquire import validate_redteam

def test_redteam_parser_schema():
    with gzip.open('tests/fixtures/test_redteam.txt.gz', 'wt') as f:
        f.write("100,U1@DOM1,C1,C2\n")
        f.write("invalid_time,U2,C1,C2\n")

    valid, reason = validate_redteam('tests/fixtures/test_redteam.txt.gz')
    assert not valid
    assert "Invalid time format" in reason
