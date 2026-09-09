import os
fig_dir, tbl_dir = "outputs/figures", "outputs/tables"
expected_figs = [f"figure_{i:02d}" for i in range(1, 56)]  # N = 55
found_figs = os.listdir(fig_dir) if os.path.isdir(fig_dir) else []
missing_figs = [f for f in expected_figs if not any(f in name for name in found_figs)]
print(f"Figures found: {len(found_figs)} / {len(expected_figs)} expected")
print(f"Missing figures: {missing_figs}")
zero_byte_figs = [f for f in found_figs if os.path.getsize(os.path.join(fig_dir, f)) == 0]
print(f"Zero-byte figures (treat as missing): {zero_byte_figs}")

expected_tbls = [
    "model_comparison_metrics.csv",
    "feature_importances.csv",
    "anomaly_by_disruption_type.csv",
    "human_intervention_nodes.csv",
    "equity_risk_routes.csv",
    "route_elasticity_table.csv",
    "best_hyperparams.json"
]
found_tbls = os.listdir(tbl_dir) if os.path.isdir(tbl_dir) else []
missing_tbls = [t for t in expected_tbls if t not in found_tbls]
print(f"Tables found: {len(found_tbls)} / {len(expected_tbls)} expected")
print(f"Missing tables: {missing_tbls}")
zero_byte_tbls = [t for t in found_tbls if os.path.getsize(os.path.join(tbl_dir, t)) == 0]
print(f"Zero-byte tables: {zero_byte_tbls}")

if not missing_figs and not zero_byte_figs and not missing_tbls and not zero_byte_tbls:
    print("AUDIT PASSED")
else:
    print("AUDIT FAILED")
