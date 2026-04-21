import subprocess
import os

# Create mermaid file
mermaid_code = """
graph LR
    classDef plain fill:transparent,stroke:none,color:#000

    subgraph Inputs
    A[data/]
    end

    subgraph Transformations
    B(src/data_loader.py)
    C(src/feature_engineering.py)
    D(src/preprocessing.py)
    end

    subgraph Learning
    E{src/models.py<br>XGBoost/IsolationForest}
    F{src/evaluation.py<br>Baselines}
    end

    subgraph Interpreters
    G(src/trust_score.py)
    H(src/shap_analysis.py)
    end

    subgraph Sink [outputs/]
    O_DL[outputs/data_loader/]
    O_FE[outputs/feature_engineering/]
    O_MOD[outputs/models/]
    O_EVAL[outputs/evaluation/]
    O_TS[outputs/trust_score/]
    O_SHAP[outputs/shap_analysis/]
    O_MAIN[outputs/main/]
    O_MAN[manifest.txt]
    end

    A -->|Ingest| B
    B -->|Cleaned DataFrame| C
    C -->|Feature Set| D
    D -->|X_train_sm, X_val, X_test| E
    D -->|X_train_sm, X_train| F

    E -->|Predictions / Probas| F
    E -->|Model & Probas| G
    E -->|XGB Model| H

    B -.->|Save| O_DL
    C -.->|Save| O_FE
    E -.->|Save| O_MOD
    F -.->|Save| O_EVAL
    G -.->|Save| O_TS
    H -.->|Save| O_SHAP

    O_DL -.-> O_MAN
    O_FE -.-> O_MAN
    O_MOD -.-> O_MAN
    O_EVAL -.-> O_MAN
    O_TS -.-> O_MAN
    O_SHAP -.-> O_MAN
"""

with open("architecture.mmd", "w") as f:
    f.write(mermaid_code)

try:
    subprocess.run(["npx", "mmdc", "-i", "architecture.mmd", "-o", "architecture.png"], check=True)
    print("architecture.png generated successfully.")
except subprocess.CalledProcessError as e:
    print(f"Error generating diagram: {e}")
except FileNotFoundError:
    print("npx/mmdc not found. Trying fallback generation.")
