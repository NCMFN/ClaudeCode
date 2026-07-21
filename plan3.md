1. **Fix Ingestion (Phase 1)**: Use `zgrep` to extract real auth records matching `redteam` users to get their actual `event_type` and avoid label artifact. We'll use a fast grep for redteam users to pull their true auth records.
2. **Remove Noise Features (Phase 2)**: Remove `path_entropy` and `usb_delta_seconds` completely, update ablation logic.
3. **Graph Features (Phase 2)**: Fix `.head(10000)` to `.sample(n=50000, random_state=42)` or full data.
4. **Phase 6 Artifacts**: Recreate `phase6_artifacts.py` to generate 20 figures and 20 tables based on the real pipeline metrics.
5. **Update Logs**: Log to `outputs/revision_log.md` under "Pass #3".
