from qiskit.transpiler.basepasses import TransformationPass
from qiskit.transpiler.passes import BasisTranslator
from qiskit.circuit.equivalence_library import SessionEquivalenceLibrary as sel
from qiskit.dagcircuit import DAGCircuit
from qiskit.circuit.library import IGate
import numpy as np

from coherence_safe_obfuscation.calibration import fetch_calibration_from_backend
from coherence_safe_obfuscation.budget import calculate_latency_budget

class CoherenceSafeObfuscationPass(TransformationPass):
    def __init__(self, backend, eta=0.1):
        super().__init__()
        self.backend = backend
        self.eta = eta
        self.target = backend.target
        self.cal_data = fetch_calibration_from_backend(backend)

    def run(self, dag: DAGCircuit) -> DAGCircuit:
        # First, decompose the circuit to the target basis gates to measure native latency accurately
        # Wait, BasisTranslator requires a target. Let's assume the input DAG is already close, or we can measure its latency directly.
        # But per constraints: "decompose the input circuit to base gates and measure native latency"

        # We will use BasisTranslator to decompose if possible, or just measure native latency.
        # It's easier to just translate it on the fly if needed, but a standard TranspilerPass modifies the DAG in-place.
        # For simplicity in this TransformationPass, we assume the dag is already in basis or we map it.
        # Let's map it using BasisTranslator.
        basis_gates = list(self.target.operation_names)
        translator = BasisTranslator(sel, basis_gates)
        dag = translator.run(dag)

        # Determine active qubits
        active_qubits = []
        for q in dag.qubits:
            idx = dag.find_bit(q).index
            active_qubits.append(idx)

        # Get T1 times dict
        t1_times = {idx: self.cal_data[idx]['t1_us'] * 1e-6 for idx in active_qubits} # convert back to seconds

        # Calculate budget
        allowed_latency_seconds = calculate_latency_budget(t1_times, active_qubits, self.eta)

        # Determine duration of the dummy gate pair we are inserting (id gate)
        # Using id gate pair (id -> id) or just a single id if we define it as identity. We'll use pairs of IGate to be a U U+ pair.
        # Let's find duration of 'id' from calibration.
        # If 'id' is in target, great. Otherwise assume it's same as 'sx' or some fallback.
        dummy_latency_seconds = 0.0
        # Let's use max 'id' or 'sx' duration across active qubits
        for q in active_qubits:
            q_latency = 0.0
            if 'id' in self.target and (q,) in self.target['id']:
                q_latency = getattr(self.target['id'][(q,)], 'duration', 0.0)
            elif 'sx' in self.target and (q,) in self.target['sx']:
                q_latency = getattr(self.target['sx'][(q,)], 'duration', 0.0)
            if q_latency > dummy_latency_seconds:
                dummy_latency_seconds = q_latency

        # If we can't find a duration, just fallback to 50ns
        if dummy_latency_seconds == 0.0:
            dummy_latency_seconds = 50e-9

        pair_duration = 2 * dummy_latency_seconds

        cumulative_added_latency = 0.0
        injected_pairs = 0

        # We will greedily inject IGate() pairs onto active qubits at the end or interspersed
        # To intersperse safely without breaking semantics, we just append U U^dag pairs.
        # For simplicity, we just inject them at the end of the DAG for obfuscation depth.

        if pair_duration > 0:
            max_pairs = int(allowed_latency_seconds // pair_duration)

            for _ in range(max_pairs):
                # We could round-robin over active qubits
                q_idx = active_qubits[injected_pairs % len(active_qubits)]
                q = dag.qubits[q_idx]
                # Apply U and U_dag. Since we use IGate, U = I, U_dag = I
                dag.apply_operation_back(IGate(), qargs=[q])
                dag.apply_operation_back(IGate(), qargs=[q])
                cumulative_added_latency += pair_duration
                injected_pairs += 1

        # Compute security confidence. Simple metric: added_latency / allowed_latency
        confidence = cumulative_added_latency / allowed_latency_seconds if allowed_latency_seconds > 0 else 0.0

        self.property_set['security_confidence'] = confidence
        self.property_set['injected_latency'] = cumulative_added_latency
        self.property_set['allowed_latency'] = allowed_latency_seconds
        self.property_set['injected_pairs'] = injected_pairs

        return dag
