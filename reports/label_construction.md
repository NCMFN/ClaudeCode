# Label Construction Rules

State 0 (Normal): thermal elevation and efficiency within config-defined normal bands.
State 1 (Thermal Warning): thermal elevation exceeds config threshold but efficiency still nominal.
State 2 (Grid/Output Volatility): efficiency or power output deviates beyond config threshold without thermal cause.
State 3 (Failure proxy): near-zero AC output during expected generation hours (irradiation above config threshold) — proxy for inverter failure, since no hardware fault flag exists in this data.

**Note:** This is a heuristic label, not ground truth.
