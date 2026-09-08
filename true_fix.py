import re
with open('run_pipeline.py', 'r') as f:
    content = f.read()

# Models & APC
save_models_code = """
    for name, model in models.items():
        joblib.dump(model, f'outputs/models/trained_{name.replace(" ", "")}.pkl')
"""
content = content.replace("joblib.dump(best_model, f'outputs/models/best_model_{best_model_name.replace(\" \",\"\")}.pkl')", save_models_code + "\n    joblib.dump(best_model, f'outputs/models/best_model_{best_model_name.replace(\" \",\"\")}.pkl')")

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
        # replace the last quote before a closing parenthesis or comma
        if line.endswith("')"):
            line = line[:-2] + ". Source: WSN_Dataset')"
        elif line.endswith("', y=1.02)"):
            line = line[:-10] + ". Source: WSN_Dataset', y=1.02)"
        elif "')" in line:
            # this is robust for lines like `plt.title('Figure 36: SHAP Summary Plot')`
            # find last `')`
            idx = line.rfind("')")
            if idx != -1:
                line = line[:idx] + ". Source: WSN_Dataset" + line[idx:]
    new_lines.append(line)

content = '\n'.join(new_lines)

with open('run_pipeline.py', 'w') as f:
    f.write(content)
