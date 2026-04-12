import graphviz

dot = graphviz.Digraph(comment='Bionic Mushroom Energy Harvest Flowchart', format='png')
dot.attr(rankdir='TB', size='10,12')
dot.attr('node', fontname='Helvetica', shape='box', style='filled')

# Nodes
dot.node('start', 'Start', shape='ellipse', fillcolor='lightgrey')
dot.node('acquire', 'Data Acquisition\nLoad/Simulate Dataset\n(Light, Humidity, Bacterial Density,\nCurrent Density)', fillcolor='lightblue')
dot.node('preprocess', 'Data Preprocessing\n- Handle Missing Values\n- Feature Scaling\n- Create Interaction Features', fillcolor='palegreen')
dot.node('prep_check', 'Preprocessing Quality\nInsufficient?', shape='diamond', fillcolor='lightgoldenrod')
dot.node('split', 'Train-Test Split', fillcolor='khaki')

# Subgraph for parallel training to enforce layout
with dot.subgraph(name='cluster_training') as c:
    c.attr(style='invis')
    c.node('train_lr', 'Train\nLinear Regression', fillcolor='moccasin')
    c.node('train_rf', 'Train & Tune\nRandom Forest', fillcolor='moccasin')
    c.node('train_nn', 'Train\nNeural Network', fillcolor='moccasin')

dot.node('eval', 'Model Evaluation\n(RMSE, MAE, R²)', fillcolor='plum')
dot.node('eval_check', 'Model Performance\nAcceptable?', shape='diamond', fillcolor='lightgoldenrod')
dot.node('output', 'Select Best Model\n& Output Predictions', fillcolor='pink')
dot.node('deploy_check', 'Deployment Performance\nDegrades?', shape='diamond', fillcolor='lightgoldenrod')

# Edges (Main flow)
dot.edge('start', 'acquire')
dot.edge('acquire', 'preprocess')
dot.edge('preprocess', 'prep_check')

# Preprocessing Feedback Loop
dot.edge('prep_check', 'split', label='No', color='green', fontcolor='green')
dot.edge('prep_check', 'acquire', label='Yes', color='red', fontcolor='red')

# Split to Training
dot.edge('split', 'train_lr')
dot.edge('split', 'train_rf')
dot.edge('split', 'train_nn')

# Training to Eval
dot.edge('train_lr', 'eval')
dot.edge('train_rf', 'eval')
dot.edge('train_nn', 'eval')

# Eval Decision
dot.edge('eval', 'eval_check')
dot.edge('eval_check', 'output', label='Yes', color='green', fontcolor='green')

# Eval Feedback Loops
# Bi-directional arrows indicated by user: Evaluation <-> Model Training, Evaluation <-> Preprocessing
# We implement the "No" paths mapping to those loops.
dot.edge('eval_check', 'train_rf', label='No (Retune)', color='red', fontcolor='red', constraint='false')
dot.edge('eval_check', 'preprocess', label='No (Refine Features)', color='red', fontcolor='red', constraint='false')

# Bi-directional indicated loops
dot.edge('train_rf', 'eval', dir='both', label='Train <-> Eval loop', color='purple', style='dashed', constraint='false')
dot.edge('preprocess', 'eval', dir='both', label='Preproc <-> Eval loop', color='purple', style='dashed', constraint='false')

# Final Deployment Loop
dot.edge('output', 'deploy_check')
dot.edge('deploy_check', 'split', label='Yes (Retrain)', color='red', fontcolor='red', constraint='false')

# Title
dot.attr(label='Bionic Mushroom Energy Harvest - Advanced Flowchart Algorithm\n', labelloc='t', fontsize='20', fontname='Helvetica-Bold')

# Render
dot.render('bionic_mushroom_flowchart', cleanup=True)
print("Flowchart generated as bionic_mushroom_flowchart.png")
