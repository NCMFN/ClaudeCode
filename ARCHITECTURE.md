# Soil Nutrient Forecasting Framework Architecture

This diagram illustrates the end-to-end data processing and machine learning pipeline, designed to predict soil nutrient levels (specifically Nitrogen) from raw microbiome sequencing data and environmental metadata.

```mermaid
graph TD
    classDef plain fill:transparent,stroke:none,color:#000

    subgraph Data Acquisition
        EMP[Earth Microbiome Project<br>FTP/Zenodo<br>16S rRNA Sequences]
        NEON[NEON Data Products<br>REST API<br>Soil Chemistry Ground Truth]
    end

    subgraph Preprocessing & Engineering
        FE[Feature Engineering<br>- Filter Soil Samples<br>- Parse BIOM Matrix<br>- CLR Transformation<br>- PCA Reduction (150 comp)<br>- Alpha Diversity]
        DI[Data Integration<br>Proximity & Seasonal Merge]
    end

    subgraph Model Development
        MD[Machine Learning Models<br>- Random Forest Regressor<br>- Gradient Boosting<br>- Ridge Regression<br><br>*Spatial Block Cross-Validation]
    end

    subgraph Evaluation & Output
        EVAL[Model Evaluation<br>- RMSE, MAE, R2<br>- 95% Prediction Intervals]
        REPORT[Reporting<br>Kaggle-structured Notebook]
    end

    %% Flow Definitions
    EMP --> FE
    NEON --> DI
    FE --> DI
    DI -- "Joined Matrix (X,y)" --> MD
    MD --> EVAL
    EVAL --> REPORT

    class EMP plain
    class NEON plain
    class FE plain
    class DI plain
    class MD plain
    class EVAL plain
    class REPORT plain
```
