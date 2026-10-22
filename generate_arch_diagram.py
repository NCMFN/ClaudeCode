import graphviz
import os

def create_architecture_diagram():
    # Use graphviz to generate a diagram matching the exact layout
    # of the user's provided sample image, but with the content
    # for the ALBAN / DePIN project.

    # Original image structure mapping:
    # B2B Cisco Ariel API -> IoT-Enabled Smart Grid Dataset
    # API Gateway -> Autonomous Device-Side FSM
    # Authentication: Block -> State S4: Primary-Only
    # Authentication: Pass -> States S1-S3: Blockchain Active
    # Malicious Traffic Database -> Primary Task Execution (Invariant)
    # Feature Extraction -> Battery SoC Monitoring
    # Random Forest Anomaly Detection -> Hysteresis Threshold Evaluation (60/35/15)
    # Clean Traffic -> S1: Full Light Node
    # Anomalies Detected -> S2/S3: Degraded Modes
    # API Backend / Endpoint -> All Blockchain Ops (Sign, Relay, Submit)
    # Threat Logs -> Partial Blockchain Ops (Sign/Submit or Relay Only)
    # Database -> Primary Task Execution (Invariant)
    # SIEM / Syslog API -> Proofs (PoC/PoU) Generation
    # Cisco Ariel Splunk Database -> Simulation Engine (SimPy)
    # Application Performance Monitoring -> Battery Lifetime Analysis
    # SIEM Integration -> FSM State Transitions
    # Traffic Heatmap Analytics -> Statistical Validation

    dot = graphviz.Digraph('Architecture', format='png')
    dot.attr(rankdir='TB', nodesep='0.5', ranksep='0.7')

    # Global matplotlib-like DPI standard as per memory guidelines
    dot.attr(dpi='300')

    # Node styling matching the sample image exactly
    dot.attr('node', shape='box', style='rounded,filled', fillcolor='#f0f0ff',
             color='#d0d0f0', fontname='Helvetica', fontsize='11', height='0.6')
    dot.attr('edge', color='#555555')

    # Define Nodes matching the sample image topology
    dot.node('n1', 'IoT-Enabled Smart Grid Dataset')
    dot.node('n2', 'Autonomous Device-Side FSM')

    dot.node('n3_left', 'State S4: Primary-Only\n(SoC <= 15%)', fillcolor='#888780', fontcolor='white')
    dot.node('n3_right', 'States S1-S3: Blockchain Active\n(SoC > 15%)')

    dot.node('n4_left', 'Primary Task Execution\n(Invariant)')

    dot.node('n4_right', 'Battery SoC Monitoring')

    dot.node('n5', 'Hysteresis Threshold Evaluation\n(60 / 35 / 15)', height='0.8')

    dot.node('n6_left', 'S1: Full Light Node\n(SoC > 60%)', fillcolor='#1D9E75', fontcolor='white')
    dot.node('n6_right', 'S2/S3: Degraded Modes\n(15% < SoC <= 60%)', fillcolor='#BA7517', fontcolor='white')

    dot.node('n7_left', 'All Blockchain Ops\n(Sign, Relay, Submit)')
    dot.node('n7_right', 'Partial Blockchain Ops\n(Sign/Submit or Relay Only)')

    dot.node('n8_left', 'Primary Task Execution\n(Invariant)')
    dot.node('n8_right', 'Proofs (PoC / PoU) Generation')

    dot.node('n9', 'Simulation Engine (SimPy)', height='0.8')

    dot.node('n10_left', 'Battery Lifetime Analysis', height='0.8')
    dot.node('n10_mid', 'FSM State Transitions')
    dot.node('n10_right', 'Statistical Validation')

    # Define Edges matching sample image topology EXACTLY
    dot.edge('n1', 'n2')

    # Split from Gateway equivalent
    dot.edge('n2', 'n3_left')
    dot.edge('n2', 'n3_right')

    # Left path
    dot.edge('n3_left', 'n4_left')

    # Right path
    dot.edge('n3_right', 'n4_right')
    dot.edge('n4_right', 'n5')

    # Split from Random Forest equivalent
    dot.edge('n5', 'n6_left')
    dot.edge('n5', 'n6_right')

    # Clean path equivalent
    dot.edge('n6_left', 'n7_left')
    dot.edge('n7_left', 'n8_left')

    # Anomalies path equivalent
    dot.edge('n6_right', 'n7_right')
    dot.edge('n7_right', 'n8_right')
    dot.edge('n8_right', 'n9')

    # Bottom splits
    dot.edge('n9', 'n10_left')
    dot.edge('n9', 'n10_mid')
    dot.edge('n9', 'n10_right')

    # Save the diagram
    os.makedirs('results/figures', exist_ok=True)

    # The instructions say: "All figures must be generated in both PNG (for submission) and PDF (for LaTeX inclusion)."
    # Also "All figures must be saved at 300 DPI as PNG and PDF."

    dot.render('results/figures/system_architecture', format='png', cleanup=True)
    dot.render('results/figures/system_architecture', format='pdf', cleanup=True)
    print("Generated results/figures/system_architecture.png")
    print("Generated results/figures/system_architecture.pdf")

if __name__ == '__main__':
    create_architecture_diagram()
