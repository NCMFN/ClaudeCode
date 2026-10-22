# Adaptive Lightweight Blockchain Node Architecture for Energy-Constrained DePIN Devices

## Overview
This project fully implements, validates, and reproduces the research study on an adaptive Lightweight Blockchain Node Architecture for Energy-Constrained DePIN Devices.

## Structure
- `data/`: Contains primary, supporting, and processed datasets.
- `src/`: Core logic including the Finite State Machine (FSM) implementation, Simulation Engine, and Analysis modules.
- `results/`: Contains generated figures, tables, and execution logs.
- `tests/`: Unit tests validating critical invariants.

## Phases Executed
1. **Data Preprocessing**: Data cleaning, schema validation, and time-based split.
2. **FSM Implementation**: The `EPDePINFSM` class with state logic and strict invariants.
3. **Simulation**: A SimPy simulation tracking battery lifetime, FSM transitions, and metrics.
4. **Statistical Analysis**: Statistical significance tests validating battery gain and coverage retention.
5. **Figure Generation**: High-quality IEEE-ready visual representations of performance metrics.

## Running Tests
Run all unit tests using:
`PYTHONPATH=. pytest tests/test_fsm.py`
