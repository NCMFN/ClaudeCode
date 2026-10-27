import os
import pytest
from src.ingest import check_lanl_local

def test_missing_files_yields_proposed(tmp_path):
    # Pass an empty temp dir as local data dir
    can_access, file_info = check_lanl_local(str(tmp_path))
    assert not can_access
    assert file_info["auth.txt.gz"]["size"] == "N/A"

def test_schema_validator_rejects_malformed(tmp_path):
    import gzip
    bad_auth = tmp_path / "auth.txt.gz"
    with gzip.open(bad_auth, 'wt') as f:
        f.write("1,user@dom,comp1,comp2,Auth,Logon,Orient\n") # Only 7 fields instead of 9

    from src.ingest import validate_file
    assert not validate_file(str(bad_auth), 9)
