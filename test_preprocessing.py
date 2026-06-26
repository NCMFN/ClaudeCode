import pandas as pd
import preprocessing

# increase dataset size to avoid stratification error
df = pd.DataFrame({
    'LoanID': [f'L{i}' for i in range(20)],
    'LoanAmount': [10000, 20000, 5000, 15000, 100000]*4,
    'LoanTerm': [12, 24, 12, 36, 60]*4,
    'Income': [120000, 60000, 30000, 80000, 500000]*4,
    'MonthsEmployed': [24, 6, 12, 36, 120]*4,
    'Age': [30, 25, 20, 40, 55]*4,
    'DTIRatio': [20.0, 40.0, 10.0, 25.0, 50.0]*4,
    'InterestRate': [5.0, 12.0, 25.0, 10.0, 8.0]*4,
    'EmploymentType': ['Full', 'Part', 'Full', 'Self', 'Full']*4,
    'LoanPurpose': ['Auto', 'Home', 'Auto', 'Debt', 'Auto']*4,
    'Default': [0, 1, 0, 0, 1]*4
})

# Add some missing values
df.loc[0, 'Income'] = float('nan')
df.loc[1, 'EmploymentType'] = float('nan')

X_train, X_test, y_train, y_test = preprocessing.preprocess_data(df, exclude_anomalies=False)
print("X_train shape:", X_train.shape)
print("X_test shape:", X_test.shape)
print(X_train.head(2))
