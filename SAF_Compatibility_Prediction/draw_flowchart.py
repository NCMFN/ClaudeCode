import graphviz

dot = graphviz.Digraph('AlgorithmFlowchart', comment='SAF Compatibility Prediction Flowchart')
dot.attr(rankdir='TB', size='10,12')
dot.attr('node', fontname='Helvetica', shape='box', style='filled', fillcolor='white')

# Nodes
dot.node('Start', 'Start', shape='ellipse', fillcolor='palegreen', style='filled,bold')
dot.node('Input', 'Input: Raw Dataset\n(SAF Features)', shape='parallelogram', fillcolor='lemonchiffon', style='filled,bold')
dot.node('Preprocess', 'Data Preprocessing\n(Missing Values, Standardization)', fillcolor='lightblue', style='filled,bold')
dot.node('Split', 'Train-Test Split & SMOTE\n(Class Balancing)', fillcolor='lightblue', style='filled,bold')
dot.node('Train', 'Model Training\n(LogReg, RF, XGBoost, NN)', fillcolor='navajowhite', style='filled,bold')
dot.node('Evaluate', 'Model Evaluation\n(Metrics & SHAP)', fillcolor='pink', style='filled,bold')
dot.node('Decision', 'Is Model\nOptimal?', shape='diamond', fillcolor='lightcoral', style='filled,bold')
dot.node('Tune', 'Hyperparameter Tuning\n(GridSearchCV)', fillcolor='plum', style='filled,bold')
dot.node('Output', 'Output: Prediction via\nStreamlit App', shape='parallelogram', fillcolor='lemonchiffon', style='filled,bold')
dot.node('End', 'End', shape='ellipse', fillcolor='palegreen', style='filled,bold')

# Edges
dot.edge('Start', 'Input')
dot.edge('Input', 'Preprocess')
dot.edge('Preprocess', 'Split')
dot.edge('Split', 'Train')
dot.edge('Train', 'Evaluate')
dot.edge('Evaluate', 'Decision')

# Decision edges
dot.edge('Decision', 'Tune', label=' No', fontname='Helvetica', fontcolor='red', color='red')
dot.edge('Tune', 'Train', color='red') # Feedback loop

dot.edge('Decision', 'Output', label=' Yes', fontname='Helvetica', fontcolor='darkgreen', color='darkgreen')
dot.edge('Output', 'End')

# Render
output_path = '/app/SAF_Compatibility_Prediction/images/system_architecture'
dot.render(output_path, format='png', cleanup=True)
print(f"Flowchart successfully generated at {output_path}.png")
