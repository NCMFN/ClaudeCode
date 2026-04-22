import graphviz
import os

def create_architecture():
    # Create a new directed graph
    dot = graphviz.Digraph(format='png')
    dot.attr(rankdir='TB')  # Top to Bottom vertical flow
    dot.attr(dpi='400')
    dot.attr('node', shape='box', style='solid', fontname='Arial', fontsize='12', margin='0.3,0.2')

    # Root level Data sources
    dot.node('A', 'Earth Microbiome Project\n(EMP Zenodo Archive)')
    dot.node('B', 'NEON Soil Microbe Data\n(REST API)')

    # Data Processing
    dot.node('C', 'Data Preprocessing\nFilter to Study Area (Soil)')
    dot.node('D', 'Feature Engineering')

    # Feature extraction split
    dot.node('E', '16S rRNA Sequences\nTaxonomic Resolution & CLR')
    dot.node('F', 'Alpha Diversity Proxies\n(Shannon, Simpson)')

    # Construction / Integration
    dot.node('G', 'Composite Construction\nTop 150 Taxa + Covariates')
    dot.node('H', 'Target Variable Integration\nTotal Soil Nitrogen')

    # ML Models
    dot.node('I', 'Model Training & CV\n(Spatial Block K-Fold)')

    dot.node('J', 'Null Baseline\n(DummyRegressor)')
    dot.node('K', 'Random Forest Regressor')
    dot.node('L', 'Gradient Boosting Regressor')
    dot.node('M', 'Ridge Regression')

    # Ground truth validation node (side dependency)
    dot.node('N', 'NEON Validation Points\nGround Truth (Holdout)', style='solid')

    # Evaluation
    dot.node('O', 'Evaluation & SHAP')

    # Outputs
    dot.node('P', 'Outputs\nFigures & Metrics')

    # Define edges based on the image's flow style
    # A -> C
    dot.edge('A', 'C')
    # B doesn't strictly flow into C in the preprocessing stage yet but supplies truth later or co-location

    # C -> D
    dot.edge('C', 'D')

    # D -> E and D -> F
    dot.edge('D', 'E')
    dot.edge('D', 'F')

    # E -> G and F -> G
    dot.edge('E', 'G')
    dot.edge('F', 'G')

    # G -> H
    dot.edge('G', 'H')

    # H -> I
    dot.edge('H', 'I')

    # I -> ML models
    dot.edge('I', 'J')
    dot.edge('I', 'K')
    dot.edge('I', 'L')
    dot.edge('I', 'M')

    # ML Models -> Evaluation
    dot.edge('J', 'O')
    dot.edge('K', 'O')
    dot.edge('L', 'O')
    dot.edge('M', 'O')

    # N -> O (Ground truth into evaluation as a dotted line or separate feed)
    dot.edge('N', 'O', style='dotted')

    # O -> P
    dot.edge('O', 'P')

    # Render to file
    output_path = 'system_architecture'
    dot.render(output_path, cleanup=True)
    print("Graphviz diagram generated as system_architecture.png")

if __name__ == "__main__":
    create_architecture()
