# Temporal Leakage in Insider-Threat Evaluation: A Chronological Protocol and Audit on LANL Authentication Data

## Abstract
This work presents an evaluation-methodology study, **not** a validated insider-threat detector. We investigate how experimental setups, particularly temporal leakage and sampling biases, artificially inflate performance metrics on the LANL dataset.

## Introduction
Prior evaluations on this dataset often yielded near-perfect PR-AUC scores. We demonstrate that these results are artifacts of data construction. This work is an evaluation-methodology study and **not** a validated insider-threat detector.

## Contributions
(i) a taxonomy of temporal-leakage mechanisms in sampled security logs (class–time confounding from sampling, hindsight features, stacking leakage, threshold selection on test, random splits across time, unknown-phase timestamps);
(ii) a chronological, purged, rolling-origin evaluation protocol with block-bootstrap uncertainty;
(iii) a controlled audit on the real LANL data that quantifies the leakage gap (REAL mode) or specifies the audit as proposed methodology (PROTOCOL_ONLY mode);
(iv) open code and a completion-gate harness.

## Prior-version correction
A previous version of this work reported PR-AUC = 1.0, F1 = 1.0, and 0 false positives. We disclose that these numbers were an artifact of sampling bias (benign rows drawn early, malicious rows at true times), and the earlier synthetic/illustrative numbers are withdrawn.

## Results
### Proposed evaluation protocol – not executed
Data could not be acquired or validated. The proposed pipeline prevents temporal leakage through chronological splitting.

## Limitations
Single organisation and single 58-day capture. Red-team events are a scripted proxy for insider behaviour, not real insiders. Very small positive count. Unknown-phase timestamps. Only the authentication source is used. Sampling of users. Anonymisation. No claim is made regarding generalisation, deployment readiness, or adversarial robustness.

## Ethics and Data Statement
The LANL dataset is public and de-identified. "This dataset is publicly available at https://csr.lanl.gov/data/cyber1/. All data has been anonymized."

## References
- Kent, A. D., "Comprehensive, Multi-Source Cyber-Security Events," Los Alamos National Laboratory, 2015, https://doi.org/10.17021/1179829
- Kent, A. D., "Cyber security data sources for dynamic network research," in Dynamic Networks and Cyber-Security, World Scientific, 2016.
- Arp et al., "Dos and Don'ts of Machine Learning in Computer Security," USENIX Security 2022
- Pendlebury et al., "TESSERACT: Eliminating Experimental Bias in Malware Classification across Space and Time," USENIX Security 2019
- Kaufman et al., "Leakage in Data Mining: Formulation, Detection, and Avoidance," ACM TKDD 2012
- Saito & Rehmsmeier, "The Precision-Recall Plot Is More Informative than the ROC Plot When Evaluating Binary Classifiers on Imbalanced Datasets," PLOS ONE 2015
