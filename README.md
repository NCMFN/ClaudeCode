# Enterprise Digital Sanitization Detection Pipeline

This project evaluates Machine Learning detection of red-team-associated sanitization activity in enterprise authentication telemetry. The central finding demonstrates that near-perfect initial detection metrics were driven by temporal shortcut learning (`hour_cos`), emphasizing a methodological framework for detecting temporal leakage.

## Note on Datasets
Not yet completed: cross-dataset validation against CERT r6.2.

## Reproducibility
Run the pipeline with `python src/run_pipeline.py`.
