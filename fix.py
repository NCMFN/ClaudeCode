with open("scripts/03_model_training.py", "r") as f:
    lines = f.readlines()
for i, line in enumerate(lines):
    if "X_train_opt, y_train_opt = X_opt.iloc[" in line:
        lines[i] = "        X_train_opt, y_train_opt = X_opt.iloc[train_idx_opt], y_opt.iloc[train_idx_opt]\n"
    if "X_test_opt, y_test_opt = X_opt.iloc[" in line:
        lines[i] = "        X_test_opt, y_test_opt = X_opt.iloc[test_idx_opt], y_opt.iloc[test_idx_opt]\n"
with open("scripts/03_model_training.py", "w") as f:
    f.writelines(lines)
