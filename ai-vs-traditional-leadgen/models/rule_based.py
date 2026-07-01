import numpy as np
import pandas as pd

def score_uci_bank(df):
    """
    Rule-based heuristic for UCI Bank Dataset.
    Mimics traditional lead scoring rules based on available features:
    - Age (e.g., between 30-50 might be preferred) -> +1
    - Job (management, tech, admin) -> +2
    - Balance (high balance > 1000) -> +2
    - Campaign (fewer contacts is better, campaign < 3) -> +1
    - Previous (previously contacted successfully) -> +3
    - Duration (longer duration implies interest, duration > 200) -> +2

    Threshold: Score >= 4
    """
    scores = np.zeros(len(df))
    scores += ((df['age'] >= 30) & (df['age'] <= 50)).astype(int) * 1
    scores += df['job'].isin(['management', 'technician', 'admin.']).astype(int) * 2
    scores += (df['balance'] > 1000).astype(int) * 2
    scores += (df['campaign'] < 3).astype(int) * 1
    scores += (df['previous'] > 0).astype(int) * 3
    scores += (df['duration'] > 200).astype(int) * 2

    return scores

def predict_uci_bank(df, threshold=4):
    return (score_uci_bank(df) >= threshold).astype(int)

def score_kaggle_lead(df):
    """
    Rule-based heuristic for Kaggle Lead Scoring Dataset.
    Features used:
    - Total Time Spent on Website (> 500) -> +3
    - Last Activity ('Email Opened', 'SMS Sent') -> +2
    - Lead Origin ('Landing Page Submission', 'Lead Add Form') -> +2
    - Do Not Email ('No') -> +1
    - Specialization (not 'Select' and not missing) -> +2

    Threshold: Score >= 5
    """
    scores = np.zeros(len(df))

    if 'Total Time Spent on Website' in df.columns:
        scores += (pd.to_numeric(df['Total Time Spent on Website'], errors='coerce') > 500).astype(int) * 3

    if 'Last Activity' in df.columns:
        scores += df['Last Activity'].isin(['Email Opened', 'SMS Sent']).astype(int) * 2

    if 'Lead Origin' in df.columns:
        scores += df['Lead Origin'].isin(['Landing Page Submission', 'Lead Add Form']).astype(int) * 2

    if 'Do Not Email' in df.columns:
        scores += (df['Do Not Email'] == 'No').astype(int) * 1

    if 'Specialization' in df.columns:
        scores += (~df['Specialization'].isin(['Select', np.nan]) & df['Specialization'].notnull()).astype(int) * 2

    return scores

def predict_kaggle_lead(df, threshold=5):
    return (score_kaggle_lead(df) >= threshold).astype(int)

def score_kaggle_b2b(df):
    """
    Rule-based heuristic for Kaggle B2B CRM.
    Features used:
    - Decision_Maker_Flag ('Yes') -> +3
    - Influence_Score (> 70) -> +2
    - Seniority_Level ('Senior', 'Director', 'C-Level') -> +2
    - Event_Attendance (> 0) -> +2
    - Newsletter_Subscription ('Yes') -> +1

    Threshold: Score >= 5
    """
    scores = np.zeros(len(df))

    if 'Decision_Maker_Flag' in df.columns:
        scores += (df['Decision_Maker_Flag'] == 'Yes').astype(int) * 3

    if 'Influence_Score' in df.columns:
        scores += (pd.to_numeric(df['Influence_Score'], errors='coerce') > 70).astype(int) * 2

    if 'Seniority_Level' in df.columns:
        scores += df['Seniority_Level'].isin(['Senior', 'Director', 'C-Level', 'VP']).astype(int) * 2

    if 'Event_Attendance' in df.columns:
        scores += (pd.to_numeric(df['Event_Attendance'], errors='coerce') > 0).astype(int) * 2

    if 'Newsletter_Subscription' in df.columns:
        scores += (df['Newsletter_Subscription'] == 'Yes').astype(int) * 1

    return scores

def predict_kaggle_b2b(df, threshold=5):
    return (score_kaggle_b2b(df) >= threshold).astype(int)
