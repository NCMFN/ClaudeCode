import pytest
import numpy as np
from qiskit import QuantumCircuit
from qiskit.transpiler import PassManager
from qiskit.quantum_info import Operator
from qiskit_ibm_runtime.fake_provider import FakeSherbrooke

from coherence_safe_obfuscation.budget import calculate_latency_budget
from coherence_safe_obfuscation.obfuscation_pass import CoherenceSafeObfuscationPass

def test_budget_edge_cases():
    t1_times = {0: 100e-6, 1: 50e-6}

    # eta = 0
    assert calculate_latency_budget(t1_times, [0, 1], eta=0.0) == 0.0

    # T1 near zero
    assert calculate_latency_budget({0: 1e-9}, [0], eta=0.1) == 0.1 * 1e-9

    # Empty active qubits
    assert calculate_latency_budget(t1_times, [], eta=0.1) == 0.0

def test_operator_equivalence_and_constraints():
    # Construct a small Bell circuit
    qc = QuantumCircuit(2)
    qc.h(0)
    qc.cx(0, 1)

    backend = FakeSherbrooke()
    pm = PassManager([CoherenceSafeObfuscationPass(backend, eta=0.1)])

    obfuscated_qc = pm.run(qc)

    # Operator equivalence check
    op_original = Operator(qc)
    op_obfuscated = Operator(obfuscated_qc)

    # They should be equivalent up to global phase, Operator.equiv handles this usually
    assert op_original.equiv(op_obfuscated), "Operator equivalence failed."

    # Constraints check
    injected = pm.property_set['injected_latency']
    allowed = pm.property_set['allowed_latency']

    assert injected <= allowed, f"Injected latency {injected} exceeds budget {allowed}"

    print(f"Test passed: Injected latency {injected} <= Budget {allowed}")
