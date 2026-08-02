import pytest
from qiskit import QuantumCircuit
from qiskit.quantum_info import Operator
from qiskit.transpiler import PassManager

from coherence_safe_obfuscation.budget import calculate_obfuscation_budget
from coherence_safe_obfuscation.obfuscation_pass import CoherenceSafeObfuscation

def test_budget_edge_cases():
    cal_data = {
        0: {"t1_us": 10.0},
        1: {"t1_us": 0.001},
        2: {"t1_us": 100.0}
    }

    # Normal case
    budget = calculate_obfuscation_budget(cal_data, [0, 2], eta=0.1)
    assert budget == 1000.0  # 0.1 * 10 * 1000

    # T1 near zero
    budget = calculate_obfuscation_budget(cal_data, [1], eta=0.1)
    assert budget == 0.1  # 0.1 * 0.001 * 1000

    # eta = 0
    budget = calculate_obfuscation_budget(cal_data, [0], eta=0.0)
    assert budget == 0.0

    # negative eta
    budget = calculate_obfuscation_budget(cal_data, [0], eta=-0.1)
    assert budget == 0.0

    # Empty active qubits
    budget = calculate_obfuscation_budget(cal_data, [], eta=0.1)
    assert budget == 0.0

    # Missing calibration data for active qubit (falls back to default/infinity internally)
    # The logic sets default to inf, but effectively 0 if not found
    # Let's check:
    budget = calculate_obfuscation_budget(cal_data, [99], eta=0.1)
    assert budget == 0.0

def test_functional_equivalence():
    qc = QuantumCircuit(2)
    qc.h(0)
    qc.cx(0, 1)

    orig_op = Operator(qc)

    pm = PassManager(CoherenceSafeObfuscation(use_fake=True, eta=0.5))
    qc_obf = pm.run(qc)

    obf_op = Operator(qc_obf)

    assert orig_op.equiv(obf_op), "Obfuscated circuit is not functionally equivalent to the original."

def test_latency_constraint():
    qc = QuantumCircuit(2)
    qc.h(0)
    qc.cx(0, 1)

    pm = PassManager(CoherenceSafeObfuscation(use_fake=True, eta=0.1))
    pm.run(qc)

    props = pm.property_set
    budget = props.get('obfuscation_budget_ns', 0)
    added = props.get('obfuscation_added_latency_ns', 0)

    assert added <= budget, f"Added latency {added} exceeded budget {budget}"
