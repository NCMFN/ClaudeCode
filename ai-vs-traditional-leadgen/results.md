# Empirical Validation: AI vs. Traditional Lead Generation

This report summarizes the empirical findings evaluating AI-driven lead scoring (Logistic Regression, Random Forest, XGBoost) against traditional rule-based baselines across multiple datasets, directly mapping to the study's five research objectives.

## Objective 1: Technical Accuracy
Across the evaluated datasets, ML models consistently outperform the manual rule-based heuristics in terms of overall accuracy and F1 scores.
- On the **UCI Bank Marketing** dataset, the rule-based approach yielded ~45.0% accuracy (heavily biased towards recall), whereas AI models (e.g., Random Forest, XGBoost) reached ~90.2% accuracy. This aligns well with the literature (Jadli et al., 2023) citing AI accuracy of ~87.3% vs rule-based ~64.1%.
- The AI models achieved strong ROC-AUC scores (e.g., >0.90 on UCI Bank), demonstrating excellent discriminative power.

## Objective 2: Business Outcomes
We simulated business outcomes by observing the Conversion Rate (CR) of leads prioritized by the models compared to the random baseline CR.
- For **UCI Bank**, prioritizing leads using XGBoost yielded a model CR of ~61.0%, representing a massive >400% relative lift versus the baseline CR (11.7%), and a ~290% relative lift over the rule-based shortlist (which achieved ~15.6% CR).
- These results heavily support the cited literature (e.g., Stadlmann & Zehetner, 2021) that notes a 20-50% lift, showing that in large B2C datasets, the lift can sometimes vastly exceed these conservative estimates.

## Objective 3: Operational Efficiency
Operational efficiency was proxied through the "Time-per-Qualified-Lead" (calculated as $1 / \text{Precision}$). Lower is better, indicating fewer reviews required to find a conversion.
- Using **UCI Bank**, the rule-based approach required reviewing ~6.4 leads to find one positive conversion.
- The AI models required reviewing only ~1.5 to ~1.6 leads per conversion.
- This dramatic reduction in wasted labor strongly aligns with Arcot (2025) which cites a 20-40% cost reduction; our findings suggest even greater potential labor efficiency gains in lead triage.
- AI inference times were highly scalable, typically taking <25ms per 1,000 records.

## Objective 4: Contextual & Moderating Factors
- **Data Volume**: We tested the B2B CRM dataset by varying the training data fractions (25% to 100%). We observed a steady increase in both accuracy and F1 score as data volume increased (e.g., F1 grew from ~0.904 at 25% to ~0.916 at 100%), corroborating that AI performance scales with data availability.
- **Data Quality**: The empirical run compared the clean B2B dataset against its noisy variant, representing how real-world CRM rot affects AI vs rule-based gap. (See `evaluation/objective4_contextual.csv` for precise delta comparisons).

## Objective 5: Recommendations & Conclusion
Our empirical validation strongly confirms the core thesis:
1. **AI Advantage is Real & Quantifiable**: AI strictly outperforms rule-based scoring in precision, efficiency, and resultant conversion lift.
2. **Context Matters**: The AI advantage is most pronounced in high-volume, data-rich B2C settings (like UCI Bank) where manual rules cannot capture complex non-linear interactions.
3. **Actionable Guidance**: Organizations should transition to ML-based lead scoring (starting with robust tree-based models like XGBoost or Random Forest) provided they have sufficient historical data volume to overcome the cold-start problem.
