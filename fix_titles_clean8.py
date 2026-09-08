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

lines = content.split('\n')
new_lines = []
for line in lines:
    if "set_title" in line or "plt.title" in line or "suptitle" in line:
        if "Source: WSN_Dataset" not in line:
            # We want to replace the LAST single quote in the line, but wait, some lines have 'Figure 1...'.
            # It's always two quotes: `ax.set_title('Some title')`
            # Just split by single quote and join? No, let's just do a manual string manipulation

            # Find the closing parenthesis
            close_paren_idx = line.rfind(")")
            # Find the quote right before it (ignoring spaces)
            # Actually, the string literal ends with a quote. Let's just find the last quote before the last parenthesis.
            last_quote_idx = line[:close_paren_idx].rfind("'")
            if last_quote_idx != -1:
                line = line[:last_quote_idx] + ". Source: WSN_Dataset" + line[last_quote_idx:]
    new_lines.append(line)

content = '\n'.join(new_lines)

with open('run_pipeline.py', 'w') as f:
    f.write(content)
