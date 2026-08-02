import pytest
from qiskit import QuantumCircuit
from qiskit.converters import circuit_to_dag, dag_to_circuit
from qiskit.quantum_info import Operator
from coherence_safe_obfuscation.calibration import CalibrationData
from coherence_safe_obfuscation.obfuscation_pass import CoherenceSafeObfuscation

@pytest.fixture
def dummy_calibration():
    # Provide simple calibration data
    # qubit_index: t1_us, t2_us, u2_ns, u3_ns, readout_error, gate_fidelity
    data = {
        0: {"t1_us": 100.0, "t2_us": 100.0, "u2_ns": 50.0, "u3_ns": 100.0, "readout_error": 0.01, "gate_fidelity": 0.99},
        1: {"t1_us": 80.0, "t2_us": 80.0, "u2_ns": 50.0, "u3_ns": 100.0, "readout_error": 0.01, "gate_fidelity": 0.99},
    }
    return CalibrationData(data)

def test_obfuscation_equivalence(dummy_calibration):
    # Original circuit
    qc = QuantumCircuit(2)
    qc.h(0)
    qc.cx(0, 1)

    orig_op = Operator(qc)

    # Run pass
    # min T1 is 80us. eta=0.1 -> budget = 8000ns
    # u3_ns is 100ns -> pair duration = 200ns
    # We should be able to inject several pairs
    pass_ = CoherenceSafeObfuscation(dummy_calibration, eta=0.1)
    dag = circuit_to_dag(qc)
    new_dag = pass_.run(dag)
    new_qc = dag_to_circuit(new_dag)

    new_op = Operator(new_qc)

    # Obfuscated circuit should be logically equivalent
    assert orig_op.equiv(new_op)

    # Check that dummy pairs were added
    assert pass_.property_set["obfuscated_dummy_pairs"] > 0
    assert pass_.property_set["obfuscated_latency_added_ns"] <= 8000.0
    assert 0.0 < pass_.property_set["security_confidence"] <= 1.0

def test_obfuscation_zero_budget(dummy_calibration):
    qc = QuantumCircuit(2)
    qc.h(0)
    qc.cx(0, 1)

    # eta = 0.0 means 0 budget, no pairs injected
    pass_ = CoherenceSafeObfuscation(dummy_calibration, eta=0.0)
    dag = circuit_to_dag(qc)
    new_dag = pass_.run(dag)

    assert pass_.property_set["obfuscated_dummy_pairs"] == 0
    assert pass_.property_set["security_confidence"] == 0.0

def test_obfuscation_stops_at_budget(dummy_calibration):
    # Make a very long circuit
    qc = QuantumCircuit(1)
    for _ in range(100):
        qc.x(0)

    # min T1 is 100us. eta=0.01 -> budget = 1000ns
    # pair duration = 200ns -> we can fit exactly 5 pairs
    pass_ = CoherenceSafeObfuscation(dummy_calibration, eta=0.01)
    dag = circuit_to_dag(qc)
    pass_.run(dag)

    assert pass_.property_set["obfuscated_dummy_pairs"] == 5
    assert pass_.property_set["obfuscated_latency_added_ns"] == 1000.0
