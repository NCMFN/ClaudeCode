# Adaptive Lightweight Blockchain Node Architecture for Energy-Constrained DePIN Devices

## Overview
This repository contains the simulation, modeling, and analysis code for the IEEE conference paper "Adaptive Lightweight Blockchain Node Architecture for Energy-Constrained DePIN Devices".

The research introduces an autonomous 4-state Finite State Machine (FSM) tailored for DePIN (Decentralized Physical Infrastructure Networks) devices, optimizing energy consumption while guaranteeing primary task preservation.

## Differentiators
1. **Device-side autonomous FSM**: The node regulates its own participation role via on-device firmware based on State-of-Charge (SoC), with zero network coordinator calls.
2. **DePIN-specific proof types**: The adaptation focuses on Proof of Coverage (PoC) and Proof of Uptime (PoU) events, avoiding generic IoT transaction models.
3. **Primary task guarantee**: A strict formal invariant ensures the device never fails its physical sensing or routing function regardless of the battery level.

## Project Structure
- `data/`: Contains primary (IoT-Enabled Smart Grid) and processed datasets.
- `src/fsm/`: FSM logic implementation (`ep_depin_fsm.py`).
- `src/simulation/`: Discrete-event simulation using SimPy (`simulation.py`).
- `src/analysis/`: Statistical tests and figure generation scripts.
- `tests/`: Pytest unit tests verifying the FSM constraints and invariant.
- `results/`: Simulation tables, statistical test outputs, and generated figures.

## Environment Setup
1. Create a Python 3 environment: `python3 -m venv venv`
2. Activate the environment: `source venv/bin/activate`
3. Install dependencies: `pip install -r requirements.txt`

## Reproduction Steps
1. **Data Preprocessing**: `python3 preprocess_data.py`
2. **Unit Tests**: `pytest tests/test_fsm.py`
3. **Simulation Runs**: `python3 src/simulation/simulation.py`
4. **Statistical Analysis**: `python3 src/analysis/analysis.py`
5. **Figure Generation**: `python3 generate_figures.py` and `python3 generate_arch_diagram.py`

