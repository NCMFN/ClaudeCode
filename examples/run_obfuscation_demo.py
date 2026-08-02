import json
import csv
import time
import os
from qiskit import QuantumCircuit
from qiskit.transpiler import PassManager
from qiskit.circuit.library import TwoLocal, QFT
from qiskit_ibm_runtime.fake_provider import FakeSherbrooke
from qiskit.transpiler.passes import BasisTranslator, UnrollCustomDefinitions
from qiskit.circuit.equivalence_library import SessionEquivalenceLibrary as sel

from coherence_safe_obfuscation.obfuscation_pass import CoherenceSafeObfuscationPass
from coherence_safe_obfuscation.calibration import fetch_calibration_from_backend

def create_circuits():
    # 1. Bell
    bell = QuantumCircuit(2)
    bell.h(0)
    bell.cx(0, 1)
    bell.name = "bell"

    # 2. VQE-style (decompose to allow mapping)
    vqe = TwoLocal(3, 'ry', 'cz', reps=2, entanglement='linear')
    vqe.name = "vqe_ansatz"

    # 3. QFT (decompose)
    qft = QFT(4)
    qft.name = "qft"

    return [bell, vqe, qft]

def run():
    backend = FakeSherbrooke()
    target = backend.target
    circuits = create_circuits()

    # Export calibration data
    cal_data = fetch_calibration_from_backend(backend)

    os.makedirs('/app/src/outputs/raw', exist_ok=True)
    with open('/app/src/outputs/raw/calibration.csv', 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(['qubit_index', 't1_us', 't2_us', 'u2_ns', 'u3_ns', 'readout_error', 'gate_fidelity'])
        for q, data in cal_data.items():
            writer.writerow([q, data['t1_us'], data['t2_us'], data['u2_ns'], data['u3_ns'], data['readout_error'], data['gate_fidelity']])

    run_results = []

    # Setup translator for original gate count
    basis_gates = list(target.operation_names)
    translator = PassManager([
        UnrollCustomDefinitions(sel, basis_gates),
        BasisTranslator(sel, basis_gates)
    ])

    for qc in circuits:
        # Pre-translate original to basis for fair comparison
        # QFT and TwoLocal are custom gates initially, so we decompose them first.
        qc = qc.decompose()

        original_translated = translator.run(qc)
        orig_depth = original_translated.depth()
        orig_count = sum(original_translated.count_ops().values())

        # Apply Obfuscation
        start_time = time.time()
        pass_instance = CoherenceSafeObfuscationPass(backend, eta=0.1)
        pm = PassManager([UnrollCustomDefinitions(sel, basis_gates), pass_instance])
        obfuscated_qc = pm.run(qc)
        end_time = time.time()

        obf_depth = obfuscated_qc.depth()
        obf_count = sum(obfuscated_qc.count_ops().values())

        run_results.append({
            "circuit_name": qc.name,
            "backend": "FakeSherbrooke",
            "qubits": qc.num_qubits,
            "original_gate_count": orig_count,
            "obfuscated_gate_count": obf_count,
            "original_depth": orig_depth,
            "obfuscated_depth": obf_depth,
            "allowed_latency": pm.property_set['allowed_latency'],
            "injected_latency": pm.property_set['injected_latency'],
            "injected_pairs": pm.property_set['injected_pairs'],
            "security_confidence": pm.property_set['security_confidence'],
            "pass_wall_clock_time": end_time - start_time,
            "original_ops": dict(original_translated.count_ops())
        })

    with open('/app/src/outputs/raw/run_results.json', 'w') as f:
        json.dump(run_results, f, indent=4)

    print("Demo completed successfully. Raw results saved.")

if __name__ == "__main__":
    run()
