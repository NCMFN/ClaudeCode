import pandas as pd
import json
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import confusion_matrix, roc_curve, auc
from urllib.parse import urlparse
import warnings
import os

warnings.filterwarnings('ignore')
plt.style.use('ggplot')
sns.set_palette("Set2")

os.makedirs('mlasf_research/visualizations', exist_ok=True)

print("Loading dataset...")
with open('mlasf_research/Cisco_Ariel_Uni_API_security_challenge/Datasets/dataset_4_train.json') as f:
    data = json.load(f)
df = pd.json_normalize(data)

df['label'] = df['request.Attack_Tag'].notna().map({True: 'Malicious', False: 'Benign'})

print("Generating Traffic Distribution plot...")
plt.figure(figsize=(8, 6))
sns.countplot(x='label', data=df)
plt.title('API Traffic Distribution (Benign vs Malicious)')
plt.ylabel('Count')
plt.savefig('mlasf_research/visualizations/traffic_distribution.png', bbox_inches='tight')
plt.close()

print("Generating Attack Category Distribution plot...")
plt.figure(figsize=(10, 6))
attack_data = df[df['label'] == 'Malicious']
sns.countplot(y='request.Attack_Tag', data=attack_data, palette='viridis', order=attack_data['request.Attack_Tag'].value_counts().index)
plt.title('Attack Category Distribution')
plt.xlabel('Count')
plt.ylabel('Attack Type')
plt.savefig('mlasf_research/visualizations/attack_categories.png', bbox_inches='tight')
plt.close()

print("Generating Time Series Request Patterns plot...")
df['timestamp'] = pd.to_datetime(df['request.headers.Date'], format='%a, %d %b %Y %H:%M:%S %Z', errors='coerce')
time_series = df.set_index('timestamp').groupby([pd.Grouper(freq='1Min'), 'label']).size().unstack(fill_value=0)
plt.figure(figsize=(14, 6))
time_series.plot(kind='line', ax=plt.gca(), colormap='Set1')
plt.title('API Request Patterns Over Time (per minute)')
plt.ylabel('Number of Requests')
plt.xlabel('Time')
plt.savefig('mlasf_research/visualizations/time_series.png', bbox_inches='tight')
plt.close()

print("Extracting features and training model...")
def extract_features(df):
    features = pd.DataFrame()
    features['url_length'] = df['request.url'].apply(lambda x: len(str(x)))
    features['url_path_length'] = df['request.url'].apply(lambda x: len(urlparse(str(x)).path))
    features['url_num_params'] = df['request.url'].apply(lambda x: str(x).count('&') + 1 if '?' in str(x) else 0)
    features['url_has_sql_keywords'] = df['request.url'].apply(lambda x: 1 if any(kw in str(x).lower() for kw in ['select', 'union', 'drop', 'insert', '--']) else 0)
    features['url_has_xss_keywords'] = df['request.url'].apply(lambda x: 1 if any(kw in str(x).lower() for kw in ['<script', 'javascript:', 'alert(']) else 0)
    features['url_has_lfi_keywords'] = df['request.url'].apply(lambda x: 1 if any(kw in str(x).lower() for kw in ['../', '..\\', 'etc/passwd']) else 0)
    features['user_agent_length'] = df['request.headers.User-Agent'].apply(lambda x: len(str(x)) if pd.notna(x) else 0)
    features['cookie_length'] = df['request.headers.Cookie'].apply(lambda x: len(str(x)) if pd.notna(x) else 0)
    features['body_length'] = df['request.body'].apply(lambda x: len(str(x)) if pd.notna(x) else 0)

    method_map = {'GET': 0, 'POST': 1, 'PUT': 2, 'DELETE': 3, 'OPTIONS': 4}
    features['method'] = df['request.method'].map(method_map).fillna(0)
    return features

X = extract_features(df)
y = (df['label'] == 'Malicious').astype(int)

X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
rf = RandomForestClassifier(n_estimators=100, random_state=42, n_jobs=-1)
rf.fit(X_train, y_train)

y_pred = rf.predict(X_test)
y_prob = rf.predict_proba(X_test)[:, 1]

print("Generating Confusion Matrix plot...")
cm = confusion_matrix(y_test, y_pred)
plt.figure(figsize=(6, 5))
sns.heatmap(cm, annot=True, fmt='d', cmap='Blues', xticklabels=['Benign', 'Malicious'], yticklabels=['Benign', 'Malicious'])
plt.title('Confusion Matrix')
plt.xlabel('Predicted Label')
plt.ylabel('True Label')
plt.savefig('mlasf_research/visualizations/confusion_matrix.png', bbox_inches='tight')
plt.close()

print("Generating ROC Curve plot...")
fpr_curve, tpr_curve, _ = roc_curve(y_test, y_prob)
roc_auc = auc(fpr_curve, tpr_curve)
plt.figure(figsize=(6, 5))
plt.plot(fpr_curve, tpr_curve, color='darkorange', lw=2, label=f'ROC curve (area = {roc_auc:.2f})')
plt.plot([0, 1], [0, 1], color='navy', lw=2, linestyle='--')
plt.xlim([0.0, 1.0])
plt.ylim([0.0, 1.05])
plt.xlabel('False Positive Rate')
plt.ylabel('True Positive Rate')
plt.title('Receiver Operating Characteristic (ROC)')
plt.legend(loc="lower right")
plt.savefig('mlasf_research/visualizations/roc_curve.png', bbox_inches='tight')
plt.close()

print("Generating Feature Importance plot...")
importance = pd.DataFrame({'feature': X.columns, 'importance': rf.feature_importances_}).sort_values('importance', ascending=False)
plt.figure(figsize=(8, 5))
sns.barplot(x='importance', y='feature', data=importance, palette='rocket')
plt.title('Feature Importance in Threat Detection')
plt.xlabel('Importance Score')
plt.ylabel('Features')
plt.savefig('mlasf_research/visualizations/feature_importance.png', bbox_inches='tight')
plt.close()

print("All visualizations saved to mlasf_research/visualizations/")
