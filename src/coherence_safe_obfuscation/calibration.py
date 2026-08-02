import csv
import json
import os
from typing import Dict, Any, Optional

def fetch_calibration_data(
    backend_name: Optional[str] = None,
    fallback_csv: str = "src/outputs/raw/local_calibration.csv",
    use_fake: bool = False
) -> Dict[int, Dict[str, float]]:
    """
    Fetches per-qubit calibration data: T1, T2, u2_ns, u3_ns, readout_error, gate_fidelity.

    If use_fake is True, attempts to use FakeSherbrooke.
    If backend_name is provided, attempts to fetch from QiskitRuntimeService.
    If all fails or neither is provided, attempts to load from the fallback_csv.
    """
    if use_fake:
        try:
            from qiskit_ibm_runtime.fake_provider import FakeSherbrooke
            backend = FakeSherbrooke()
            return _extract_from_backend(backend)
        except ImportError:
            pass # fallback to csv if fake provider fails

    if backend_name:
        try:
            from qiskit_ibm_runtime import QiskitRuntimeService
            service = QiskitRuntimeService()
            backend = service.backend(backend_name)
            return _extract_from_backend(backend)
        except Exception as e:
            print(f"Failed to fetch from QiskitRuntimeService: {e}")

    return _load_from_csv(fallback_csv)

def _extract_from_backend(backend) -> Dict[int, Dict[str, float]]:
    """Extracts required metrics from a Qiskit backend."""
    # Qiskit 2.0 backend.target contains instruction properties
    target = backend.target
    num_qubits = target.num_qubits

    data = {}
    for q in range(num_qubits):
        q_props = target.qubit_properties
        # properties might be None if not fully characterized
        if q_props and q < len(q_props) and q_props[q]:
            t1 = q_props[q].t1
            t2 = q_props[q].t2
        else:
            t1 = 0.0
            t2 = 0.0

        # getting gate durations and fidelities
        # usually u2 (or sx) and u3 (or x)
        # Assuming typical basis gates: 'sx', 'x', 'rz', 'id'
        # Convert to ns

        u2_dur = 0.0
        u3_dur = 0.0
        gate_fid = 1.0

        # Check for 'sx' (like u2) and 'x' (like u3)
        if 'sx' in target and (q,) in target['sx']:
            sx_props = target['sx'][(q,)]
            u2_dur = sx_props.duration * 1e9 if sx_props and sx_props.duration else 0.0
            gate_fid = 1.0 - (sx_props.error if sx_props and sx_props.error else 0.0)

        if 'x' in target and (q,) in target['x']:
            x_props = target['x'][(q,)]
            u3_dur = x_props.duration * 1e9 if x_props and x_props.duration else 0.0

        # readout error
        readout_error = 0.0
        if 'measure' in target and (q,) in target['measure']:
            meas_props = target['measure'][(q,)]
            readout_error = meas_props.error if meas_props and meas_props.error else 0.0

        # convert T1/T2 to us
        data[q] = {
            "t1_us": t1 * 1e6,
            "t2_us": t2 * 1e6,
            "u2_ns": u2_dur,
            "u3_ns": u3_dur,
            "readout_error": readout_error,
            "gate_fidelity": gate_fid
        }
    return data

def _load_from_csv(csv_path: str) -> Dict[int, Dict[str, float]]:
    """Loads calibration data from a CSV file."""
    if not os.path.exists(csv_path):
        raise FileNotFoundError(f"Fallback CSV {csv_path} not found.")

    data = {}
    with open(csv_path, mode='r') as f:
        reader = csv.DictReader(f)
        for row in reader:
            q = int(row['qubit_index'])
            data[q] = {
                "t1_us": float(row['t1_us']),
                "t2_us": float(row['t2_us']),
                "u2_ns": float(row['u2_ns']),
                "u3_ns": float(row['u3_ns']),
                "readout_error": float(row['readout_error']),
                "gate_fidelity": float(row['gate_fidelity'])
            }
    return data
