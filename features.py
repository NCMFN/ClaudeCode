import pandas as pd
import numpy as np
import logging
from config import COL_MAPPING as CM

logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')

def engineer_features(df_in):
    """
    Engineers new features based on domain knowledge.
    Creates: payment_to_income, credit_to_income, employment_age_ratio,
             high_dti_flag, interest_rate_tier.

    Args:
        df_in (pd.DataFrame): Input dataframe.

    Returns:
        pd.DataFrame: DataFrame with engineered features.
    """
    # Create a copy to maintain immutability principle
    df = df_in.copy()

    # payment_to_income = monthly_loan_payment / monthly_income
    if CM['loan_amount'] in df.columns and CM['loan_term'] in df.columns and CM['income'] in df.columns:
        monthly_income = df[CM['income']] / 12
        monthly_payment = df[CM['loan_amount']] / df[CM['loan_term']].replace(0, 1)
        df[CM['payment_to_income']] = monthly_payment / monthly_income.replace(0, 1)
    else:
        logging.warning("Missing columns for payment_to_income feature. Skipping.")

    # credit_to_income = total_debt / annual_income
    if CM['loan_amount'] in df.columns and CM['income'] in df.columns:
        df[CM['credit_to_income']] = df[CM['loan_amount']] / df[CM['income']].replace(0, 1)
    else:
        logging.warning("Missing columns for credit_to_income feature. Skipping.")

    # employment_age_ratio = employment_months / applicant_age_months
    if CM['months_employed'] in df.columns and CM['age'] in df.columns:
        applicant_age_months = df[CM['age']] * 12
        df[CM['employment_age_ratio']] = df[CM['months_employed']] / applicant_age_months.replace(0, 1)
    else:
        logging.warning("Missing columns for employment_age_ratio feature. Skipping.")

    # high_dti_flag = 1 if DTI > 35 else 0
    if CM['dti_ratio'] in df.columns:
        df[CM['high_dti_flag']] = (df[CM['dti_ratio']] > 35).astype(int)
    else:
        logging.warning("Missing column DTIRatio for high_dti_flag. Skipping.")

    # interest_rate_tier = pd.cut(interest_rate, bins=[0,10,15,20,100], labels=['Low','Medium','High','VeryHigh'])
    if CM['interest_rate'] in df.columns:
        df[CM['interest_rate_tier']] = pd.cut(
            df[CM['interest_rate']],
            bins=[0, 10, 15, 20, 100],
            labels=['Low', 'Medium', 'High', 'VeryHigh']
        )
    else:
        logging.warning("Missing column InterestRate for interest_rate_tier. Skipping.")

    return df
