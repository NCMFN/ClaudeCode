import os
fig_dir = "outputs/figures"
expected_figs = [f"Figure_{i}_" for i in range(1, 53)]
found = os.listdir(fig_dir) if os.path.isdir(fig_dir) else []
missing = [f for f in expected_figs if not any(name.startswith(f) for name in found)]
print(f"Figures found: {len(found)} / {len(expected_figs)} expected")
print(f"Missing: {missing}")
zero_byte = [f for f in found if os.path.getsize(os.path.join(fig_dir, f)) == 0]
print(f"Zero-byte files (treat as missing): {zero_byte}")

if missing or zero_byte:
    print("FAILED AUDIT")
else:
    print("AUDIT PASSED")
