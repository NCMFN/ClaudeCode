import graphviz
import os

def create_architecture_diagram():
    # Use graphviz to generate a diagram resembling the user's provided sample

    # Global settings
    dot = graphviz.Digraph('Architecture', format='png')
    dot.attr(rankdir='TB', nodesep='0.5', ranksep='0.7')

    # Node styling
    dot.attr('node', shape='box', style='rounded,filled', fillcolor='#f0f0ff',
             color='#d0d0f0', fontname='Helvetica', fontsize='11', height='0.6')
    dot.attr('edge', color='#555555')

    # Define Nodes
    dot.node('b2b', 'B2B Cisco Ariel API')
    dot.node('gateway', 'API Gateway')

    dot.node('auth_block', 'Authentication: Block')
    dot.node('auth_pass', 'Authentication: Pass')

    dot.node('malicious_db', 'Malicious Traffic Database')

    dot.node('feature_ext', 'Feature Extraction')

    dot.node('rf_anomaly', 'Random Forest Anomaly\nDetection', height='0.8')

    dot.node('clean_traffic', 'Clean Traffic')
    dot.node('anomalies', 'Anomalies Detected')

    dot.node('api_backend', 'API Backend / Endpoint')
    dot.node('threat_logs', 'Threat Logs')

    dot.node('database', 'Database')
    dot.node('siem_api', 'SIEM / Syslog API')

    dot.node('splunk_db', 'Cisco Ariel Splunk\nDatabase', height='0.8')

    dot.node('apm', 'Application Performance\nMonitoring', height='0.8')
    dot.node('siem_integ', 'SIEM Integration')
    dot.node('heatmap', 'Traffic Heatmap Analytics')

    # Define Edges
    dot.edge('b2b', 'gateway')

    # Split from Gateway
    dot.edge('gateway', 'auth_block')
    dot.edge('gateway', 'auth_pass')

    # Block path
    dot.edge('auth_block', 'malicious_db')

    # Pass path
    dot.edge('auth_pass', 'feature_ext')
    dot.edge('feature_ext', 'rf_anomaly')

    # Split from RF Anomaly
    dot.edge('rf_anomaly', 'clean_traffic')
    dot.edge('rf_anomaly', 'anomalies')

    # Clean path
    dot.edge('clean_traffic', 'api_backend')
    dot.edge('api_backend', 'database')

    # Anomalies path
    dot.edge('anomalies', 'threat_logs')
    dot.edge('threat_logs', 'siem_api')
    dot.edge('siem_api', 'splunk_db')

    # Splunk splits
    dot.edge('splunk_db', 'apm')
    dot.edge('splunk_db', 'siem_integ')
    dot.edge('splunk_db', 'heatmap')

    # Save the diagram
    os.makedirs('results/figures', exist_ok=True)
    dot.render('results/figures/system_architecture_new', cleanup=True)
    print("Generated results/figures/system_architecture_new.png")

if __name__ == '__main__':
    create_architecture_diagram()
