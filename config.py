# Column mapping configuration
COL_MAPPING = {
    'id': 'LoanID',
    'target': 'Default',
    'income': 'Income',
    'loan_amount': 'LoanAmount',
    'loan_term': 'LoanTerm',
    'months_employed': 'MonthsEmployed',
    'age': 'Age',
    'dti_ratio': 'DTIRatio',
    'interest_rate': 'InterestRate',
    'employment_type': 'EmploymentType',
    'loan_purpose': 'LoanPurpose',
    # New engineered features
    'payment_to_income': 'payment_to_income',
    'credit_to_income': 'credit_to_income',
    'employment_age_ratio': 'employment_age_ratio',
    'high_dti_flag': 'high_dti_flag',
    'interest_rate_tier': 'interest_rate_tier'
}
