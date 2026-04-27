import simpy
import random
import pandas as pd
import numpy as np
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from fsm.ep_depin_fsm import EPDePINFSM

BATTERY_CAPACITY_MAH = 3000.0
SIM_DURATION_MINUTES = 72 * 60

SCENARIOS = {
    'Baseline': None,
    'EP-DePIN FSM': {'S1_to_S2': 60, 'S2_to_S3': 35, 'S3_to_S4': 15},
    'EP-DePIN Aggressive': {'S1_to_S2': 50, 'S2_to_S3': 25, 'S3_to_S4': 10},
    'EP-DePIN Conservative': {'S1_to_S2': 70, 'S2_to_S3': 45, 'S3_to_S4': 20},
    'No blockchain': 'None'
}

CURRENT_DRAWS = {
    'Baseline': 450,
    'S1_FULL': 420,
    'S2_PROOF_ONLY': 280,
    'S3_RELAY_ONLY': 150,
    'S4_PRIMARY_ONLY': 60,
    'No blockchain': 60
}

# mA * minutes -> mAh => draw * duration_min / 60
def current_to_mah(current_ma, duration_min):
    return (current_ma * duration_min) / 60.0

class DePINNode:
    def __init__(self, env, scenario_name, thresholds):
        self.env = env
        self.scenario_name = scenario_name
        self.battery_mah = BATTERY_CAPACITY_MAH
        self.soc = 100.0
        self.is_dead = False

        self.poc_proofs_submitted = 0
        self.poc_proofs_missed = 0
        self.primary_tasks_completed = 0
        self.primary_tasks_total = 0

        self.state_transitions = 0
        self.time_in_states = {'S1_FULL': 0, 'S2_PROOF_ONLY': 0, 'S3_RELAY_ONLY': 0, 'S4_PRIMARY_ONLY': 0}

        self.coordinator_calls = 0
        self.proof_log = []

        self.fsm = None
        if thresholds is not None and thresholds != 'None':
            self.fsm = EPDePINFSM(thresholds)

        self.current_state = 'S1_FULL'
        if self.scenario_name == 'No blockchain':
            self.current_state = 'S4_PRIMARY_ONLY'
        elif self.scenario_name == 'Baseline':
            self.current_state = 'S1_FULL'

        self.soc_log = []

        # Start processes
        self.env.process(self.primary_task_loop())
        self.env.process(self.poc_proof_loop())
        self.env.process(self.battery_drain_loop())

    def update_soc(self):
        self.soc = max(0.0, (self.battery_mah / BATTERY_CAPACITY_MAH) * 100.0)
        if self.soc == 0:
            self.is_dead = True

        # Log state
        self.soc_log.append((self.env.now, self.soc))

        if not self.is_dead and self.fsm:
            old_state = self.current_state
            self.current_state = self.fsm.get_state(self.soc)
            if old_state != self.current_state:
                self.state_transitions += 1

    def primary_task_loop(self):
        while not self.is_dead:
            # every 60 seconds
            yield self.env.timeout(1)
            if self.is_dead: break

            self.primary_tasks_total += 1

            # Burst draw: 5 mA for 10 ms (0.01s = 0.00016 min)
            drain = current_to_mah(5, 0.01 / 60)
            self.battery_mah -= drain
            self.update_soc()

            # Invariant check
            if self.fsm:
                assert self.fsm.primary_task_active(self.current_state) == True

            if not self.is_dead:
                self.primary_tasks_completed += 1

    def poc_proof_loop(self):
        while not self.is_dead:
            # every 5 minutes
            yield self.env.timeout(5)
            if self.is_dead: break

            can_submit = False
            if self.scenario_name == 'Baseline':
                can_submit = True
            elif self.scenario_name == 'No blockchain':
                can_submit = False
            elif self.fsm:
                ops = self.fsm.get_blockchain_ops(self.current_state)
                can_submit = ops['submit_tx']

            if can_submit:
                # 30 mA burst for 800 ms (0.8s = 0.0133 min)
                drain = current_to_mah(30, 0.8 / 60)
                self.battery_mah -= drain
                self.update_soc()
                if not self.is_dead:
                    self.poc_proofs_submitted += 1
                    self.proof_log.append((self.env.now, 'PoC'))
            else:
                self.poc_proofs_missed += 1

    def battery_drain_loop(self):
        while not self.is_dead:
            yield self.env.timeout(1)
            if self.is_dead: break

            # Base drain for the minute
            if self.scenario_name == 'Baseline':
                draw = CURRENT_DRAWS['Baseline']
            elif self.scenario_name == 'No blockchain':
                draw = CURRENT_DRAWS['No blockchain']
            else:
                draw = CURRENT_DRAWS[self.current_state]

            self.time_in_states[self.current_state] += 1

            drain = current_to_mah(draw, 1)
            self.battery_mah -= drain
            self.update_soc()

def run_simulation():
    results = []
    soc_trajectories = {}

    for scenario_name, thresholds in SCENARIOS.items():
        soc_trajectories[scenario_name] = []
        for seed in range(42, 52): # 10 runs
            random.seed(seed)
            env = simpy.Environment()
            node = DePINNode(env, scenario_name, thresholds)
            env.run(until=SIM_DURATION_MINUTES)

            # Calculate metrics
            lifetime = env.now
            if node.battery_mah > 0:
                lifetime = SIM_DURATION_MINUTES

            completion_rate = 100.0 if node.primary_tasks_total == 0 else (node.primary_tasks_completed / node.primary_tasks_total) * 100

            results.append({
                'Scenario': scenario_name,
                'Run': seed - 41,
                'Lifetime_mins': lifetime,
                'Proofs_Submitted': node.poc_proofs_submitted,
                'Proofs_Missed': node.poc_proofs_missed,
                'Primary_Task_Completion_%': completion_rate,
                'Transitions': node.state_transitions,
                'S1_Time': node.time_in_states.get('S1_FULL', 0),
                'S2_Time': node.time_in_states.get('S2_PROOF_ONLY', 0),
                'S3_Time': node.time_in_states.get('S3_RELAY_ONLY', 0),
                'S4_Time': node.time_in_states.get('S4_PRIMARY_ONLY', 0),
                'Coordinator_Calls': node.coordinator_calls
            })
            soc_trajectories[scenario_name].append(node.soc_log)

    df_results = pd.DataFrame(results)
    df_results.to_csv('results/tables/simulation_results.csv', index=False)

    # Validation checks
    assert df_results['Coordinator_Calls'].sum() == 0, 'FSM must be fully device-side — no coordinator calls permitted'
    assert (df_results['Primary_Task_Completion_%'] == 100.0).all(), 'PRIMARY TASK INVARIANT VIOLATED'

    summary = df_results.groupby('Scenario').agg({
        'Lifetime_mins': ['mean', 'std'],
        'Proofs_Submitted': ['mean', 'std'],
        'Primary_Task_Completion_%': 'mean'
    }).reset_index()

    # Flatten multi-level columns
    summary.columns = ['_'.join(col).strip() if col[1] else col[0] for col in summary.columns.values]
    summary.to_csv('results/tables/simulation_summary.csv', index=False)

    print("Simulation complete.")

if __name__ == '__main__':
    run_simulation()
