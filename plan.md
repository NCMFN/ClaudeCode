1. **Project setup**: Create `pyproject.toml` with `coherence_safe_obfuscation` package and dependencies: `qiskit>=1.0`, `qiskit-ibm-runtime`, `numpy`, `pandas`, `matplotlib`, `pytest`. Create `src/coherence_safe_obfuscation/__init__.py`.
2. **Calibration module**: Create `src/coherence_safe_obfuscation/calibration.py` handling runtime service backend properties or local CSV fallback.
3. **Budget module**: Create `src/coherence_safe_obfuscation/budget.py` implementing `eta * min_T1`.
4. **Obfuscation Pass**: Create `src/coherence_safe_obfuscation/obfuscation_pass.py` subclassing `TransformationPass` to add dummy identity gates based on latency budget.
5. **Integration script**: Create `src/examples/run_obfuscation_demo.py` with 3 test circuits, saving to `src/outputs/raw/run_results.json`.
6. **Tests and CI**: Write `tests/test_obfuscation.py` and `.github/workflows/pytest.yml`.
7. **Reporting layer**: Create `src/reporting/plot_style.py` and `src/reporting/generate_outputs.py` to produce 10+ figures, 10+ tables, and a `source_manifest.json` in `src/outputs/figures/` and `src/outputs/tables/`.
8. **Pre-commit**: Run pre-commit instructions.
9. **Submit**: Create PR.
