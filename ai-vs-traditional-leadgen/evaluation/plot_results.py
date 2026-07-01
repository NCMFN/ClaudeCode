import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import os

os.makedirs('evaluation/plots', exist_ok=True)

# 1. Plot Accuracy & F1
df1 = pd.read_csv('evaluation/objective1_metrics.csv')
plt.figure(figsize=(10, 6))
sns.barplot(data=df1, x='Dataset', y='F1', hue='Model')
plt.title('Objective 1: F1 Score Comparison (Rule-Based vs ML)')
plt.ylabel('F1 Score')
plt.xticks(rotation=45)
plt.tight_layout()
plt.savefig('evaluation/plots/obj1_f1_score.png')
plt.close()

# 2. Plot Business Outcomes (Lift)
df2 = pd.read_csv('evaluation/objective2_business.csv')
plt.figure(figsize=(10, 6))
sns.barplot(data=df2, x='Dataset', y='Relative_Lift_vs_Baseline', hue='Model')
plt.title('Objective 2: Relative Lift vs Baseline Conversion Rate')
plt.ylabel('Relative Lift (Ratio)')
plt.xticks(rotation=45)
plt.tight_layout()
plt.savefig('evaluation/plots/obj2_conversion_lift.png')
plt.close()

# 3. Plot Operational Efficiency (Time per lead)
df3 = pd.read_csv('evaluation/objective3_efficiency.csv')
plt.figure(figsize=(10, 6))
sns.barplot(data=df3, x='Dataset', y='Time_per_Qualified_Lead_Proxy', hue='Model')
plt.title('Objective 3: Effort Proxy (Reviews per Qualified Lead)')
plt.ylabel('Reviews per Lead (Lower is Better)')
plt.xticks(rotation=45)
plt.tight_layout()
plt.savefig('evaluation/plots/obj3_effort_proxy.png')
plt.close()

# 4. Plot Contextual Factors (Data Volume)
df4 = pd.read_csv('evaluation/objective4_contextual.csv')
plt.figure(figsize=(8, 5))
sns.lineplot(data=df4, x='Training_Data_Fraction', y='F1', marker='o')
plt.title('Objective 4: Impact of Data Volume on F1 (XGBoost, B2B Clean)')
plt.ylabel('F1 Score')
plt.xlabel('Fraction of Training Data')
plt.tight_layout()
plt.savefig('evaluation/plots/obj4_data_volume.png')
plt.close()

print("Generated plots in evaluation/plots/")
