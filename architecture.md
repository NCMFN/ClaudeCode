# System Architecture Flowchart

This diagram represents the end-to-end machine learning and optimization pipeline for analyzing and optimizing Sustainable Development Goals (SDGs) in policy documents, as derived from the provided Google Colab notebook.

## Flowchart Description

1. **Start**: The beginning of the pipeline.
2. **Input Data**: Raw datasets containing policy documents and surveys from NGOs and community feedback.
3. **Data Preprocessing**: Initial text cleaning, dealing with missing values, and translating diverse African languages into a common language (English).
4. **Feature Engineering**: NLP normalization and tokenization using NLTK to prepare the text for the classification model.
5. **Model Application**: Using a multi-label classification model (RoBERTA-Large) to map text segments to their relevant SDGs.
6. **System Evaluation**: Analyzing the SDG distributions, performing gap analysis, and detecting any policy conflicts or trade-offs.
7. **Decision Point (Is Policy Optimal?)**: Evaluating whether the current policy coverage meets the required thresholds and has no conflicts.
8. **Optimization**: If not optimal, applying Integer Linear Programming (ILP) solvers (like Branch-and-Bound) to iteratively formulate what-if scenarios and optimize the policy coverage.
9. **Output**: Once optimized, presenting the final predictions and recommendations via interactive dashboards and policy briefs.
10. **End**: The conclusion of the pipeline.

## Mermaid Diagram

```mermaid
graph TD
    classDef startEnd fill:#90EE90,stroke:#000,stroke-width:1px,color:#000;
    classDef inputOutput fill:#FFFACD,stroke:#000,stroke-width:1px,color:#000;
    classDef processBlue fill:#ADD8E6,stroke:#000,stroke-width:1px,color:#000;
    classDef processOrange fill:#FFDEAD,stroke:#000,stroke-width:1px,color:#000;
    classDef processPink fill:#FFB6C1,stroke:#000,stroke-width:1px,color:#000;
    classDef decisionRed fill:#F08080,stroke:#000,stroke-width:1px,color:#000;
    classDef processPurple fill:#DDA0DD,stroke:#000,stroke-width:1px,color:#000;

    Start([Start]):::startEnd
    Input[/Input: Raw Dataset <br/> Policy Docs & Surveys/]:::inputOutput
    Preprocess[Data Preprocessing <br/> Text Cleaning & Translation]:::processBlue
    FeatureEng[Feature Engineering <br/> NLP Tokenization & Lemmatization]:::processBlue
    Model[Classification Model <br/> RoBERTA-Large SDG Tagger]:::processOrange
    Eval[System Evaluation <br/> Gap Analysis & Conflicts]:::processPink
    Check{Is Policy <br/> Optimal?}:::decisionRed
    Tune[Optimization <br/> ILP Solvers & Scenarios]:::processPurple
    Output[/Output: Actionable Briefs <br/> & Dashboards/]:::inputOutput
    End([End]):::startEnd

    Start --> Input
    Input --> Preprocess
    Preprocess --> FeatureEng
    FeatureEng --> Model
    Model --> Eval
    Eval --> Check
    Check -->|Yes| Output
    Check -->|No| Tune
    Tune --> Model
    Output --> End

    linkStyle 6 stroke:#008000,stroke-width:2px;
    linkStyle 7 stroke:#FF0000,stroke-width:2px;
    linkStyle 8 stroke:#FF0000,stroke-width:2px;
```
