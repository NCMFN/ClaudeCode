# Research Report: Dietary Exposure Risk and Blood Microplastic Loads

## 1. Introduction
This report outlines a data-driven approach to predicting biological Microplastic (MP) risk levels based on dietary and lifestyle metadata. Building on the research indicating the ubiquitous nature of MPs, our goal was to build a non-invasive screening tool to classify an individual's MP exposure risk (Negligible, Low, High).

## 2. Methodology
- **Data Preparation**: A dataset of 229 individuals was utilized. Missing values in fecal MP measures were imputed using median values to preserve data distribution. We engineered the target variable `Exposure_Risk` by splitting `Total_Blood_MP_ug_mL` into tertiles, successfully creating a balanced categorization of Negligible, Low, and High Risk.
- **Exploratory Data Analysis (EDA)**: Visualizations (correlation heatmaps, boxplots, distribution plots) were generated to understand trends, such as the log-linear relationship between bottled water consumption and MP loads in urban populations.
- **Modeling**: The dataset was one-hot encoded and standardized. We addressed class imbalances internally (although the tertile split provided a naturally balanced target, SMOTE was used during cross-validation to reinforce robust training boundaries). An XGBoost Classifier was optimized using Optuna with a focus on maximizing Sensitivity (Recall) for the "High Risk" class.

## 3. Hypothesis Testing & Research Alignment

### Hypothesis 1
*Hypothesis:* Individuals consuming >4 items of plastic-packaged processed food daily show a 70% higher probability of "High Risk" classification.
*Results:* We used `Packaging_Exposure_Score` as a proxy. While individuals with higher packaging exposure had an increased probability of being High Risk (38.60% vs 29.57%), the relative increase was ~30.55%, not 70%. Furthermore, the Chi-Square test yielded a p-value of 0.1928, meaning the difference is not statistically significant in this sample size.
*Conclusion:* Hypothesis 1 is **not statistically validated** by the current data.

### Hypothesis 2
*Hypothesis:* Fresh, plant-based diets serve as a predictive indicator for "Negligible" or "Low" MP load, regardless of urban proximity.
*Results:* The Pearson correlation between vegetable intake (`Veg_Intake_g_day`) and total blood MP was nearly zero (r = 0.0021, p = 0.9751). The mean vegetable intake for Negligible/Low risk (248.92 g/day) was slightly higher than High Risk (239.96 g/day), but this difference was negligible. Region-specific correlations (Urban, Suburban, Rural) also showed no significant relationship.
*Conclusion:* Hypothesis 2 is **refuted**. High vegetable intake alone does not act as a strong predictive indicator for lower MP loads in this dataset.

## 4. Modeling Results
The Optuna-optimized XGBoost model achieved the following performance on the test set:
- **High Risk Sensitivity (Recall)**: 0.38
- **Accuracy**: 0.37
Given the small dataset (n=229) and the noise inherent in self-reported dietary metrics, predicting precise tertile risk levels from this limited set of non-invasive features remains highly challenging.

## 5. Limitations & Future Work
- **Correlation vs Causality**: The findings highlight correlations (or lack thereof) but do not establish causality between specific dietary items and blood MP accumulation.
- **Data Size & Variability**: A dataset of 229 participants limits the statistical power needed to detect subtle non-linear interactions.
- **Measurement Constraints**: Self-reported dietary intakes are subject to recall bias, and metabolic variability was not accounted for.
- **Next Steps**: A larger, longitudinal study is needed, integrating clinical organ health correlations and potentially standardizing the "Plastic Load Index" (PLI) metrics more rigorously to enhance predictive power.
