import graphviz

def create_architecture():
    # Create a new directed graph based heavily on CIR7.png vertical logic
    dot = graphviz.Digraph(format='png')
    dot.attr(rankdir='TB')  # Top to Bottom vertical flow
    dot.attr(dpi='400')
    dot.attr('node', shape='box', style='solid', fontname='Arial', fontsize='12', margin='0.3,0.2')

    # Root level Data sources
    dot.node('A', 'Earth Microbiome Project\n(EMP Zenodo Archive)')

    # Data Processing
    dot.node('C', 'Data Preprocessing\nFilter to Soil Samples')
    dot.node('D', 'Feature Engineering\n(Taxonomic Resolution & CLR)')

    # Feature extraction split
    dot.node('E', 'Biomarker Extraction\nTop 150 Taxa by Variance')
    dot.node('F', 'Alpha Diversity Proxies\n(Shannon, Simpson)')

    # Construction / Integration
    dot.node('G', 'Composite Construction')
    dot.node('H', 'Target Variable Integration\nTotal Soil Nitrogen\n(EMP & NEON Validation)')

    # ML Models
    dot.node('I', 'Model Training & CV\n(Spatial Block K-Fold)')

    dot.node('K', 'Random Forest')
    dot.node('L', 'Gradient Boosting')
    dot.node('M', 'Ridge Regression')

    # Evaluation
    dot.node('O', 'Evaluation & SHAP')

    # Null Baseline (side dependency check)
    dot.node('N', 'Null Baseline Check\n(DummyRegressor)', style='solid')

    # Outputs
    dot.node('P', 'Outputs\nFigures & Metrics')

    # Define edges based on the image's vertical flow style
    dot.edge('A', 'C')
    dot.edge('C', 'D')

    # D branching into E and F
    dot.edge('D', 'E')
    dot.edge('D', 'F')

    # E and F converging into G
    dot.edge('E', 'G')
    dot.edge('F', 'G')

    # Vertical descent
    dot.edge('G', 'H')
    dot.edge('H', 'I')

    # I branching into Models
    dot.edge('I', 'K')
    dot.edge('I', 'L')
    dot.edge('I', 'M')

    # Models converging into Evaluation
    dot.edge('K', 'O')
    dot.edge('L', 'O')
    dot.edge('M', 'O')

    # N feeding into O with a dotted line as per reference
    dot.edge('N', 'O', style='dotted')

    # Output
    dot.edge('O', 'P')

    output_path = 'system_architecture'
    dot.render(output_path, cleanup=True)
    print("Graphviz diagram generated as system_architecture.png")

if __name__ == "__main__":
    create_architecture()
