import csv
from typing import Dict, Any, Optional

class CalibrationData:
    """Stores calibration properties for qubits."""

    def __init__(self, data: Dict[int, Dict[str, float]]):
        self._data = data

    def get_qubit_properties(self, qubit: int) -> Dict[str, float]:
        """Get properties for a specific qubit."""
        if qubit not in self._data:
            raise ValueError(f"Qubit {qubit} not found in calibration data.")
        return self._data[qubit]

    def get_all_qubits(self) -> list[int]:
        """Get list of all qubit indices."""
        return list(self._data.keys())

def fetch_calibration_from_backend(backend_name: str, channel: str = "ibm_quantum") -> CalibrationData:
    """
    Fetch calibration data from a Qiskit backend by name via QiskitRuntimeService.

    Extracts t1, t2, u2/u3 gate durations, readout error, and gate fidelity.
    """
    from qiskit_ibm_runtime import QiskitRuntimeService

    # This might require credentials to be saved on the system or passed via env vars.
    service = QiskitRuntimeService(channel=channel)
    backend = service.backend(backend_name)

    return _extract_from_backend_object(backend)

def _extract_from_backend_object(backend) -> CalibrationData:
    data = {}

    if not hasattr(backend, "num_qubits"):
        raise ValueError("Backend does not have num_qubits attribute.")

    num_qubits = backend.num_qubits

    props = getattr(backend, "properties", lambda: None)()
    qubit_props = getattr(backend, "qubit_properties", lambda x: None)

    for q in range(num_qubits):
        q_data = {
            "t1_us": 0.0,
            "t2_us": 0.0,
            "u2_ns": 0.0,
            "u3_ns": 0.0,
            "readout_error": 0.0,
            "gate_fidelity": 1.0
        }

        # Try to get from qubit_properties (Target / V2 backend format)
        if callable(qubit_props):
            qp = None
            try:
                qp = qubit_props(q)
            except Exception:
                pass

            if qp is not None:
                if hasattr(qp, "t1") and qp.t1 is not None:
                    q_data["t1_us"] = qp.t1 * 1e6
                if hasattr(qp, "t2") and qp.t2 is not None:
                    q_data["t2_us"] = qp.t2 * 1e6

        # Try to get from properties (V1 backend format)
        if props is not None:
            try:
                if hasattr(props, "t1") and callable(props.t1):
                    q_data["t1_us"] = props.t1(q) * 1e6
                if hasattr(props, "t2") and callable(props.t2):
                    q_data["t2_us"] = props.t2(q) * 1e6
                if hasattr(props, "readout_error") and callable(props.readout_error):
                    q_data["readout_error"] = props.readout_error(q)

                # Gate info
                if hasattr(props, "gate_error") and callable(props.gate_error):
                    try:
                        err = props.gate_error("sx", [q]) # Often used as base for u2
                        q_data["gate_fidelity"] = 1.0 - err
                    except Exception:
                        pass

                if hasattr(props, "gate_length") and callable(props.gate_length):
                    try:
                        q_data["u2_ns"] = props.gate_length("sx", [q]) * 1e9
                        q_data["u3_ns"] = q_data["u2_ns"] * 2
                    except Exception:
                        pass
            except Exception:
                pass

        # Also check Target for gate durations (V2 backend format)
        if hasattr(backend, "target"):
            target = backend.target
            # Look for typical 1Q gates
            for gate_name in ["sx", "x", "rz", "u"]:
                if gate_name in target:
                    try:
                        instruction_props = target[gate_name].get((q,), None)
                        if instruction_props is not None:
                            if hasattr(instruction_props, "duration") and instruction_props.duration is not None:
                                # Standardize to u2/u3 equivalents
                                duration_ns = instruction_props.duration * 1e9
                                if gate_name in ["sx", "x"]:
                                    q_data["u2_ns"] = duration_ns
                                    q_data["u3_ns"] = duration_ns * 2
                            if hasattr(instruction_props, "error") and instruction_props.error is not None:
                                q_data["gate_fidelity"] = max(q_data["gate_fidelity"], 1.0 - instruction_props.error)
                    except Exception:
                        pass

            # Readout error from measure instruction
            if "measure" in target:
                try:
                    meas_props = target["measure"].get((q,), None)
                    if meas_props is not None and hasattr(meas_props, "error") and meas_props.error is not None:
                        q_data["readout_error"] = meas_props.error
                except Exception:
                    pass

        data[q] = q_data

    return CalibrationData(data)

def fetch_calibration_from_csv(filepath: str) -> CalibrationData:
    """
    Fetch calibration data from a local CSV file.
    Schema: qubit_index, t1_us, t2_us, u2_ns, u3_ns, readout_error, gate_fidelity
    """
    data = {}

    with open(filepath, mode='r') as file:
        reader = csv.DictReader(file)

        # Check schema
        expected_fields = {"qubit_index", "t1_us", "t2_us", "u2_ns", "u3_ns", "readout_error", "gate_fidelity"}
        if not expected_fields.issubset(set(reader.fieldnames or [])):
            raise ValueError(f"CSV must contain headers: {expected_fields}")

        for row in reader:
            qubit = int(row["qubit_index"])
            data[qubit] = {
                "t1_us": float(row["t1_us"]),
                "t2_us": float(row["t2_us"]),
                "u2_ns": float(row["u2_ns"]),
                "u3_ns": float(row["u3_ns"]),
                "readout_error": float(row["readout_error"]),
                "gate_fidelity": float(row["gate_fidelity"])
            }

    return CalibrationData(data)
