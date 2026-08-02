import sys
import os

# Add src to Python path for running the example directly
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src')))

from qiskit import QuantumCircuit
from qiskit.transpiler import PassManager
from qiskit_ibm_runtime.fake_provider import FakeSherbrooke

from coherence_safe_obfuscation.calibration import _extract_from_backend_object
from coherence_safe_obfuscation.obfuscation_pass import CoherenceSafeObfuscation

def main():
    print("--- Coherence-Safe Obfuscation Demo ---")

    # 1. Setup target backend
    print("\n1. Setting up Fake Backend (FakeSherbrooke)")
    backend = FakeSherbrooke()

    # 2. Fetch calibration
    print("2. Fetching calibration data from backend")
    # For demo without credentials we use the internal extractor on the fake backend
    cal_data = _extract_from_backend_object(backend)

    for q in range(2):
        props = cal_data.get_qubit_properties(q)
        print(f"   - Qubit {q}: T1 = {props['t1_us']:.2f} us, u3_duration = {props['u3_ns']:.2f} ns")

    # 3. Create small VQE-style ansatz circuit
    print("\n3. Creating target circuit")
    qc = QuantumCircuit(2)
    qc.rx(1.57, 0)
    qc.ry(1.57, 1)
    qc.cx(0, 1)
    qc.rz(0.5, 0)
    qc.cx(0, 1)

    print("Original circuit depth:", qc.depth())
    print("Original gate count:", sum(qc.count_ops().values()))

    # 4. Integrate pass via PassManager
    print("\n4. Running Obfuscation Pass (eta=0.1)")
    pass_ = CoherenceSafeObfuscation(cal_data, eta=0.1)
    pm = PassManager([pass_])

    obfuscated_qc = pm.run(qc)

    # 5. Output results
    print("\n5. Results")
    print("Obfuscated circuit depth:", obfuscated_qc.depth())
    print("Obfuscated gate count:", sum(obfuscated_qc.count_ops().values()))

    prop_set = pm.property_set
    print(f"Native Latency (ns): {prop_set.get('native_latency_ns', 0):.2f}")
    print(f"Added Latency (ns): {prop_set.get('obfuscated_latency_added_ns', 0):.2f}")
    print(f"Dummy Pairs Injected: {prop_set.get('obfuscated_dummy_pairs', 0)}")
    print(f"Security Confidence (0 to 1): {prop_set.get('security_confidence', 0):.2f}")

    print("\nDone!")

if __name__ == "__main__":
    main()
