# Revision Log

## Download Outcomes
- Red-team authentication: PASSED (File downloaded successfully, size 4846 bytes, SHA-256 verified, 749 events).
- Authentic LANL data: Failed to download the full 7626505158 byte `auth.txt.gz` file within the sandbox time budget. The file exists on the author's machine and the evaluation is deferred to a local run.

## Fallback
Status: PROPOSED_METHODOLOGY
LANL auth data download exceeded time budget. Fallback to proposed methodology.

## Artifacts Generated
* `outputs/tables/redteam_authentication.csv`
* `outputs/tables/cert_cross_dataset_validation_skipped.csv`
* `outputs/tables/redteam_events_per_day.csv`
* `outputs/tables/redteam_events_per_hour_offset.csv`
* `outputs/tables/redteam_events_per_user.csv`
* `outputs/tables/redteam_computer_pair_counts.csv`
* `outputs/tables/redteam_interevent_time_summary.csv`
* `outputs/tables/redteam_split_feasibility.csv`
* `outputs/tables/spec_split_strategies.csv`
* `outputs/tables/spec_feature_groups.csv`
* `outputs/tables/spec_claims_and_limitations.csv`
* `outputs/tables/spec_gate_definitions.csv`
* `outputs/figures/redteam_events_per_day.png`
* `outputs/figures/redteam_cumulative_events.png`
* `outputs/figures/redteam_hour_offset_distribution.png`
* `outputs/figures/redteam_events_per_user.png`
* `outputs/figures/redteam_split_feasibility_heatmap.png`
* `outputs/figures/protocol_schematic_chronological_split.png`

None. Not computed / not generated, with reasons:
* All model evaluations, cross-validation, significance tests, ablations, adversarial diagnostics, and SHAP figures were `NOT_COMPUTED` because the 7626505158 byte `auth.txt.gz` could not be streamed to completion.

## check_gates.py Result
Enforced gates (c)–(f) passed; gates (a), (g), (h), (i) are N/A in fallback mode

The methodology has not been validated on authentic LANL data in this environment.
