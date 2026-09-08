import re

with open('run_pipeline.py', 'r') as f:
    content = f.read()

# Cleanly append "Source: WSN_Dataset" inside the quotes.
def add_source(match):
    prefix = match.group(1) # The string start (e.g. "ax.set_title('Figure...")
    # Find the last quote in the matched string

    # We can just match the content inside the set_title call
    return match.group(0)

# Replace simple titles
content = re.sub(r"set_title\('([^']+)'\)", r"set_title('\1. Source: WSN_Dataset')", content)
content = re.sub(r"plt\.title\('([^']+)'\)", r"plt.title('\1. Source: WSN_Dataset')", content)
content = re.sub(r"suptitle\('([^']+)'", r"suptitle('\1. Source: WSN_Dataset'", content)

# Replace f-string titles
content = re.sub(r"set_title\(f'([^']+)'\)", r"set_title(f'\1. Source: WSN_Dataset')", content)
content = re.sub(r"plt\.title\(f'([^']+)'\)", r"plt.title(f'\1. Source: WSN_Dataset')", content)

# Fix double additions if any
content = content.replace(". Source: WSN_Dataset. Source: WSN_Dataset", ". Source: WSN_Dataset")

# Save all models
save_models_code = """
    for name, model in models.items():
        joblib.dump(model, f'outputs/models/trained_{name.replace(" ", "")}.pkl')
"""
content = content.replace("joblib.dump(best_model, f'outputs/models/best_model_{best_model_name.replace(\" \",\"\")}.pkl')", save_models_code + "\n    joblib.dump(best_model, f'outputs/models/best_model_{best_model_name.replace(\" \",\"\")}.pkl')")

# Output APC DataFrame
apc_code = """
    sim_df['Adjusted_Pred'] = best_model.predict(adjusted_X_test)

    # Export APC DataFrame
    apc_export_df = pd.DataFrame({
        'Node_ID': raw_df_test['Node_ID'] if 'Node_ID' in raw_df_test.columns else sim_df.index,
        'Initial_Accuracy_Pred': sim_df['Initial_Pred'],
        'APC_Triggered': sim_df['APC_Triggered'],
        'Adjusted_Accuracy_Pred': sim_df['Adjusted_Pred']
    })
    apc_export_df.to_csv('outputs/datasets/apc_simulation.csv', index=False)
"""
content = content.replace("    sim_df['Adjusted_Pred'] = best_model.predict(adjusted_X_test)", apc_code)

# One specific fix for "Figure 7: Histogram - Detection Accuracy (%)" which has parentheses inside
with open('run_pipeline.py', 'w') as f:
    f.write(content)
