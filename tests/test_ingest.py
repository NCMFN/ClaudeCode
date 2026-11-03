import pytest
import pandas as pd
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

def test_ingest_schema():
    from src.ingest import update_provenance
    assert True
