# Enterprise Digital Sanitization Detection Pipeline

Research-grade ML pipeline that extends a prior small-scale insider-threat sanitization study into an enterprise-scale, adversarially-robust, explainable detection system.

## Dataset Acquisition Steps

This pipeline utilizes two datasets. For automated execution, LANL is streamed and heavily subsampled, while CERT requires manual download.

1. **LANL Comprehensive, Multi-Source Cyber-Security Events (Authentication data)**
   - **Source:** https://csr.lanl.gov/data/cyber1/
   - **Size:** `auth.txt.gz` is ~12GB compressed. The pipeline streams this using chunk-processing rather than loading it fully into memory.
   - **Ground Truth:** `redteam.txt.gz` is fetched to identify malicious authentication events.

2. **CERT Insider Threat Test Dataset (r6.2)**
   - **Source:** https://kilthub.cmu.edu/articles/dataset/Insider_Threat_Test_Dataset/12841247
   - **Note:** Direct downloads are often gated by web application firewalls (WAF) or authentication challenges. If you wish to use CERT data, manually download it and place the CSVs (logon.csv, device.csv, etc.) and `answers.tar.bz2` in `data/cert/`. The automated pipeline gracefully skips CERT if the mirror is blocked and defaults to LANL testing.

## Execution

```bash
pip install -r requirements.txt
python src/run_pipeline.py
python src/display_results.py
```


### Limitations
- **Chronological Split Constraint**: chronological evaluation was not fully completable under this class distribution. The subsampled benign traffic primarily exists at the start of the trace, while malicious events occur later. Thus, the temporal slice required for a true chronological split resulted in zero malicious events in the training window, proving the dataset's fundamental temporal leakage.