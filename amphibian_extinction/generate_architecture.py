import subprocess
import os

mermaid_code = """
graph TD
    classDef plain fill:transparent,stroke:none,color:#000

    A[Data Ingestion Layer] -->|Download & Extract| B(AmphiBIO Dataset)
    A -->|GBIF API Queries| C(Species Occurrences & IUCN Status)
    A -->|Download Rasters| D(WorldClim Climate Data)

    B --> E[Data Processing Pipeline]
    C --> E
    D --> E

    E -->|Raster Sampling & Merging| F(Feature Engineering)
    F -->|Imputation & Scaling| G(Data Splitting & Class Imbalance Handling)

    G -->|SMOTE Oversampling| H[Model Training Layer]
    H -->|Train & Tune| I(Random Forest)
    H -->|Train & Tune| J(XGBoost)
    H -->|Train| K(Deep Neural Network - Keras)

    I --> L[Evaluation & Visualization Layer]
    J --> L
    K --> L

    L --> M(Feature Importance)
    L --> N(ROC-AUC Curves)
    L --> O(Confusion Matrix)

    class A,E,H,L plain
"""

with open('outputs/architecture.mmd', 'w') as f:
    f.write(mermaid_code)

print("Saved architecture.mmd. Use mermaid-cli to generate PNG if installed, otherwise mmd is ready.")
