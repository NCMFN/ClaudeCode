#!/bin/bash
set -e

echo "Starting DRPP Extended Simulation..."

echo "Running unit tests..."
PYTHONPATH=. pytest tests/

echo "Running experiments..."
PYTHONPATH=src python experiments/exp_1_to_3.py
PYTHONPATH=src python experiments/exp_4_to_6.py
PYTHONPATH=src python experiments/exp_7_to_9.py
PYTHONPATH=src python experiments/generate_static.py

echo "Simulation completed successfully! All data, figures, and tables generated."
