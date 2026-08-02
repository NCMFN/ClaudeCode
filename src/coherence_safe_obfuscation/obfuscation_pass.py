import math
from qiskit.transpiler.basepasses import TransformationPass
from qiskit.transpiler.passes import BasisTranslator
from qiskit.circuit.equivalence_library import SessionEquivalenceLibrary
from qiskit.dagcircuit import DAGCircuit
from qiskit.circuit.library import UGate
from coherence_safe_obfuscation.calibration import CalibrationData
from coherence_safe_obfuscation.budget import calculate_budget_ns

class CoherenceSafeObfuscation(TransformationPass):
    """
    A transpiler pass that hides quantum circuit structure by injecting dummy
    identity-gate pairs (U * U_dg), keeping total injected latency under the
    T1/T2 decoherence budget.
    """

    def __init__(self, calibration_data: CalibrationData, eta: float = 0.1, dummy_gate_angles: tuple = (math.pi/2, math.pi/4, math.pi/8)):
        """
        Args:
            calibration_data: The calibration properties of the target backend.
            eta: The safety coefficient for the noise budget (default 0.1).
            dummy_gate_angles: The (theta, phi, lambda) angles to use for the dummy UGate.
        """
        super().__init__()
        self.calibration_data = calibration_data
        self.eta = eta
        self.dummy_gate_angles = dummy_gate_angles
        self.dummy_gate = UGate(*dummy_gate_angles)
        self.dummy_gate_inv = self.dummy_gate.inverse()

    def run(self, dag: DAGCircuit) -> DAGCircuit:
        """Run the pass on the given DAG."""
        active_qubits = []
        for bit in dag.qubits:
            # Assumes index matches physical qubit mappings.
            index = getattr(bit, 'index', dag.qubits.index(bit))
            active_qubits.append(index)

        if not active_qubits:
            self.property_set["security_confidence"] = 0.0
            return dag

        # 1. Fetch T1 times and gate durations
        t1_times = []
        gate_durations = {}
        for q in active_qubits:
            props = self.calibration_data.get_qubit_properties(q)
            t1_times.append(props["t1_us"])
            duration = props.get("u3_ns", 100.0)
            # dummy pair = U + U_dg
            gate_durations[q] = duration * 2

        # 2. Calculate budget
        total_budget_ns = calculate_budget_ns(t1_times, self.eta)

        # 3. Decompose the DAG to base gates to measure native latency.
        # This translates high-level gates down into the standard IBM basis (cx, id, rz, sx, x)
        basis_gates = ['cx', 'id', 'rz', 'sx', 'x']
        translator = BasisTranslator(SessionEquivalenceLibrary, basis_gates)
        decomposed_dag = translator.run(dag)

        # Calculate native latency
        native_latency_ns = 0.0
        for node in decomposed_dag.op_nodes():
            if len(node.qargs) == 1:
                q_idx = getattr(node.qargs[0], 'index', decomposed_dag.qubits.index(node.qargs[0]))
                props = self.calibration_data.get_qubit_properties(q_idx)
                if node.name in ['sx', 'x']:
                    native_latency_ns += props.get("u2_ns", 50.0)
                elif node.name == 'rz':
                    pass # Virtual rz has 0 latency
                else:
                    native_latency_ns += props.get("u3_ns", 100.0)
            elif len(node.qargs) == 2:
                # Roughly estimate 2Q gate latency (typically 3-5x longer than 1Q)
                # This could be pulled precisely from calibration if available, but 300ns is a safe default proxy
                native_latency_ns += 300.0

        self.property_set["native_latency_ns"] = native_latency_ns

        # 4. Inject dummy pairs
        # Iterate through decomposed DAG
        remaining_budget = total_budget_ns
        injected_pairs = 0

        new_dag = decomposed_dag.copy_empty_like()

        for node in decomposed_dag.topological_op_nodes():
            qargs = node.qargs

            if qargs:
                target_q = qargs[0]
                target_idx = getattr(target_q, 'index', decomposed_dag.qubits.index(target_q))

                pair_duration = gate_durations.get(target_idx, 200.0)

                if remaining_budget >= pair_duration and pair_duration > 0:
                    new_dag.apply_operation_back(self.dummy_gate, [target_q])
                    new_dag.apply_operation_back(self.dummy_gate_inv, [target_q])
                    remaining_budget -= pair_duration
                    injected_pairs += 1

            new_dag.apply_operation_back(node.op, qargs, node.cargs)

        if total_budget_ns > 0:
            utilization = (total_budget_ns - remaining_budget) / total_budget_ns
        else:
            utilization = 0.0

        self.property_set["security_confidence"] = utilization
        self.property_set["obfuscated_latency_added_ns"] = total_budget_ns - remaining_budget
        self.property_set["obfuscated_dummy_pairs"] = injected_pairs

        return new_dag
