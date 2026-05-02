import graphviz

# Create a Digraph object
dot = graphviz.Digraph(comment='SAF Compatibility Prediction Flowchart', format='png')
dot.attr(rankdir='TB', size='10,12')
dot.attr('node', fontname='Helvetica', shape='box', style='filled', fillcolor='white')

# Define nodes with appropriate shapes and colors
dot.node('start', 'Start', shape='ellipse', fillcolor='palegreen')
dot.node('input', 'Input: Raw Dataset\n(SAF Features)', shape='parallelogram', fillcolor='lemonchiffon')
dot.node('prep', 'Data Preprocessing\n(Missing Values, Standardization)', shape='box', fillcolor='lightblue')
dot.node('split', 'Train-Test Split & SMOTE\n(Class Balancing)', shape='box', fillcolor='lightblue')
dot.node('train', 'Model Training\n(LogReg, RF, XGBoost, NN)', shape='diamond', fillcolor='moccasin')
dot.node('tune', 'Hyperparameter Tuning\n(GridSearchCV on XGBoost)', shape='box', fillcolor='plum')
dot.node('eval', 'Model Evaluation &\nSHAP Interpretation', shape='box', fillcolor='pink')
dot.node('decision', 'Performance\nMet?', shape='diamond', fillcolor='lightgoldenrod')
dot.node('output', 'Output: Prediction via\nStreamlit App', shape='parallelogram', fillcolor='lemonchiffon')
dot.node('end', 'End', shape='ellipse', fillcolor='palegreen')

# Define edges
dot.edge('start', 'input')
dot.edge('input', 'prep')
dot.edge('prep', 'split')
dot.edge('split', 'train')
dot.edge('train', 'tune')
dot.edge('tune', 'eval')
dot.edge('eval', 'decision')

# Decision edges
dot.edge('decision', 'output', label='Yes', fontcolor='green', color='green', penwidth='2')
dot.edge('decision', 'tune', label='No', fontcolor='red', color='red', penwidth='2')
# Adding a bi-directional conceptual loop if requested, but a standard 'No' back to tuning works well.

dot.edge('output', 'end')

# Add graph label
dot.attr(label='Algorithm Flowchart for SAF Compatibility Prediction\n', labelloc='t', fontsize='20', fontname='Helvetica-Bold')

# Render the graph
dot.render('saf_flowchart', cleanup=True)
print("Flowchart successfully generated as saf_flowchart.png")
