import json
import time
from qiskit import QuantumCircuit
from qiskit.transpiler import PassManager
from qiskit.circuit.library import QFT, RealAmplitudes
from coherence_safe_obfuscation.obfuscation_pass import CoherenceSafeObfuscation
import sys

def main():
    print("Starting Obfuscation Demo...")

    circuits = {}

    # Circuit 1: GHZ
    qc_ghz = QuantumCircuit(3)
    qc_ghz.h(0)
    qc_ghz.cx(0, 1)
    qc_ghz.cx(1, 2)
    circuits["ghz"] = qc_ghz

    # Circuit 2: QFT-style
    qc_qft = QFT(num_qubits=4)
    circuits["qft"] = qc_qft

    # Circuit 3: RealAmplitudes (VQE-style)
    qc_vqe = RealAmplitudes(num_qubits=4, reps=2)
    circuits["vqe"] = qc_vqe

    results = {}

    pass_manager = PassManager()
    obfuscation_pass = CoherenceSafeObfuscation(use_fake=True, eta=0.1)
    pass_manager.append(obfuscation_pass)

    pass_manager_stage_timing = []

    for name, qc in circuits.items():
        print(f"Transpiling {name} circuit...")

        start_time = time.time()
        # Qiskit PassManager run
        qc_obf = pass_manager.run(qc)
        end_time = time.time()

        timing = end_time - start_time
        pass_manager_stage_timing.append({"circuit": name, "stage": "obfuscation", "time_s": timing})

        props = pass_manager.property_set

        original_depth = qc.depth()
        obfuscated_depth = qc_obf.depth()

        results[name] = {
            "circuit": name,
            "original_gate_count": props.get('obfuscation_original_gates', 0),
            "obfuscated_gate_count": props.get('obfuscation_final_gates', 0),
            "added_latency_ns": props.get('obfuscation_added_latency_ns', 0.0),
            "budget_ns": props.get('obfuscation_budget_ns', 0.0),
            "security_confidence": props.get('obfuscation_security_confidence', 0.0),
            "original_depth": original_depth,
            "obfuscated_depth": obfuscated_depth,
            "qubit_count": qc.num_qubits,
            "gate_types": list(set([instr.operation.name for instr in qc.data]))
        }

    # Also save the calibration data used
    cal_data = obfuscation_pass.calibration_data

    output = {
        "run_results": results,
        "calibration_used": cal_data,
        "pass_manager_stage_timing": pass_manager_stage_timing,
        "config_constants": {
            "eta": 0.1,
            "dummy_gate_name": "id",
            "backend": "FakeSherbrooke"
        }
    }

    output_path = "src/outputs/raw/run_results.json"
    with open(output_path, "w") as f:
        json.dump(output, f, indent=4)

    print(f"Saved results to {output_path}")

if __name__ == "__main__":
    main()
