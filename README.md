# Adaptive TTL Policy for Entangled Keys - QKD Simulator

This repository implements a Python research simulator for an "Adaptive TTL Policy for Entangled Keys." It explores a No-ML, telemetry-driven buffer-flush policy for Quantum Key Distribution (QKD) systems.

## Context
In QKD systems, Bell pairs held in quantum memory decohere over time (T2 transverse relaxation). Classical confirmation signals travel at network speed and are subject to latency and jitter. If confirmation arrives after fidelity drops below 0.85, the key is considered a security liability ("Zombie Data"). This policy monitors real-time Round Trip Time (RTT), computes fidelity decay, and flushes the buffer if the threshold is crossed.

## Model Constraints and Assumptions
- **RTT Dataset**: The simulation leverages the Seattle dataset from [NetLatency-Data](https://github.com/uofa-rzhu3/NetLatency-Data). For each of the 688 time slices, one strictly non-zero RTT sample is extracted randomly. This synthesizes a continuous trace of sequential measurements.
- **Independence**: The RTT data is not genuinely time-correlated with real quantum hardware runs; it's a synthetic fusion of independent public datasets. It's meant for simulating telemetry feedback.
- **Fidelity Decay**: model is `F(t) = 0.5 + 0.5 * exp(-t / T2)`.
- **Pure Python**: Uses `pandas`, `numpy`, `matplotlib`, and `seaborn`. No machine learning elements are included, demonstrating a purely deterministic approach.

## Components
1. `data_loaders/netlatency_loader.py` - Parses the Seattle NetLatency data into a time series.
2. `model/fidelity.py` - Implements the fidelity decay math. T2 configuration defaults are provided for:
   - **IonQ Aria** (Trapped-ion): T2 ≈ 1.0 s
   - **AQT ring chip** (Superconducting transmon): T2 ≈ 50 ms
3. `policy/adaptive_ttl.py` & `policy/static_ttl.py` - Implement adaptive buffer flushing and a naive static-TTL timeout comparison.
4. `simulate.py` - Executes both policies against the parsed dataset and exports performance to CSV and an Open MCT-compliant JSON telemetry format.
5. `reporting/generate_reports.py` - Generates a variety of figures (distributions, time series, correlations) and tables (summaries, metrics) for reporting purposes.

## Usage
Ensure you have the required dependencies installed:
```bash
pip install pandas numpy matplotlib seaborn
```

First, clone the required NetLatency-Data repository to provide the RTT matrix files:
```bash
git clone https://github.com/uofa-rzhu3/NetLatency-Data.git
```

Then, execute the entire simulation pipeline and reporting scripts:
```bash
python simulate.py
python reporting/generate_reports.py
```

Output datasets, Open MCT telemetry JSONs, graphical charts, and CSV tables will populate in the `outputs/` folder.
