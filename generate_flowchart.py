from graphviz import Digraph

dot = Digraph('flowchart', format='png')
dot.attr(rankdir='TB', nodesep='0.6', ranksep='0.6', dpi='300')

# Default node and edge styling to match the sample
dot.attr('node', fontname='Arial', fontsize='12', shape='box', style='filled', color='black', penwidth='1.5')
dot.attr('edge', fontname='Arial', fontsize='10', arrowhead='normal', color='black', penwidth='1.5')

# Specific node styles mapped from the sample diagram
style_start = {'shape': 'oval', 'fillcolor': '#a8e6cf'} # Light green
style_input = {'shape': 'parallelogram', 'fillcolor': '#fff2cc'} # Light yellow
style_process = {'shape': 'box', 'fillcolor': '#add8e6'} # Light blue
style_train = {'shape': 'box', 'fillcolor': '#f5deb3'} # Wheat / Light Orange
style_eval = {'shape': 'box', 'fillcolor': '#ffb6c1'} # Light pink
style_decision = {'shape': 'diamond', 'fillcolor': '#f08080'} # Light Coral / Salmon
style_tune = {'shape': 'box', 'fillcolor': '#dda0dd'} # Plum / Light Purple

# --- Nodes based on the ORIGINAL flowchart, but using SAMPLE styles ---

# Start Node
dot.node('start', 'Start', **style_start)

# The first row of original flowchart
dot.node('collect', 'Collect historical price\ndata for the selected\ncryptocurrency', **style_input)
dot.node('analysis', 'Perform Market\nAnalysis', **style_process)
dot.node('buy', 'Decision\nto buy', **style_decision)
dot.node('drop', 'Drop', **style_process)

# Exchange row
dot.node('exchange', 'Choose a Cryptocurrency\nExchange', **style_process)
dot.node('account', 'Create an\nAccount', **style_process)
dot.node('fund', 'Fund the\nAccount', **style_process)
dot.node('order', 'Place an Order', **style_process)

# Pool
dot.node('pool', 'Pool of cryptocurrencies', **style_process)

# Wavelet
dot.node('wavelet', 'Wavelet Analysis (DWT, MWT, Wavelet Coherence)', **style_process)

# Intensity Decision
dot.node('intensity', 'Assess frequency\nintensity', **style_decision)

# Portfolios (Mapped to tuning/training style)
dot.node('short', 'Short term portfolio', **style_tune)
dot.node('medium', 'Medium Term Portfolio', **style_tune)
dot.node('long', 'Long Term Horizon', **style_tune)

# Risk Analysis (Mapped to Eval style)
dot.node('risk', 'Risk Analysis', **style_eval)

# Sell Criteria
dot.node('sell_crit', 'Meet\nSelling\nCriteria', **style_decision)

# Sell (Mapped to output/input style)
dot.node('sell', 'SELL', **style_input)

# Relevant Decision
dot.node('relevant', 'Relevant', **style_decision)

# Exit
dot.node('exit', 'Exit', **style_start)


# --- Edges ---
dot.edge('start', 'collect')
dot.edge('collect', 'analysis')
dot.edge('analysis', 'buy')

# Buy branch
dot.edge('buy', 'drop', label='No', fontcolor='red', color='red')
dot.edge('buy', 'exchange', label='Yes', fontcolor='green', color='green')

dot.edge('exchange', 'account')
dot.edge('account', 'fund')
dot.edge('fund', 'order')
dot.edge('order', 'pool')

dot.edge('pool', 'wavelet')

dot.edge('wavelet', 'intensity')

dot.edge('intensity', 'short', label='Period 64 to 256')
dot.edge('intensity', 'medium', label='Period 8 to 32')
dot.edge('intensity', 'long', label='Period 0 to 8')

dot.edge('short', 'risk')
dot.edge('medium', 'risk')
dot.edge('long', 'risk')

dot.edge('risk', 'sell_crit')

dot.edge('sell_crit', 'sell', label='Yes', fontcolor='green', color='green')
dot.edge('sell_crit', 'relevant', label='No', fontcolor='red', color='red')

dot.edge('relevant', 'wavelet', label='Yes', fontcolor='green', color='green')
dot.edge('relevant', 'exit', label='No', fontcolor='red', color='red')

dot.render('flowchart_like_sample')
