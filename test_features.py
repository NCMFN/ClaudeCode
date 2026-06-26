import pandas as pd
import features

df = pd.DataFrame({
    'LoanAmount': [10000, 20000, 0],
    'LoanTerm': [12, 24, 12],
    'Income': [120000, 60000, 0],
    'MonthsEmployed': [24, 6, 0],
    'Age': [30, 25, 20],
    'DTIRatio': [20.0, 40.0, 10.0],
    'InterestRate': [5.0, 12.0, 25.0]
})

df_feat = features.engineer_features(df)
print(df_feat[['payment_to_income', 'credit_to_income', 'employment_age_ratio', 'high_dti_flag', 'interest_rate_tier']])
