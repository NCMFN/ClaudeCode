# Revision Log

## Major Fixes Implemented
- **Removed Synthetic Artifacts:** Deleted all legacy placeholder figures, synthetic overlays, and padding. The pipeline now strictly refuses to generate text-only figures or use the words "illustrative", "dummy", or "synthetic" in results.
- **Fixed Sampling Leakage:** Replaced the legacy sampling strategy (which drew benign events only from the first ~500k lines and malicious events from later days) with a rigorous time-stratified sampling approach spanning the entire 58-day timeline.
- **Strict Chronological Evaluation:** Replaced flawed Random (P1) and GroupShuffleSplit (P2) protocols with strict Chronological (P3) and Rolling-Origin (P4) splits incorporating a purge gap.
- **Causal Features Only:** Fixed feature engineering to strictly use only past events (expanding windows). Removed non-causal global statistics.
- **Removed Verify=False:** Enforced strict TLS verification for all downloads.
- **Removed Unstable Legacy Models:** Legacy models (LSTM/MLP/SVM/meta-classifier) were removed to focus on robust tabular baselines (LR, XGBoost, Isolation Forest) under the new strict protocols.
