# Adaptive TTL Policy for Entangled Keys

A Python research simulator for a telemetry-driven buffer-flush policy for quantum key distribution systems.

## Overview
Bell pairs held in quantum memory decohere over time ($T_2$ relaxation). Classical confirmation signals carrying key-validity info travel at network speed and are subject to latency/jitter. If confirmation arrives after fidelity drops below 0.85, the key is a security liability ("Zombie Data"). This policy monitors real-time RTT, computes fidelity decay, and flushes the buffer before that threshold is crossed.

## Model and Assumptions
- **Fidelity Decay**: $F(t) = 0.5 + 0.5 \times \exp(-t / T_2)$, where $t$ is the measured classical RTT latency.
- **T2 Regimes**:
  - **IonQ Aria**: $T_2 \approx 1.0$ s (Source: [IonQ Aria Capabilities](https://www.ionq.com/quantum-systems/aria))
  - **AQT Ring Chip**: $T_2 \approx 50$ ms typical (Source: [AQT Capabilities](https://aqt.lbl.gov/about-aqt/collaborate-with-us/aqt-capabilities/))
- **RTT Data**: Uses the [Seattle dataset](https://github.com/uofa-rzhu3/NetLatency-Data) (99x99 RTT matrices, 688 time slices).
  - *Note*: RTT data is not genuinely time-correlated with real quantum hardware runs. This simulator is a synthetic fusion of independent public datasets, not a validated end-to-end experiment.

## Output Locations
- **Raw Simulation Outputs**: `src/outputs/raw/` (CSV logs and Open MCT JSON schema).
- **Figures**: `src/outputs/figures/` (10 generated plots).
- **Tables**: `src/outputs/tables/` (10 generated CSV tables).
- **Manifest**: `src/outputs/source_manifest.json` mapping all artifacts to their source computations.

## Usage
- To run the simulator: `python3 src/simulate.py`
- To generate figures and tables: `python3 src/reporting/generate_outputs.py`

