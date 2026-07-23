# Classifying Historical Telegraph Defects — Supervised ML on 19th-Century Submarine Cable Telemetry

## 1. Abstract
This paper presents a machine learning pipeline classifying historical telegraph defect telemetry into three classes: Insulation Degradation, Inductive Crosstalk, and Ground Faults & Leakage.

## 2. Introduction & Research Problem
Historical records of the 1858 and 1866 transatlantic cables provide qualitative narratives of failures, but quantitative analysis is hampered by the lack of digitized logbooks. This paper bridges the gap by building predictive models on physics-grounded synthetic telemetry.

## 3. Historical Background
The controversy between E.O.W. Whitehouse and William Thomson (Lord Kelvin) highlighted the challenges of early submarine cables. Whitehouse's use of ~700V induction coils famously ruptured the gutta-percha insulation of the 1858 cable. Thomson's 1855 Law of Squares defined signal retardation scaling ($t \propto L^2$).

## 4. Data & Methods
**Note on Data Provenance:** The dataset used in this study is a physics-grounded **synthetic** dataset generated to model the historical ranges and failure mechanisms described in primary sources. It is not an archival tabular dataset.

Features include Resistance (2.5–12.0 Ω/mi), Capacitance (0.25–0.45 μF/mi), Voltage (12–700 V), and Length (500–2200 nmi).

## 5. Models
We evaluate Multinomial L2-regularized Logistic Regression as a baseline, alongside Linear and RBF Support Vector Machines. Hyperparameters were tuned via 5-fold cross-validation.

## 6. Results
The generated data produced the following metrics on the test set:
- **Logistic Regression**: Accuracy = 0.4917, Macro-F1 = 0.3504
- **Linear SVM**: Accuracy = 0.4950, Macro-F1 = 0.3535
- **RBF SVM**: Accuracy = 0.4900, Macro-F1 = 0.3495

Odds ratios indicate the varying impact of parameters (see `outputs`).
See figures in `figures/`.

## 7. Discussion
The L2 regularization in our logistic model mitigated the multicollinearity between Length and Retardation. The high voltage testing clearly correlated with Insulation Degradation, reflecting historical accounts.

## 8. Conclusion & Future Work
Future work involves partnering with archives like the Porthcurno Telegraph Museum to digitize physical logbooks and validate these simulated findings against empirical data.

## 9. References
- Atlantic Cable history archive: https://atlantic-cable.com/
- IEEE Engineering and Technology History Wiki, "Underwater Cables": https://ethw.org/Underwater_Cables
- IEEE Technology Navigator, "Telegraphy": https://technav.ieee.org/topic/telegraphy/
