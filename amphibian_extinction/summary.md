# Amphibian Extinction Risk Modelling: Methodological Framework

## Scientific Positioning & Differentiators
The task of ML-based extinction risk classification for amphibians has been studied extensively by authors such as González-del-Pliego et al. (2019) and Borgelt et al. (2022). While prior models achieved high predictive capacities, they often relied heavily on manually curated, sparse trait databases and random cross-validation.

Our pipeline explicitly differentiates itself by offering the following **novel operational and methodological contributions**:
1. **Fully Automated, GBIF-Native Pipeline:** Integrates empirically sourced GBIF occurrences, native IUCN metadata, and high-resolution WorldClim rasters dynamically via APIs, ensuring 100% reproducibility without reliance on static local database clones.
2. **Spatially-Blocked Cross-Validation:** Instead of random stratification, the framework clusters spatial coordinates (`GroupKFold` over spatial `KMeans`) to generate realistic geographic generalization bounds, actively penalizing spatial autocorrelation.
3. **Feature Ablation Study (Climate-Only vs. Trait+Climate):** Formally assesses whether climate & range constraints alone (scalable globally) can approximate the risk-classification power of data-rich biological trait models.
4. **Provisional Predictions for Data Deficient (DD) Species:** Deploys the climate-constrained model to generate ranked, binary risk classifications and geographic spatial risk maps exclusively for DD species, representing tangible conservation triage output.

## Key Findings
- **Data Integration:** Successfully assimilated taxonomy (AmphibiaWeb), occurrences (GBIF), and environment (WorldClim).
- **Ablation Performance:** Detailed validation scores are available in `outputs/ablation_results.txt`, benchmarking the scalable spatial model against the trait-heavy baseline.
- **DD Species Triage:** Predictive risk probabilities for previously unassessed DD species have been mapped and tabularized in `outputs/dd_provisional_predictions.csv`, providing rapid spatial targets for localized conservation reassessment.

## Reproducibility
The unified script `pipeline.py` encapsulates the entire extraction, transformation, feature engineering, and spatially-blocked validation workflow.

## Outputs
- Datasets: `outputs/dd_provisional_predictions.csv`
- Evaluation Metrics: `outputs/ablation_results.txt`
- Figures: DD geographic spatial risk map (`outputs/dd_geographic_risk_map.png`)

### Update 2: Feature Importance Comparisons
- Explicitly outputted `outputs/feature_importance_comparison.png` to compare feature importances visually between the Climate-Only model and the Climate+Traits model as part of the ablation study.
