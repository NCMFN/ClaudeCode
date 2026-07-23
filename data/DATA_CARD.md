# Data Card: Synthetic 19th-Century Submarine Telegraph Telemetry

## Overview
This dataset is **SYNTHETIC/SIMULATED** and does not represent actual digitized logbook telemetry. It was generated to serve as a physics-grounded proxy for historical events, specifically to train and evaluate machine learning models for the purpose of a research project/conference paper (HISTELCON).

## Why Synthetic?
There is currently no clean, tabular, public dataset of 19th-century cable fault telemetry containing parameters like Resistance (R), Capacitance (C), Voltage (V), and Length (L) per fault event. Real archives (e.g., atlantic-cable.com, Porthcurno Museum) hold narrative accounts and scanned primary sources, which have not yet been digitized into ML-ready formats.

## Generation Logic and Historical Grounding
The generation logic (`generate_synthetic_telegraph_data.py`) uses parameter ranges based on the real physical properties of the 1858 and 1866 transatlantic cables.

### Parameter Ranges
- **Resistance R (Ω/mi):** 2.5 – 12.0
- **Capacitance C (μF/mi):** 0.25 – 0.45
- **Voltage V (VDC):** 12 – 700 V (Typical operating voltages were low, but tests like those by E.O.W. Whitehouse on the 1858 cable used induction coils reaching ~700V).
- **Length L (nmi):** 500 – 2200 (Representing various segments and full transatlantic spans).
- **Signal Retardation t (ms):** 100 – 1800 ms. Simulated proportionally to $R \times C \times L^2$ as described by William Thomson's (Lord Kelvin) 1855 Law of Squares, plus normally distributed noise.

### Fault Classes and Mechanisms
1. **Insulation Degradation:** Probability increases with higher V, higher C, and proxy latent variables for thinner effective insulation. This models the historical failure of the 1858 cable's gutta-percha insulation due to Whitehouse's high-voltage induction coils.
2. **Inductive Crosstalk:** Probability increases with moderate Resistance and a latent proxy variable simulating parallel paths or closely-spaced cables.
3. **Ground Faults & Leakage:** Probability increases with lower insulation resistance (modeled inversely to R in this context) and higher latent seawater exposure.

Overall failure rates are distributed such that approximately 75% of failures fall into Insulation Degradation and Ground Faults & Leakage combined.

## Missing Data
To simulate the reality of incomplete historical 19th-century logbooks, missingness (NaN values) was randomly introduced at a rate of 5% for Resistance and Capacitance, and 10% for Retardation.

## Citations for Parameter Ranges and Historical Context
- **Atlantic Cable History Archive:** https://atlantic-cable.com/
- **IEEE Engineering and Technology History Wiki, "Underwater Cables":** https://ethw.org/Underwater_Cables
- **IEEE Technology Navigator, "Telegraphy":** https://technav.ieee.org/topic/telegraphy/

*Note: These sources are cited for the historical narrative and parameter bounding, NOT as sources of the tabular data itself.*
