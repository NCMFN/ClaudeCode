import pytest
import tempfile
import os
import csv
from qiskit_ibm_runtime.fake_provider import FakeSherbrooke

from coherence_safe_obfuscation.calibration import (
    _extract_from_backend_object,
    fetch_calibration_from_csv,
    CalibrationData
)

def test_fetch_from_fake_backend():
    # Use FakeSherbrooke as requested in prompt
    backend = FakeSherbrooke()

    cal_data = _extract_from_backend_object(backend)

    assert isinstance(cal_data, CalibrationData)
    # FakeSherbrooke has 127 qubits
    assert len(cal_data.get_all_qubits()) == 127

    for q in range(5): # Just check a few to be fast
        props = cal_data.get_qubit_properties(q)
        assert "t1_us" in props
        assert "t2_us" in props
        assert "u2_ns" in props
        assert "u3_ns" in props
        assert "readout_error" in props
        assert "gate_fidelity" in props

        # Verify units and values are somewhat reasonable
        assert props["t1_us"] > 0
        assert props["t2_us"] > 0
        assert props["gate_fidelity"] <= 1.0

def test_fetch_from_csv():
    # Create a temporary CSV file
    fd, path = tempfile.mkstemp(suffix=".csv")
    try:
        with os.fdopen(fd, 'w', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(["qubit_index", "t1_us", "t2_us", "u2_ns", "u3_ns", "readout_error", "gate_fidelity"])
            writer.writerow([0, 100.5, 80.2, 35.5, 71.0, 0.02, 0.999])
            writer.writerow([1, 120.0, 95.0, 36.0, 72.0, 0.015, 0.998])

        cal_data = fetch_calibration_from_csv(path)

        assert isinstance(cal_data, CalibrationData)

        q0 = cal_data.get_qubit_properties(0)
        assert q0["t1_us"] == 100.5
        assert q0["t2_us"] == 80.2
        assert q0["u2_ns"] == 35.5
        assert q0["u3_ns"] == 71.0
        assert q0["readout_error"] == 0.02
        assert q0["gate_fidelity"] == 0.999

        q1 = cal_data.get_qubit_properties(1)
        assert q1["t1_us"] == 120.0
        assert q1["gate_fidelity"] == 0.998

        with pytest.raises(ValueError):
            cal_data.get_qubit_properties(2)

    finally:
        os.remove(path)

def test_fetch_csv_invalid_schema():
    fd, path = tempfile.mkstemp(suffix=".csv")
    try:
        with os.fdopen(fd, 'w', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(["qubit_index", "t1", "t2"]) # Wrong headers
            writer.writerow([0, 100.5, 80.2])

        with pytest.raises(ValueError, match="CSV must contain headers"):
            fetch_calibration_from_csv(path)
    finally:
        os.remove(path)
