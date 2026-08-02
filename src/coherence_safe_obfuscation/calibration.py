import csv
from typing import Dict, Any

def fetch_calibration_from_backend(backend) -> Dict[int, Dict[str, float]]:
    """
    Fetch calibration properties from a Qiskit backend.
    Uses backend.target properties.
    """
    target = backend.target
    cal_data = {}

    for q in range(target.num_qubits):
        q_data = {}

        props = target.qubit_properties[q]
        q_data['t1_us'] = getattr(props, 't1', 0.0) * 1e6  # convert seconds to us
        q_data['t2_us'] = getattr(props, 't2', 0.0) * 1e6

        # We need u2/u3 equivalents. Typically 'sx' is a good proxy for single qubit gate duration.
        # Check if 'sx' exists for this qubit.
        if 'sx' in target and (q,) in target['sx']:
            inst_props = target['sx'][(q,)]
            q_data['u2_ns'] = getattr(inst_props, 'duration', 0.0) * 1e9  # seconds to ns
            q_data['u3_ns'] = q_data['u2_ns'] * 2 # Approximating u3 as 2 * u2 duration
            error = getattr(inst_props, 'error', 0.0)
            q_data['gate_fidelity'] = 1.0 - error
        else:
            q_data['u2_ns'] = 0.0
            q_data['u3_ns'] = 0.0
            q_data['gate_fidelity'] = 1.0

        # Readout error. Typically 'measure' exists
        if 'measure' in target and (q,) in target['measure']:
            meas_props = target['measure'][(q,)]
            q_data['readout_error'] = getattr(meas_props, 'error', 0.0)
        else:
            q_data['readout_error'] = 0.0

        cal_data[q] = q_data

    return cal_data

def read_calibration_csv(filepath: str) -> Dict[int, Dict[str, float]]:
    """
    Read calibration data from a CSV file.
    Schema: qubit_index, t1_us, t2_us, u2_ns, u3_ns, readout_error, gate_fidelity
    """
    cal_data = {}
    with open(filepath, 'r') as f:
        reader = csv.DictReader(f)
        for row in reader:
            q = int(row['qubit_index'])
            cal_data[q] = {
                't1_us': float(row['t1_us']),
                't2_us': float(row['t2_us']),
                'u2_ns': float(row['u2_ns']),
                'u3_ns': float(row['u3_ns']),
                'readout_error': float(row['readout_error']),
                'gate_fidelity': float(row['gate_fidelity']),
            }
    return cal_data
