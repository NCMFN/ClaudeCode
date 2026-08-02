import numpy as np
from qiskit.transpiler.basepasses import TransformationPass
from qiskit.dagcircuit import DAGCircuit
from qiskit.circuit.library import IGate
from qiskit.circuit import Qubit, Instruction

from .calibration import fetch_calibration_data
from .budget import calculate_obfuscation_budget

class CoherenceSafeObfuscation(TransformationPass):
    """
    A transpiler pass that adds U U^dagger pairs to obfuscate a quantum circuit
    without exceeding the coherence budget of the active qubits.
    """

    def __init__(
        self,
        backend_name=None,
        fallback_csv="src/outputs/raw/local_calibration.csv",
        use_fake=False,
        eta=0.1,
        dummy_gate_name='id'
    ):
        super().__init__()
        self.backend_name = backend_name
        self.fallback_csv = fallback_csv
        self.use_fake = use_fake
        self.eta = eta

        # Determine dummy gate
        # For true obfuscation, usually we inject U U^dagger.
        # We will use Identity (IGate) or a combination of RZ(pi) RZ(-pi).
        # We'll use IGate pairs for simplicity and low impact, assuming it adds some duration if not optimized out.
        # In a real hardware context, a dynamic decoupling sequence or active identity is used.
        self.dummy_gate_name = dummy_gate_name

        # Fetch calibration data once per pass instantiation
        self.calibration_data = fetch_calibration_data(
            backend_name=self.backend_name,
            fallback_csv=self.fallback_csv,
            use_fake=self.use_fake
        )

    def _get_active_qubits(self, dag: DAGCircuit) -> list:
        active = set()
        for node in dag.op_nodes():
            for q in node.qargs:
                active.add(dag.find_bit(q).index)
        return list(active)

    def _get_gate_latency(self, qubit_idx: int, gate_name: str) -> float:
        """Returns gate latency in ns"""
        if qubit_idx not in self.calibration_data:
            return 35.5 # default guess

        cal = self.calibration_data[qubit_idx]
        if gate_name in ['x', 'u3']:
            return cal.get("u3_ns", 71.0)
        elif gate_name in ['sx', 'u2']:
            return cal.get("u2_ns", 35.5)
        elif gate_name == 'id':
            # Identity often takes same time as sx
            return cal.get("u2_ns", 35.5)
        else:
            return 35.5

    def run(self, dag: DAGCircuit) -> DAGCircuit:
        active_qubits = self._get_active_qubits(dag)

        budget_ns = calculate_obfuscation_budget(
            self.calibration_data,
            active_qubits,
            eta=self.eta
        )

        added_latency_ns = 0.0
        injected_gate_count = 0
        original_gate_count = len(dag.op_nodes())

        # Greedily inject IGate pairs (U U^dagger)
        # We'll just iterate through the active qubits and append IGate pairs at the end
        # until budget is full. (For real obfuscation we might interleave, but appending/interleaving
        # both add depth and gate count)

        qubits = dag.qubits
        if not qubits:
            return dag

        # We will distribute them across the circuit or at the end
        # For simplicity, we just add them to the DAG iteratively

        while True:
            # Pick a random active qubit or just round-robin
            for q_idx in active_qubits:
                gate_time = self._get_gate_latency(q_idx, self.dummy_gate_name)
                # A pair takes 2 * gate_time
                pair_time = 2 * gate_time

                if added_latency_ns + pair_time > budget_ns:
                    break

                # Add pair
                q_obj = qubits[q_idx]

                # In Qiskit 1.0/2.0, adding to DAG:
                dag.apply_operation_back(IGate(), qargs=[q_obj])
                dag.apply_operation_back(IGate(), qargs=[q_obj])

                added_latency_ns += pair_time
                injected_gate_count += 2

            # Check if we can add any more to ANY qubit
            can_add_more = False
            for q_idx in active_qubits:
                if added_latency_ns + 2 * self._get_gate_latency(q_idx, self.dummy_gate_name) <= budget_ns:
                    can_add_more = True
                    break

            if not can_add_more:
                break

        security_confidence = 0.0
        if budget_ns > 0:
            security_confidence = added_latency_ns / budget_ns

        self.property_set['obfuscation_budget_ns'] = budget_ns
        self.property_set['obfuscation_added_latency_ns'] = added_latency_ns
        self.property_set['obfuscation_injected_gates'] = injected_gate_count
        self.property_set['obfuscation_security_confidence'] = security_confidence
        self.property_set['obfuscation_original_gates'] = original_gate_count
        self.property_set['obfuscation_final_gates'] = original_gate_count + injected_gate_count

        return dag
