import simpy
import random
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), 'src')))
from fsm.ep_depin_fsm import EPDePINFSM

BATTERY_CAPACITY_MAH = 3000.0
SIM_DURATION_MINUTES = 72 * 60

SCENARIOS = {
    'Baseline': None,
    'EP-DePIN FSM': {'S1_to_S2': 60, 'S2_to_S3': 35, 'S3_to_S4': 15}
}

CURRENT_DRAWS = {
    'Baseline': 450,
    'S1_FULL': 420,
    'S2_PROOF_ONLY': 280,
    'S3_RELAY_ONLY': 150,
    'S4_PRIMARY_ONLY': 60,
    'No blockchain': 60
}

def current_to_mah(current_ma, duration_min):
    return (current_ma * duration_min) / 60.0

class DePINNodeSimple:
    def __init__(self, env, scenario_name, thresholds):
        self.env = env
        self.scenario_name = scenario_name
        self.battery_mah = BATTERY_CAPACITY_MAH
        self.soc = 100.0
        self.is_dead = False

        self.fsm = None
        if thresholds is not None:
            self.fsm = EPDePINFSM(thresholds)

        self.current_state = 'S1_FULL'
        self.soc_log = []
        self.state_log = []

        self.env.process(self.loop())

    def loop(self):
        while not self.is_dead:
            # log current state
            self.soc_log.append((self.env.now, self.soc))

            if self.scenario_name == 'Baseline':
                draw = CURRENT_DRAWS['Baseline']
                self.state_log.append((self.env.now, 'S1_FULL'))
            else:
                draw = CURRENT_DRAWS[self.current_state]
                self.state_log.append((self.env.now, self.current_state))

            drain = current_to_mah(draw, 1)
            self.battery_mah -= drain
            self.soc = max(0.0, (self.battery_mah / BATTERY_CAPACITY_MAH) * 100.0)

            if self.soc == 0:
                self.is_dead = True

            if not self.is_dead and self.fsm:
                self.current_state = self.fsm.get_state(self.soc)

            yield self.env.timeout(1)

plt.rcParams.update({'font.size': 11, 'axes.titlesize': 13, 'axes.labelsize': 11, 'xtick.labelsize': 10, 'ytick.labelsize': 10, 'figure.dpi': 300, 'savefig.dpi': 300})

COLORS = {
    'S1_FULL': '#1D9E75',
    'S2_PROOF_ONLY': '#BA7517',
    'S3_RELAY_ONLY': '#993C1D',
    'S4_PRIMARY_ONLY': '#888780',
    'Baseline': '#1F3864'
}

def generate_trajectory_plots():
    all_soc = {}
    all_states = {}

    for scenario_name, thresholds in SCENARIOS.items():
        all_soc[scenario_name] = []

        # Run 10 times for SoC trajectories
        for seed in range(42, 52):
            random.seed(seed)
            env = simpy.Environment()
            node = DePINNodeSimple(env, scenario_name, thresholds)
            env.run(until=SIM_DURATION_MINUTES)
            all_soc[scenario_name].append(node.soc_log)

            # Save state log for the first run of EP-DePIN FSM
            if scenario_name == 'EP-DePIN FSM' and seed == 42:
                all_states['EP-DePIN FSM'] = node.state_log

    # Fig 3: SoC trajectory
    plt.figure(figsize=(10, 6))
    for scenario_name, runs in all_soc.items():
        for i, run in enumerate(runs):
            times = [r[0]/60.0 for r in run]
            socs = [r[1] for r in run]

            color = COLORS['Baseline'] if scenario_name == 'Baseline' else COLORS['S1_FULL']
            alpha = 0.5
            label = scenario_name if i == 0 else ""
            plt.plot(times, socs, color=color, alpha=alpha, label=label)

    plt.title('Figure 3: SoC Trajectory (10 runs)')
    plt.xlabel('Time (hours)')
    plt.ylabel('Battery SoC (%)')
    plt.legend()
    plt.grid(True, alpha=0.3)
    plt.tight_layout()
    plt.savefig('results/figures/soc_trajectory.png')
    plt.savefig('results/figures/soc_trajectory.pdf')
    plt.close()

    # Fig 2: FSM state over time (Stacked area chart)
    plt.figure(figsize=(10, 6))
    states_log = all_states['EP-DePIN FSM']
    times = [s[0]/60.0 for s in states_log]

    y1, y2, y3, y4 = [], [], [], []
    for s in states_log:
        st = s[1]
        y1.append(1 if st == 'S1_FULL' else 0)
        y2.append(1 if st == 'S2_PROOF_ONLY' else 0)
        y3.append(1 if st == 'S3_RELAY_ONLY' else 0)
        y4.append(1 if st == 'S4_PRIMARY_ONLY' else 0)

    plt.stackplot(times, y1, y2, y3, y4, labels=['S1_FULL', 'S2_PROOF_ONLY', 'S3_RELAY_ONLY', 'S4_PRIMARY_ONLY'],
                  colors=[COLORS['S1_FULL'], COLORS['S2_PROOF_ONLY'], COLORS['S3_RELAY_ONLY'], COLORS['S4_PRIMARY_ONLY']])

    plt.title('Figure 2: FSM State Over Time')
    plt.xlabel('Time (hours)')
    plt.ylabel('Active state (Binary)')
    plt.legend(loc='upper right')
    plt.tight_layout()
    plt.savefig('results/figures/fsm_state_over_time.png')
    plt.savefig('results/figures/fsm_state_over_time.pdf')
    plt.close()

if __name__ == '__main__':
    generate_trajectory_plots()
