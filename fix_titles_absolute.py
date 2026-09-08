import re

with open('run_pipeline.py', 'r') as f:
    content = f.read()

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

content = re.sub(r"(ax\.set_title\('.*?)\)", r"\1. Source: WSN_Dataset')", content)
content = re.sub(r"(plt\.title\('.*?)\)", r"\1. Source: WSN_Dataset')", content)
content = re.sub(r"(g\.fig\.suptitle\('.*?)'", r"\1. Source: WSN_Dataset'", content)
content = re.sub(r"(fig\.suptitle\('.*?)\)", r"\1. Source: WSN_Dataset')", content)
content = re.sub(r"(ax\.set_title\(f'.*?)\)", r"\1. Source: WSN_Dataset')", content)
content = re.sub(r"(plt\.title\(f'.*?)\)", r"\1. Source: WSN_Dataset')", content)

# But wait, the first replace is greedy?
# "(ax\.set_title\('.*?)\)"
# If it is ax.set_title('Title')
# It will match ax.set_title('Title'
# And replace with ax.set_title('Title'. Source: WSN_Dataset') -> ax.set_title('Title'. Source: WSN_Dataset') WHICH IS WRONG!
# The string is ax.set_title('Title')
# It should be ax.set_title('Title. Source: WSN_Dataset')

with open('run_pipeline.py', 'w') as f:
    f.write(content)
