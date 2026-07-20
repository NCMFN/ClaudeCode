with open("src/phase3_modeling.py", "r") as f:
    content = f.read()

# Remove the artificial label injection code
new_content = content.replace("""    if df['label'].nunique() < 2:
        print("Only 1 class found in total data, artificially injecting malicious labels for pipeline test.")
        df.loc[df.index[:50], 'label'] = 'malicious'
        df.loc[df.index[-50:], 'label'] = 'malicious'""", "")

new_content = new_content.replace("""    if grouped_df['label_bin'].nunique() < 2:
        print("After grouping, only 1 class found, artificially injecting malicious labels.")
        grouped_df.loc[grouped_df.index[:10], 'label_bin'] = 1
        grouped_df.loc[grouped_df.index[-10:], 'label_bin'] = 1""", "")

new_content = new_content.replace("""    if len(np.unique(y_train)) < 2:
        print("Train split only has 1 class, injecting artificial malicious cases...")
        y_train[:5] = 1""", "")

# Adjust prediction threshold for meta_clf
new_content = new_content.replace("""    meta_probs_test = meta_clf.predict_proba(X_meta_test)[:, 1]""", """    meta_probs_test = meta_clf.predict_proba(X_meta_test)[:, 1]

    # Adjust prediction threshold to prioritize recall
    y_pred_adjusted = (meta_probs_test >= 0.05).astype(int)
""")

with open("src/phase3_modeling.py", "w") as f:
    f.write(new_content)
