# DRPP Extended Simulation & Empirical Study

This repository contains the complete, reproducible Python simulation and analysis framework that empirically validates, extends, and statistically stress-tests the DRPP protocol. This project extends the conference paper "Deception-Resistant Presence Proof (DRPP): A Cryptographic Protocol for Human-Centric Authentication."

## Structure
- `/src` -> Core simulation code and liveness detection modalities (modular, unit-tested)
- `/experiments` -> Experiment runner scripts to execute specific simulation modules
- `/data` -> Raw CSV outputs of all simulations
- `/figures` -> All generated figures (PNG + SVG)
- `/tables` -> All generated tables (CSV + LaTeX + Markdown)
- `/report` -> Final Markdown report compiling everything
- `/tests` -> Unit tests for core protocol logic

## Running
Install dependencies:
```bash
pip install -r requirements.txt
```

Run all simulations and generate all artifacts:
```bash
./run_all.sh
```

Run unit tests:
```bash
pytest tests/
```
