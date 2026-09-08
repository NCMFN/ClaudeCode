with open('run_pipeline.py', 'r') as f:
    content = f.read()

# I need to move the apc_export_df logic below where raw_df_test is defined
# Or just use sim_df.index
apc_code_old = """
    # Export APC DataFrame
    apc_export_df = pd.DataFrame({
        'Node_ID': raw_df_test['Node_ID'] if 'Node_ID' in raw_df_test.columns else sim_df.index,
        'Initial_Accuracy_Pred': sim_df['Initial_Pred'],
        'APC_Triggered': sim_df['APC_Triggered'],
        'Adjusted_Accuracy_Pred': sim_df['Adjusted_Pred']
    })
    apc_export_df.to_csv('outputs/datasets/apc_simulation.csv', index=False)
"""
apc_code_new = """
    # Export APC DataFrame
    apc_export_df = pd.DataFrame({
        'Node_ID': sim_df.index,
        'Initial_Accuracy_Pred': sim_df['Initial_Pred'],
        'APC_Triggered': sim_df['APC_Triggered'],
        'Adjusted_Accuracy_Pred': sim_df['Adjusted_Pred']
    })
    apc_export_df.to_csv('outputs/datasets/apc_simulation.csv', index=False)
"""
content = content.replace(apc_code_old, apc_code_new)
with open('run_pipeline.py', 'w') as f:
    f.write(content)
