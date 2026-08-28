import os
import yaml

def test_config_yaml_exists():
    assert os.path.exists('config.yaml')
    with open('config.yaml', 'r') as f:
        config = yaml.safe_load(f)
    assert 'data' in config
    assert 'raw_dir' in config['data']

def test_schema_audit_output():
    assert os.path.exists('reports/schema_audit.md')
    with open('reports/schema_audit.md', 'r') as f:
        content = f.read()

    assert "MODULE_TEMPERATURE" in content
    assert "AMBIENT_TEMPERATURE" in content
    assert "Confirmed available fields" in content
    assert "Confirmed absent fields" in content
    assert "THD" in content
    assert "Frequency deviation" in content
    assert "Reactive power" in content
    assert "IGBT" in content
    assert "Row count" in content
