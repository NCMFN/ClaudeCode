# Setup imports
import os
import shutil
os.makedirs('output_figures', exist_ok=True)
import subprocess
try:
    import langdetect
except ImportError:
    print("Installing langdetect...")
    subprocess.check_call(["pip", "install", "langdetect"])

import pandas as pd
import random
import matplotlib.pyplot as plt
import seaborn as sns
import os, glob, re, string, nltk
from langdetect import detect, DetectorFactory
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer
import itertools
import networkx as nx

# --- Original Cell 0 ---
# from google.colab import files

print('Downloading CSV files:')
# files.download('ngo_data.csv')
# files.download('community_survey.csv')

# --- Original Cell 1 ---
# from google.colab import files

print('Downloading text files:')
# files.download('traditional_knowledge1.txt')
# files.download('traditional_knowledge2.txt')

# --- Original Cell 2 ---
import subprocess
try:
    import langdetect
except ImportError:
    print("Installing langdetect...")
    subprocess.check_call(["pip", "install", "langdetect"])

import pandas as pd
import os

# Create dummy CSV files
csv_data1 = {
    'ID': [1, 2, 3, 4, 5],
    'Name': ['Alice', 'Bob', 'Charlie', 'David', 'Eve'],
    'Age': [24, 27, 22, 32, 29],
    'City': ['New York', 'Los Angeles', 'Chicago', 'Houston', 'Phoenix'],
    'Score': [85, 92, 78, 88, 95]
}
df1 = pd.DataFrame(csv_data1)
df1.to_csv('ngo_data.csv', index=False)

csv_data2 = {
    'SurveyID': [101, 102, 103, 104, 105],
    'Question1': ['Good', 'Neutral', 'Bad', 'Good', 'Good'],
    'Question2': [5, 3, 1, 4, 5],
    'RespondentAge': [45, 32, 60, 28, 51],
    'Income': [50000, 30000, None, 75000, 40000]
}
df2 = pd.DataFrame(csv_data2)
df2.to_csv('community_survey.csv', index=False)

# Create dummy text files
with open('traditional_knowledge1.txt', 'w') as f:
    f.write('This document contains traditional knowledge related to sustainable farming practices.')
with open('traditional_knowledge2.txt', 'w') as f:
    f.write('This document details local remedies using indigenous plants.')

print("Dummy data files created successfully.")

# --- Original Cell 3 ---
import glob

# --- Load and review CSV files ---
csv_files = glob.glob('*.csv')
loaded_dataframes = {}

print('--- Reviewing CSV Files ---\n')
for csv_file in csv_files:
    print(f'Loading and reviewing: {csv_file}')
    df_name = os.path.splitext(csv_file)[0] # Use filename as df name
    df = pd.read_csv(csv_file)
    loaded_dataframes[df_name] = df

    print(f'\n{csv_file} - First 5 rows:')
    print(df.head())

    print(f'\n{csv_file} - Column names:')
    print(df.columns.tolist())

    print(f'\n{csv_file} - Data types and non-null values:')
    df.info()

    print(f'\n{csv_file} - Missing values:')
    print(df.isnull().sum())
    print('\n' + '-'*50 + '\n')

# --- Load and review text files ---
text_files = glob.glob('*.txt')
text_documents = []

print('--- Reviewing Text Files ---\n')
for txt_file in text_files:
    with open(txt_file, 'r') as f:
        content = f.read()
        text_documents.append(content)
    print(f'Loaded text file: {txt_file}')

print(f'\nTotal number of text documents loaded: {len(text_documents)}')

if text_documents:
    print(f'\nFirst 200 characters of the first document:')
    print(text_documents[0][:200])
else:
    print('No text documents were found or loaded.')


# --- Original Cell 4 ---
import re
import string

# 1. Combine all textual data
all_texts = []

# Add text documents
all_texts.extend(text_documents)

# Add relevant string columns from DataFrames
# From 'ngo_data'
if 'ngo_data' in loaded_dataframes:
    df_ngo = loaded_dataframes['ngo_data']
    all_texts.extend(df_ngo['Name'].astype(str).tolist())
    all_texts.extend(df_ngo['City'].astype(str).tolist())

# From 'community_survey'
if 'community_survey' in loaded_dataframes:
    df_community = loaded_dataframes['community_survey']
    all_texts.extend(df_community['Question1'].astype(str).tolist())

print(f"Total number of combined text entries: {len(all_texts)}")
print("First 5 raw text entries:")
for i, text in enumerate(all_texts[:5]):
    print(f"  {i+1}. {text[:100]}...")

# 2. Define a text cleaning function
def clean_text(text):
    text = str(text).lower()  # Convert to lowercase and ensure string type
    text = text.translate(str.maketrans('', '', string.punctuation))  # Remove punctuation
    text = re.sub(r'[^a-z\s]', '', text)  # Remove special characters and numbers (keeping only letters and spaces)
    text = re.sub(r'\s+', ' ', text).strip()  # Remove extra whitespace
    return text

# 3. Apply the cleaning function
cleaned_texts = [clean_text(text) for text in all_texts]

# 4. Print the first 200 characters of the first few cleaned texts
print('\n--- Verification of Cleaned Texts ---\n')
print(f'Total number of cleaned text entries: {len(cleaned_texts)}')

if cleaned_texts:
    print('\nFirst 3 cleaned text entries (first 200 characters each):')
    for i, cleaned_text in enumerate(cleaned_texts[:3]):
        print(f'Entry {i+1}: {cleaned_text[:200]}')
else:
    print('No cleaned texts to display.')


# --- Original Cell 5 ---
import sys

# Install langdetect
# !{sys.executable} -m pip install langdetect

# Install NLTK
# !{sys.executable} -m pip install nltk

import nltk

# Download necessary NLTK data
nltk.download('punkt')
nltk.download('stopwords')
nltk.download('wordnet')
nltk.download('punkt_tab')
# Install NLTK (if not already satisfied)
# !{sys.executable} -m pip install nltk

# Download necessary NLTK data. nltk.download() checks if already present.
nltk.download('punkt', quiet=True)
nltk.download('stopwords', quiet=True)
nltk.download('wordnet', quiet=True)

print("Required libraries and NLTK data installed/downloaded.")

# --- Original Cell 7 ---
from langdetect import detect, DetectorFactory

# Ensure reproducibility for langdetect
DetectorFactory.seed = 0

# 1. Identify the language of each text string
text_languages = []
for text in cleaned_texts:
    try:
        lang = detect(text)
        text_languages.append(lang)
    except Exception as e:
        text_languages.append('unknown') # Handle cases where language detection fails

print(f"Detected languages for the first 10 texts: {text_languages[:10]}")
print(f"Language distribution: {pd.Series(text_languages).value_counts()}")

# 2. Simulate translation for non-English texts
translated_texts = []
for i, text in enumerate(cleaned_texts):
    if text_languages[i] != 'en':
        # Simulate translation. In a real scenario, use a translation API.
        translated_texts.append(f"[Translated to English] {text}")
    else:
        translated_texts.append(text)

print('\n--- Simulated Translation Verification ---\n')
print(f'Total number of texts after simulated translation: {len(translated_texts)}')
print('\nFirst 5 original texts and their translated versions (if applicable):')
for i in range(min(5, len(cleaned_texts))):
    print(f'Original [{text_languages[i]}]: {cleaned_texts[i][:100]}')
    print(f'Translated: {translated_texts[i][:100]}\n')

# Store the English/translated texts for the next steps
english_texts = translated_texts

# --- Original Cell 8 ---
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer
import nltk

# Ensure punkt_tab is downloaded for word_tokenize
nltk.download('punkt_tab', quiet=True)

# Initialize NLTK components
stop_words = set(stopwords.words('english'))
lemmatizer = WordNetLemmatizer()

processed_texts = []

print('--- Performing Tokenization, Stopword Removal, and Lemmatization ---\n')
for i, text in enumerate(english_texts):
    # 1. Tokenization
    tokens = word_tokenize(text)

    # 2. Stopword Removal and Lowercasing (already lowercased, but good practice)
    filtered_tokens = [word for word in tokens if word not in stop_words and word.isalpha()] # .isalpha() to remove non-alphabetic tokens

    # 3. Lemmatization
    lemmas = [lemmatizer.lemmatize(word) for word in filtered_tokens]
    processed_texts.append(lemmas)

print(f'Total number of processed text documents: {len(processed_texts)}')
print('\nFirst 5 processed text entries (lemmatized tokens):')
for i, tokens in enumerate(processed_texts[:5]):
    print(f'Entry {i+1}: {tokens}')

# --- Original Cell 9 ---
final_prepared_texts = []

for doc_tokens in processed_texts:
    # Join the lemmatized tokens back into a single string
    rejoined_text = ' '.join(doc_tokens)
    final_prepared_texts.append(rejoined_text)

print(f'Total number of prepared documents: {len(final_prepared_texts)}')

print('\nFirst 3 prepared documents:')
for i, doc in enumerate(final_prepared_texts[:3]):
    print(f'Document {i+1}: {doc}')

# --- Original Cell 10 ---
import random

# 1. Define a list of dummy Sustainable Development Goals (SDGs)
dummy_sdgs = [
    'SDG 1: No Poverty',
    'SDG 2: Zero Hunger',
    'SDG 3: Good Health and Well-being',
    'SDG 4: Quality Education',
    'SDG 5: Gender Equality',
    'SDG 6: Clean Water and Sanitation',
    'SDG 7: Affordable and Clean Energy',
    'SDG 8: Decent Work and Economic Growth',
    'SDG 9: Industry, Innovation, and Infrastructure',
    'SDG 10: Reduced Inequalities',
    'SDG 11: Sustainable Cities and Communities',
    'SDG 12: Responsible Consumption and Production',
    'SDG 13: Climate Action',
    'SDG 14: Life Below Water',
    'SDG 15: Life On Land',
    'SDG 16: Peace, Justice, and Strong Institutions',
    'SDG 17: Partnerships for the Goals'
]

# 2. Initialize an empty list to store simulated SDG labels
simulated_sdg_labels = []

# 3. Iterate through each document in final_prepared_texts
for doc_text in final_prepared_texts:
    # 4. For each document, randomly select a subset of 1 to 3 SDGs
    num_sdgs_to_assign = random.randint(1, 3) # Randomly choose between 1 and 3 SDGs
    selected_sdgs = random.sample(dummy_sdgs, num_sdgs_to_assign)

    # 5. Append the list of selected SDG labels for the current document
    simulated_sdg_labels.append(selected_sdgs)

# 6. Print the total number of documents for which SDG labels were generated
print(f"Total number of documents with simulated SDG labels: {len(simulated_sdg_labels)}")

# 7. Print the first 5 entries of simulated_sdg_labels
print('\nFirst 5 simulated SDG label assignments:')
for i, labels in enumerate(simulated_sdg_labels[:5]):
    print(f'Document {i+1}: {labels}')

# --- Original Cell 11 ---
import random
import subprocess
try:
    import langdetect
except ImportError:
    print("Installing langdetect...")
    subprocess.check_call(["pip", "install", "langdetect"])

import pandas as pd
from collections import defaultdict

# 1. Create a list of dummy geographical regions
dummy_regions = ['East Africa', 'West Africa', 'Southern Africa', 'Central Africa', 'North Africa']
simulated_regions = [random.choice(dummy_regions) for _ in range(len(final_prepared_texts))]

# 2. Create a list of dummy issues
dummy_issues = ['Agriculture', 'Education', 'Health', 'Infrastructure', 'Governance', 'Environment']
simulated_issues = [random.choice(dummy_issues) for _ in range(len(final_prepared_texts))]

# 3. Create a Pandas DataFrame
data_for_df = {
    'text': final_prepared_texts,
    'sdg_labels': simulated_sdg_labels,
    'region': simulated_regions,
    'issue': simulated_issues
}
df_analysis = pd.DataFrame(data_for_df)

print("DataFrame created with text, SDG labels, regions, and issues.")
print("First 5 rows of the analysis DataFrame:")
print(df_analysis.head())

# Helper function to flatten list of lists for SDG counting
def flatten_sdg_labels(list_of_lists):
    flat_list = []
    for sublist in list_of_lists:
        for item in sublist:
            flat_list.append(item)
    return flat_list

# 4. Calculate the overall frequency of each SDG
all_sdgs_flat = flatten_sdg_labels(df_analysis['sdg_labels'])
overall_sdg_frequency = pd.Series(all_sdgs_flat).value_counts()

print('\n--- Overall SDG Frequency ---\n')
print("Top 5 most frequent SDGs:")
print(overall_sdg_frequency.head(5))

# 5. Group by 'region' and calculate SDG frequency within each region
print('\n--- SDG Frequency by Region ---\n')
for region in df_analysis['region'].unique():
    region_df = df_analysis[df_analysis['region'] == region]
    region_sdgs_flat = flatten_sdg_labels(region_df['sdg_labels'])
    if region_sdgs_flat:
        region_sdg_frequency = pd.Series(region_sdgs_flat).value_counts()
        print(f'\nTop 3 SDGs for {region}:')
        print(region_sdg_frequency.head(3))
    else:
        print(f'\nNo SDGs found for {region}.')

# 6. Group by 'issue' and calculate SDG frequency within each issue
print('\n--- SDG Frequency by Issue ---\n')
for issue in df_analysis['issue'].unique():
    issue_df = df_analysis[df_analysis['issue'] == issue]
    issue_sdgs_flat = flatten_sdg_labels(issue_df['sdg_labels'])
    if issue_sdgs_flat:
        issue_sdg_frequency = pd.Series(issue_sdgs_flat).value_counts()
        print(f'\nTop 3 SDGs for {issue}:')
        print(issue_sdg_frequency.head(3))
    else:
        print(f'\nNo SDGs found for {issue}.')


# --- Original Cell 12 ---
import itertools

# 1. Define a list of known conflicting SDG pairs or individual SDGs in tension
# These are illustrative examples; real-world conflicts are complex and numerous.
conflicting_sdg_pairs = [
    ('SDG 8: Decent Work and Economic Growth', 'SDG 13: Climate Action'), # Economic growth vs. environmental protection
    ('SDG 9: Industry, Innovation, and Infrastructure', 'SDG 15: Life On Land'), # Industrial expansion vs. ecosystem preservation
    ('SDG 2: Zero Hunger', 'SDG 12: Responsible Consumption and Production'), # Increased food production often unsustainable
    ('SDG 1: No Poverty', 'SDG 10: Reduced Inequalities') # Poverty reduction might not always reduce inequality proportionally
]

detected_conflicts = []

# 2. Iterate through each document's sdg_labels in the df_analysis DataFrame
for index, row in df_analysis.iterrows():
    doc_sdgs = set(row['sdg_labels'])
    document_conflicts = []

    # 3. Check if any of the predefined conflicting SDG pairs co-occur
    for conflict_pair in conflicting_sdg_pairs:
        sdg1, sdg2 = conflict_pair
        if sdg1 in doc_sdgs and sdg2 in doc_sdgs:
            document_conflicts.append(conflict_pair)

    # 4. Store the identified conflicts
    if document_conflicts:
        detected_conflicts.append({
            'document_index': index,
            'document_text_sample': row['text'][:100] + '...', # Store a sample of the text
            'assigned_sdgs': list(doc_sdgs),
            'conflicting_pairs': document_conflicts
        })

# 5. Print a summary of the detected conflicts
print(f"Total number of documents analyzed: {len(df_analysis)}")
print(f"Total number of documents with detected conflicts: {len(detected_conflicts)}")

if detected_conflicts:
    print('\n--- Examples of Detected Conflicts ---')
    for i, conflict_info in enumerate(detected_conflicts[:5]): # Print up to 5 examples
        print(f"\nDocument Index: {conflict_info['document_index']}")
        print(f"  Text Sample: {conflict_info['document_text_sample']}")
        print(f"  Assigned SDGs: {conflict_info['assigned_sdgs']}")
        print(f"  Conflicting Pairs: {conflict_info['conflicting_pairs']}")
else:
    print('\nNo policy conflicts were detected based on the defined pairs.')


# --- Original Cell 13 ---
import re

# 1. Define three sets of SDG categories
# These categorizations are typical but can be adapted based on specific analytical needs.
ECONOMIC_SDGS = {'SDG 1', 'SDG 8', 'SDG 9', 'SDG 10', 'SDG 12', 'SDG 17'}
SOCIAL_SDGS = {'SDG 1', 'SDG 2', 'SDG 3', 'SDG 4', 'SDG 5', 'SDG 6', 'SDG 7', 'SDG 11', 'SDG 16', 'SDG 17'}
ENVIRONMENTAL_SDGS = {'SDG 2', 'SDG 6', 'SDG 7', 'SDG 12', 'SDG 13', 'SDG 14', 'SDG 15', 'SDG 17'}

# Note: Some SDGs (e.g., SDG 1, 2, 6, 7, 12, 16, 17) can overlap across categories due to their interconnected nature.
# For example, SDG 1 (No Poverty) has economic and social aspects.
# SDG 17 (Partnerships for the Goals) supports all dimensions.

print("SDG categories defined: ECONOMIC_SDGS, SOCIAL_SDGS, ENVIRONMENTAL_SDGS")

# --- Original Cell 14 ---
def count_sdg_dimensions(sdg_labels):
    economic_count = 0
    social_count = 0
    environmental_count = 0

    for label in sdg_labels:
        # Extract SDG number (e.g., 'SDG 1') from 'SDG 1: No Poverty'
        sdg_number = label.split(':')[0].strip()

        if sdg_number in ECONOMIC_SDGS:
            economic_count += 1
        if sdg_number in SOCIAL_SDGS:
            social_count += 1
        if sdg_number in ENVIRONMENTAL_SDGS:
            environmental_count += 1

    return economic_count, social_count, environmental_count

# Apply the function to df_analysis
df_analysis[['economic_sdgs', 'social_sdgs', 'environmental_sdgs']] = df_analysis['sdg_labels'].apply(lambda x: pd.Series(count_sdg_dimensions(x)))

print("Calculated Economic, Social, and Environmental SDG counts for each document.")
print("First 5 rows with new SDG dimension counts:")
print(df_analysis[['sdg_labels', 'economic_sdgs', 'social_sdgs', 'environmental_sdgs']].head())

# Calculate average counts per dimension
average_economic_sdgs = df_analysis['economic_sdgs'].mean()
average_social_sdgs = df_analysis['social_sdgs'].mean()
average_environmental_sdgs = df_analysis['environmental_sdgs'].mean()

print(f"\nAverage Economic SDGs per document: {average_economic_sdgs:.2f}")
print(f"Average Social SDGs per document: {average_social_sdgs:.2f}")
print(f"Average Environmental SDGs per document: {average_environmental_sdgs:.2f}")

# --- Original Cell 15 ---
import subprocess
try:
    import langdetect
except ImportError:
    print("Installing langdetect...")
    subprocess.check_call(["pip", "install", "langdetect"])

import pandas as pd

# 5. Calculate the overall frequency of each individual SDG (already done in a previous step)
#    The `overall_sdg_frequency` Series was created previously.
print('--- Overall SDG Frequency (Top 5) ---\n')
print(overall_sdg_frequency.head(5))

# 6. Set a threshold for 'underrepresentation'
#    For demonstration, we will consider an SDG underrepresented if it appears less than 2 times.
underrepresentation_threshold = 2

# 7. Identify and print SDGs that fall below this frequency threshold
underrepresented_sdgs = overall_sdg_frequency[overall_sdg_frequency < underrepresentation_threshold]

print(f'\n--- Underrepresented SDGs (frequency < {underrepresentation_threshold}) ---\n')
if not underrepresented_sdgs.empty:
    print(underrepresented_sdgs)
else:
    print('No SDGs found below the underrepresentation threshold.')

# --- Original Cell 16 ---
print('\n--- Underrepresented Regions and Issues (by document count) ---\n')

# Group by 'region' and count documents
region_document_counts = df_analysis['region'].value_counts()
underrepresented_regions = region_document_counts[region_document_counts < underrepresentation_threshold]

if not underrepresented_regions.empty:
    print(f'Regions with fewer than {underrepresentation_threshold} documents:')
    print(underrepresented_regions)
else:
    print('No regions found below the document count threshold.')

print('\n' + '-'*50 + '\n')

# Group by 'issue' and count documents
issue_document_counts = df_analysis['issue'].value_counts()
underrepresented_issues = issue_document_counts[issue_document_counts < underrepresentation_threshold]

if not underrepresented_issues.empty:
    print(f'Issues with fewer than {underrepresentation_threshold} documents:')
    print(underrepresented_issues)
else:
    print('No issues found below the document count threshold.')

# --- Original Cell 17 ---
print('\n--- Context-Specific Underrepresented SDGs (by Region and Issue) ---\n')

all_dummy_sdgs = [sdg.split(':')[0].strip() for sdg in dummy_sdgs] # Extract 'SDG 1' from 'SDG 1: No Poverty'

# Identify underrepresented SDGs per region
for region in df_analysis['region'].unique():
    region_df = df_analysis[df_analysis['region'] == region]
    region_sdgs_flat = flatten_sdg_labels(region_df['sdg_labels'])

    if not region_sdgs_flat:
        print(f'\nRegion: {region} - No SDGs found.')
        continue

    region_sdg_frequency = pd.Series(region_sdgs_flat).value_counts().apply(lambda x: x if isinstance(x, (int, float)) else 0)

    # Convert full SDG names to SDG numbers for comparison with all_dummy_sdgs
    region_sdg_numbers_present = {sdg.split(':')[0].strip() for sdg in region_sdg_frequency.index}

    missing_sdgs_region = [sdg for sdg in all_dummy_sdgs if sdg not in region_sdg_numbers_present]

    underrepresented_in_region = region_sdg_frequency[region_sdg_frequency < underrepresentation_threshold]
    underrepresented_in_region_names = [sdg for sdg in underrepresented_in_region.index if sdg.split(':')[0].strip() not in missing_sdgs_region]

    if missing_sdgs_region or underrepresented_in_region_names:
        print(f'\nRegion: {region}')
        if missing_sdgs_region:
            print(f'  Completely Missing SDGs: {missing_sdgs_region}')
        if underrepresented_in_region_names:
            print(f'  Underrepresented SDGs (count < {underrepresentation_threshold}): {underrepresented_in_region_names}')
    else:
        print(f'\nRegion: {region} - No specific underrepresentation detected beyond overall.')

print('\n' + '-'*50 + '\n')

# Identify underrepresented SDGs per issue
for issue in df_analysis['issue'].unique():
    issue_df = df_analysis[df_analysis['issue'] == issue]
    issue_sdgs_flat = flatten_sdg_labels(issue_df['sdg_labels'])

    if not issue_sdgs_flat:
        print(f'\nIssue: {issue} - No SDGs found.')
        continue

    issue_sdg_frequency = pd.Series(issue_sdgs_flat).value_counts().apply(lambda x: x if isinstance(x, (int, float)) else 0)

    # Convert full SDG names to SDG numbers for comparison with all_dummy_sdgs
    issue_sdg_numbers_present = {sdg.split(':')[0].strip() for sdg in issue_sdg_frequency.index}

    missing_sdgs_issue = [sdg for sdg in all_dummy_sdgs if sdg not in issue_sdg_numbers_present]

    underrepresented_in_issue = issue_sdg_frequency[issue_sdg_frequency < underrepresentation_threshold]
    underrepresented_in_issue_names = [sdg for sdg in underrepresented_in_issue.index if sdg.split(':')[0].strip() not in missing_sdgs_issue]

    if missing_sdgs_issue or underrepresented_in_issue_names:
        print(f'\nIssue: {issue}')
        if missing_sdgs_issue:
            print(f'  Completely Missing SDGs: {missing_sdgs_issue}')
        if underrepresented_in_issue_names:
            print(f'  Underrepresented SDGs (count < {underrepresentation_threshold}): {underrepresented_in_issue_names}')
    else:
        print(f'\nIssue: {issue} - No specific underrepresentation detected beyond overall.')

# --- Original Cell 18 ---
import random

# 1. Define a baseline scenario for SDG attainment
# For simplicity, let's use the SDG numbers as keys and assign random initial scores.
# We'll use all 17 SDGs.
baseline_sdg_scores = {
    f'SDG {i}': random.randint(30, 70) for i in range(1, 18)
}

print("Baseline SDG Scores (initial attainment levels):")
for sdg, score in baseline_sdg_scores.items():
    print(f"  {sdg}: {score}")

# 2. Define several hypothetical 'policy interventions' or 'investments'
# Each intervention will have a name and a dictionary of SDG impacts.
policy_interventions = [
    {
        'name': 'Investment in Education Programs',
        'impact': {'SDG 4': 15, 'SDG 1': 5, 'SDG 5': 7} # Quality Education, No Poverty, Gender Equality
    },
    {
        'name': 'Sustainable Agriculture Initiative',
        'impact': {'SDG 2': 20, 'SDG 13': 10, 'SDG 15': 8} # Zero Hunger, Climate Action, Life On Land
    },
    {
        'name': 'Healthcare Infrastructure Project',
        'impact': {'SDG 3': 18, 'SDG 6': 5, 'SDG 1': 3} # Good Health, Clean Water, No Poverty
    },
    {
        'name': 'Renewable Energy Transition',
        'impact': {'SDG 7': 25, 'SDG 13': 12, 'SDG 9': 5} # Clean Energy, Climate Action, Industry & Innovation
    },
    {
        'name': 'Water Conservation Policy',
        'impact': {'SDG 6': 20, 'SDG 12': 8, 'SDG 14': 5} # Clean Water, Responsible Consumption, Life Below Water
    }
]

print('\nDefined Policy Interventions:')
for intervention in policy_interventions:
    print(f"  - {intervention['name']}: {intervention['impact']}")

# --- Original Cell 19 ---
def simulate_what_if_scenario(baseline_scores, selected_interventions):
    # Create a copy of the baseline scores to simulate changes
    simulated_scores = baseline_scores.copy()

    print(f"\n--- Simulating What-If Scenario with {len(selected_interventions)} Interventions ---")
    for intervention in selected_interventions:
        print(f"Applying intervention: {intervention['name']}")
        for sdg, impact_value in intervention['impact'].items():
            current_score = simulated_scores.get(sdg, 0) # Get current score, default to 0 if SDG not in baseline
            new_score = current_score + impact_value
            # Ensure score does not exceed 100
            simulated_scores[sdg] = min(new_score, 100)

    return simulated_scores

print("Defined 'simulate_what_if_scenario' function.")

# --- Original Cell 20 ---
import subprocess
try:
    import langdetect
except ImportError:
    print("Installing langdetect...")
    subprocess.check_call(["pip", "install", "langdetect"])

import pandas as pd

# 4. Demonstrate the prototype by running a 'what-if' scenario

# Choose a few interventions for the scenario
selected_interventions_scenario1 = [
    policy_interventions[0], # Investment in Education Programs
    policy_interventions[2]  # Healthcare Infrastructure Project
]

# Run the simulation
simulated_sdg_scores_scenario1 = simulate_what_if_scenario(baseline_sdg_scores, selected_interventions_scenario1)

# Prepare data for comparison
comparison_df = pd.DataFrame({
    'Baseline Score': baseline_sdg_scores,
    'Simulated Score': simulated_sdg_scores_scenario1
})

print('\n--- What-If Scenario 1 Results ---')
print('\nInterventions Applied:')
for intervention in selected_interventions_scenario1:
    print(f"- {intervention['name']}")

print('\nComparison of SDG Scores (Baseline vs. Simulated):')
print(comparison_df)

print('\nChanges in SDG Scores:')
comparison_df['Change'] = comparison_df['Simulated Score'] - comparison_df['Baseline Score']
print(comparison_df[comparison_df['Change'] != 0])

# --- Original Cell 21 ---
print('--- Summary of Overall SDG Prevalence ---\n')
print(f"Total unique SDGs identified: {len(overall_sdg_frequency)}")
print(f"Total SDG tags across all documents: {overall_sdg_frequency.sum()}\n")

print('Top 5 Most Prevalent SDGs:')
print(overall_sdg_frequency.head())

print('\nBottom 5 Least Prevalent SDGs:')
print(overall_sdg_frequency.tail())

# --- Original Cell 22 ---
print('\n--- Summary of SDG Dimension Balance ---\n')
print(f"Average Economic SDGs per document: {average_economic_sdgs:.2f}")
print(f"Average Social SDGs per document: {average_social_sdgs:.2f}")
print(f"Average Environmental SDGs per document: {average_environmental_sdgs:.2f}")

# --- Original Cell 23 ---
print('\n--- Summary of Underrepresented SDGs, Regions, and Issues ---\n')

if not underrepresented_sdgs.empty:
    print(f'Underrepresented SDGs (frequency < {underrepresentation_threshold}):')
    print(underrepresented_sdgs)
else:
    print('No SDGs found below the underrepresentation threshold.')

print('\n' + '-'*50 + '\n')

if not underrepresented_regions.empty:
    print(f'Underrepresented Regions (document count < {underrepresentation_threshold}):')
    print(underrepresented_regions)
else:
    print('No regions found below the document count threshold.')

print('\n' + '-'*50 + '\n')

if not underrepresented_issues.empty:
    print(f'Underrepresented Issues (document count < {underrepresentation_threshold}):')
    print(underrepresented_issues)
else:
    print('No issues found below the document count threshold.')

# --- Original Cell 24 ---
print('\n--- Summary of Detected Policy Conflicts and Trade-offs ---\n')

if detected_conflicts:
    print(f'Total number of documents with detected conflicts: {len(detected_conflicts)}')
    print('\nExamples of Detected Conflicts (first 5 if available):')
    for i, conflict_info in enumerate(detected_conflicts[:5]):
        print(f"\nDocument Index: {conflict_info['document_index']}")
        print(f"  Text Sample: {conflict_info['document_text_sample']}")
        print(f"  Assigned SDGs: {conflict_info['assigned_sdgs']}")
        print(f"  Conflicting Pairs: {conflict_info['conflicting_pairs']}")
else:
    print('No policy conflicts were detected based on the defined pairs.')

# --- Original Cell 25 ---
print('\n--- Summary of What-If Scenario (Baseline vs. Simulated SDG Scores) ---\n')
print(comparison_df.to_string())

# --- Original Cell 26 ---
import matplotlib.pyplot as plt

print('\n--- Visualization of Overall SDG Distribution ---\n')

plt.figure(figsize=(12, 7))
overall_sdg_frequency.sort_values(ascending=False).plot(kind='bar', color='skyblue')
plt.title('Overall Distribution of Sustainable Development Goals')
plt.xlabel('Sustainable Development Goal')
plt.ylabel('Frequency of Appearance in Documents')
plt.xticks(rotation=45, ha='right') # Rotate labels for better readability
plt.tight_layout()
plt.savefig('output_figures/plot_01.png', bbox_inches='tight')
plt.show()


# --- Original Cell 27 ---
print('\n--- Visualization of What-If Scenario Impact (Baseline vs. Simulated) ---\n')

# Filter for SDGs where a change occurred
changed_sdgs_df = comparison_df[comparison_df['Change'] != 0].copy()

if not changed_sdgs_df.empty:
    # Prepare data for plotting
    plot_data = changed_sdgs_df[['Baseline Score', 'Simulated Score']]

    plt.figure(figsize=(14, 8))
    plot_data.plot(kind='bar', figsize=(14, 8), width=0.8, colormap='viridis')
    plt.title('Impact of What-If Scenario: Baseline vs. Simulated SDG Scores for Changed SDGs')
    plt.xlabel('Sustainable Development Goal')
    plt.ylabel('Score (0-100)')
    plt.xticks(rotation=45, ha='right')
    plt.legend(title='Score Type')
    plt.grid(axis='y', linestyle='--', alpha=0.7)
    plt.tight_layout()
    plt.savefig('output_figures/plot_02.png', bbox_inches='tight')
    plt.show()
else:
    print('No SDGs experienced a change in the simulated scenario to visualize.')


# --- Original Cell 28 ---
print('\n--- Visualization of What-If Scenario Impact (Baseline vs. Simulated) ---\n')

# Filter for SDGs where a change occurred
changed_sdgs_df = comparison_df[comparison_df['Change'] != 0].copy()

if not changed_sdgs_df.empty:
    # Prepare data for plotting
    plot_data = changed_sdgs_df[['Baseline Score', 'Simulated Score']]

    plt.figure(figsize=(14, 8))
    plot_data.plot(kind='bar', figsize=(14, 8), width=0.8, colormap='viridis')
    plt.title('Impact of What-If Scenario: Baseline vs. Simulated SDG Scores for Changed SDGs')
    plt.xlabel('Sustainable Development Goal')
    plt.ylabel('Score (0-100)')
    plt.xticks(rotation=45, ha='right')
    plt.legend(title='Score Type')
    plt.grid(axis='y', linestyle='--', alpha=0.7)
    plt.tight_layout()
    plt.savefig('output_figures/plot_03.png', bbox_inches='tight')
    plt.show()
else:
    print('No SDGs experienced a change in the simulated scenario to visualize.')

# --- Original Cell 29 ---
print('''
--- Visualization of What-If Scenario Impact (Baseline vs. Simulated) ---
''')

# Filter for SDGs where a change occurred
changed_sdgs_df = comparison_df[comparison_df['Change'] != 0].copy()

if not changed_sdgs_df.empty:
    # Prepare data for plotting
    plot_data = changed_sdgs_df[['Baseline Score', 'Simulated Score']]

    plt.figure(figsize=(14, 8))
    plot_data.plot(kind='bar', figsize=(14, 8), width=0.8, colormap='viridis')
    plt.title('Impact of What-If Scenario: Baseline vs. Simulated SDG Scores for Changed SDGs')
    plt.xlabel('Sustainable Development Goal')
    plt.ylabel('Score (0-100)')
    plt.xticks(rotation=45, ha='right')
    plt.legend(title='Score Type')
    plt.grid(axis='y', linestyle='--', alpha=0.7)
    plt.tight_layout()
    plt.savefig('output_figures/plot_04.png', bbox_inches='tight')
    plt.show()
else:
    print('No SDGs experienced a change in the simulated scenario to visualize.')

# --- Original Cell 30 ---
import sys
# !{sys.executable} -m pip install langdetect
print("langdetect installed successfully.")

# --- Original Cell 31 ---
import subprocess
try:
    import langdetect
except ImportError:
    print("Installing langdetect...")
    subprocess.check_call(["pip", "install", "langdetect"])

import pandas as pd
import os
import glob
import re
import string
from langdetect import detect, DetectorFactory
import nltk
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer
import random

# Ensure reproducibility for langdetect
DetectorFactory.seed = 0

# --- Re-create dummy data files (from cell f3f5b176) ---
csv_data1 = {
    'ID': [1, 2, 3, 4, 5],
    'Name': ['Alice', 'Bob', 'Charlie', 'David', 'Eve'],
    'Age': [24, 27, 22, 32, 29],
    'City': ['New York', 'Los Angeles', 'Chicago', 'Houston', 'Phoenix'],
    'Score': [85, 92, 78, 88, 95]
}
df1 = pd.DataFrame(csv_data1)
df1.to_csv('ngo_data.csv', index=False)

csv_data2 = {
    'SurveyID': [101, 102, 103, 104, 105],
    'Question1': ['Good', 'Neutral', 'Bad', 'Good', 'Good'],
    'Question2': [5, 3, 1, 4, 5],
    'RespondentAge': [45, 32, 60, 28, 51],
    'Income': [50000, 30000, None, 75000, 40000]
}
df2 = pd.DataFrame(csv_data2)
df2.to_csv('community_survey.csv', index=False)

with open('traditional_knowledge1.txt', 'w') as f:
    f.write('This document contains traditional knowledge related to sustainable farming practices.')
with open('traditional_knowledge2.txt', 'w') as f:
    f.write('This document details local remedies using indigenous plants.')

# --- Load DataFrames and Text Documents (from cell 4348b007) ---
csv_files = glob.glob('*.csv')
loaded_dataframes = {}
for csv_file in csv_files:
    df_name = os.path.splitext(csv_file)[0]
    df = pd.read_csv(csv_file)
    loaded_dataframes[df_name] = df

text_files = glob.glob('*.txt')
text_documents = []
for txt_file in text_files:
    with open(txt_file, 'r') as f:
        content = f.read()
        text_documents.append(content)

# --- Text Cleaning and Normalization (from cell 9a42f3c6) ---
all_texts = []
all_texts.extend(text_documents)
if 'ngo_data' in loaded_dataframes:
    df_ngo = loaded_dataframes['ngo_data']
    all_texts.extend(df_ngo['Name'].astype(str).tolist())
    all_texts.extend(df_ngo['City'].astype(str).tolist())
if 'community_survey' in loaded_dataframes:
    df_community = loaded_dataframes['community_survey']
    all_texts.extend(df_community['Question1'].astype(str).tolist())

def clean_text(text):
    text = str(text).lower()
    text = text.translate(str.maketrans('', '', string.punctuation))
    text = re.sub(r'[^a-z\s]', '', text)
    text = re.sub(r'\s+', ' ', text).strip()
    return text
cleaned_texts = [clean_text(text) for text in all_texts]

# --- Multilingual Text Processing (from cell 603a18ce) ---
text_languages = []
for text in cleaned_texts:
    try:
        lang = detect(text)
        text_languages.append(lang)
    except:
        text_languages.append('unknown')
english_texts = []
for i, text in enumerate(cleaned_texts):
    if text_languages[i] != 'en':
        english_texts.append(f"[Translated to English] {text}")
    else:
        english_texts.append(text)

# --- Tokenization, Stopword Removal, Lemmatization (from cell 9fb9a06b) ---
nltk.download('punkt', quiet=True)
nltk.download('stopwords', quiet=True)
nltk.download('wordnet', quiet=True)
nltk.download('punkt_tab', quiet=True)

stop_words = set(stopwords.words('english'))
lemmatizer = WordNetLemmatizer()
processed_texts = []
for i, text in enumerate(english_texts):
    tokens = word_tokenize(text)
    filtered_tokens = [word for word in tokens if word not in stop_words and word.isalpha()]
    lemmas = [lemmatizer.lemmatize(word) for word in filtered_tokens]
    processed_texts.append(lemmas)

# --- Prepare Data for SDG Classification (from cell bc820512) ---
final_prepared_texts = []
for doc_tokens in processed_texts:
    rejoined_text = ' '.join(doc_tokens)
    final_prepared_texts.append(rejoined_text)

# --- Apply Multi-Label SDG Classification (from cell f1d7f910) ---
dummy_sdgs = [
    'SDG 1: No Poverty', 'SDG 2: Zero Hunger', 'SDG 3: Good Health and Well-being',
    'SDG 4: Quality Education', 'SDG 5: Gender Equality', 'SDG 6: Clean Water and Sanitation',
    'SDG 7: Affordable and Clean Energy', 'SDG 8: Decent Work and Economic Growth',
    'SDG 9: Industry, Innovation, and Infrastructure', 'SDG 10: Reduced Inequalities',
    'SDG 11: Sustainable Cities and Communities', 'SDG 12: Responsible Consumption and Production',
    'SDG 13: Climate Action', 'SDG 14: Life Below Water', 'SDG 15: Life On Land',
    'SDG 16: Peace, Justice, and Strong Institutions', 'SDG 17: Partnerships for the Goals'
]
simulated_sdg_labels = []
for doc_text in final_prepared_texts:
    num_sdgs_to_assign = random.randint(1, 3)
    selected_sdgs = random.sample(dummy_sdgs, num_sdgs_to_assign)
    simulated_sdg_labels.append(selected_sdgs)

# --- Analyze SDG Tagging by Region and Issue (creation of df_analysis from cell 7536372a) ---
dummy_regions = ['East Africa', 'West Africa', 'Southern Africa', 'Central Africa', 'North Africa']
simulated_regions = [random.choice(dummy_regions) for _ in range(len(final_prepared_texts))]
dummy_issues = ['Agriculture', 'Education', 'Health', 'Infrastructure', 'Governance', 'Environment']
simulated_issues = [random.choice(dummy_issues) for _ in range(len(final_prepared_texts))]

data_for_df = {
    'text': final_prepared_texts,
    'sdg_labels': simulated_sdg_labels,
    'region': simulated_regions,
    'issue': simulated_issues
}
df_analysis = pd.DataFrame(data_for_df)

# --- Coherence and Gap Analysis (SDG categories and function from cells 25b6541f and 1ba7c7d1) ---
ECONOMIC_SDGS = {'SDG 1', 'SDG 8', 'SDG 9', 'SDG 10', 'SDG 12', 'SDG 17'}
SOCIAL_SDGS = {'SDG 1', 'SDG 2', 'SDG 3', 'SDG 4', 'SDG 5', 'SDG 6', 'SDG 7', 'SDG 11', 'SDG 16', 'SDG 17'}
ENVIRONMENTAL_SDGS = {'SDG 2', 'SDG 6', 'SDG 7', 'SDG 12', 'SDG 13', 'SDG 14', 'SDG 15', 'SDG 17'}

def count_sdg_dimensions(sdg_labels):
    economic_count = 0
    social_count = 0
    environmental_count = 0

    for label in sdg_labels:
        sdg_number = label.split(':')[0].strip()

        if sdg_number in ECONOMIC_SDGS:
            economic_count += 1
        if sdg_number in SOCIAL_SDGS:
            social_count += 1
        if sdg_number in ENVIRONMENTAL_SDGS:
            environmental_count += 1

    return economic_count, social_count, environmental_count

# Apply the function to df_analysis to get dimension counts
df_analysis[['economic_sdgs', 'social_sdgs', 'environmental_sdgs']] = df_analysis['sdg_labels'].apply(lambda x: pd.Series(count_sdg_dimensions(x)))

# Recalculate average counts per dimension
average_economic_sdgs = df_analysis['economic_sdgs'].mean()
average_social_sdgs = df_analysis['social_sdgs'].mean()
average_environmental_sdgs = df_analysis['environmental_sdgs'].mean()

# --- Produce the SDG Dimensional Balance Table ---
print('\n--- SDG Dimensional Balance Table (Average Counts Per Document) ---\n')

# Instructions 1, 2, 3: Print the value of each average
print(f"Average Economic SDGs per document: {average_economic_sdgs:.2f}")
print(f"Average Social SDGs per document: {average_social_sdgs:.2f}")
print(f"Average Environmental SDGs per document: {average_environmental_sdgs:.2f}\n")

sdg_balance_data = {
    'Dimension': ['Economic', 'Social', 'Environmental'],
    'Average Count per Document': [average_economic_sdgs, average_social_sdgs, average_environmental_sdgs]
}
sdg_balance_df = pd.DataFrame(sdg_balance_data)
sdg_balance_df['Average Count per Document'] = sdg_balance_df['Average Count per Document'].round(2)

print(sdg_balance_df.to_string(index=False))

# --- Original Cell 32 ---
import subprocess
try:
    import langdetect
except ImportError:
    print("Installing langdetect...")
    subprocess.check_call(["pip", "install", "langdetect"])

import pandas as pd
import random

# Re-define baseline_sdg_scores (from cell 930fdfe1)
baseline_sdg_scores = {
    f'SDG {i}': random.randint(30, 70) for i in range(1, 18)
}

# Re-define policy_interventions (from cell 930fdfe1)
policy_interventions = [
    {
        'name': 'Investment in Education Programs',
        'impact': {'SDG 4': 15, 'SDG 1': 5, 'SDG 5': 7}
    },
    {
        'name': 'Sustainable Agriculture Initiative',
        'impact': {'SDG 2': 20, 'SDG 13': 10, 'SDG 15': 8}
    },
    {
        'name': 'Healthcare Infrastructure Project',
        'impact': {'SDG 3': 18, 'SDG 6': 5, 'SDG 1': 3}
    },
    {
        'name': 'Renewable Energy Transition',
        'impact': {'SDG 7': 25, 'SDG 13': 12, 'SDG 9': 5}
    },
    {
        'name': 'Water Conservation Policy',
        'impact': {'SDG 6': 20, 'SDG 12': 8, 'SDG 14': 5}
    }
]

# Re-define simulate_what_if_scenario function (from cell a635719d)
def simulate_what_if_scenario(baseline_scores, selected_interventions):
    simulated_scores = baseline_scores.copy()
    for intervention in selected_interventions:
        for sdg, impact_value in intervention['impact'].items():
            current_score = simulated_scores.get(sdg, 0)
            new_score = current_score + impact_value
            simulated_scores[sdg] = min(new_score, 100)
    return simulated_scores

# Re-run the demonstration of the prototype (from cell 350ef127)
selected_interventions_scenario1 = [
    policy_interventions[0],
    policy_interventions[2]
]

simulated_sdg_scores_scenario1 = simulate_what_if_scenario(baseline_sdg_scores, selected_interventions_scenario1)

# Re-create comparison_df
comparison_df = pd.DataFrame({
    'Baseline Score': baseline_sdg_scores,
    'Simulated Score': simulated_sdg_scores_scenario1
})
comparison_df['Change'] = comparison_df['Simulated Score'] - comparison_df['Baseline Score']


print('\n--- What-If Scenario Comparison Table (Baseline vs. Simulated SDG Scores) ---\n')
print(comparison_df.to_string())

# --- Original Cell 33 ---
import itertools
import subprocess
try:
    import langdetect
except ImportError:
    print("Installing langdetect...")
    subprocess.check_call(["pip", "install", "langdetect"])

import pandas as pd # Ensure pandas is imported as df_analysis is a DataFrame

# Re-define a list of known conflicting SDG pairs (from cell 3c2e1949)
conflicting_sdg_pairs = [
    ('SDG 8: Decent Work and Economic Growth', 'SDG 13: Climate Action'),
    ('SDG 9: Industry, Innovation, and Infrastructure', 'SDG 15: Life On Land'),
    ('SDG 2: Zero Hunger', 'SDG 12: Responsible Consumption and Production'),
    ('SDG 1: No Poverty', 'SDG 10: Reduced Inequalities')
]

detected_conflicts = []

# Iterate through each document's sdg_labels in the df_analysis DataFrame
# df_analysis is assumed to be defined from previous successful execution (e.g., cell 7c6907f1)
for index, row in df_analysis.iterrows():
    doc_sdgs = set(row['sdg_labels'])
    document_conflicts = []

    # Check if any of the predefined conflicting SDG pairs co-occur
    for conflict_pair in conflicting_sdg_pairs:
        sdg1, sdg2 = conflict_pair
        if sdg1 in doc_sdgs and sdg2 in doc_sdgs:
            document_conflicts.append(conflict_pair)

    # Store the identified conflicts
    if document_conflicts:
        detected_conflicts.append({
            'document_index': index,
            'document_text_sample': row['text'][:100] + '...', # Store a sample of the text
            'assigned_sdgs': list(doc_sdgs),
            'conflicting_pairs': document_conflicts
        })

print('\n--- Policy Conflicts Summary Table ---\n')

# Check if the detected_conflicts list is not empty
if detected_conflicts:
    # Print the total number of documents with conflicts
    print(f'Total number of documents with detected conflicts: {len(detected_conflicts)}')
    print('\nExamples of Detected Conflicts (first 5 if available):')
    # Iterate through the first few entries (e.g., 5) in detected_conflicts
    for i, conflict_info in enumerate(detected_conflicts[:5]):
        print(f"\nDocument Index: {conflict_info['document_index']}")
        print(f"  Text Sample: {conflict_info['document_text_sample']}")
        print(f"  Assigned SDGs: {conflict_info['assigned_sdgs']}")
        print(f"  Conflicting Pairs: {conflict_info['conflicting_pairs']}")
else:
    # Print a message stating that no policy conflicts were found
    print('No policy conflicts were detected based on the defined pairs.')

# --- Original Cell 34 ---
import subprocess
try:
    import langdetect
except ImportError:
    print("Installing langdetect...")
    subprocess.check_call(["pip", "install", "langdetect"])

import pandas as pd

# Helper function to flatten list of lists for SDG counting (re-defined from cell 7536372a)
def flatten_sdg_labels(list_of_lists):
    flat_list = []
    for sublist in list_of_lists:
        for item in sublist:
            flat_list.append(item)
    return flat_list

# Recalculate the overall frequency of each SDG (from cell 7536372a)
# df_analysis is assumed to be defined from previous successful execution (e.g., cell 7c6907f1)
all_sdgs_flat = flatten_sdg_labels(df_analysis['sdg_labels'])
overall_sdg_frequency = pd.Series(all_sdgs_flat).value_counts()

print('\n--- Overall SDG Prevalence Table ---\n')

# Convert the Series to a DataFrame for better table formatting
ovr_sdg_freq_df = overall_sdg_frequency.reset_index()
ovr_sdg_freq_df.columns = ['SDG', 'Frequency']

print('Total unique SDGs identified:', len(ovr_sdg_freq_df))
print('Total SDG tags across all documents:', ovr_sdg_freq_df['Frequency'].sum(), '\n')

print('Overall SDG Frequency (All SDGs):')
print(ovr_sdg_freq_df.to_string(index=False))

print('\nTop 5 Most Prevalent SDGs:')
print(ovr_sdg_freq_df.head(5).to_string(index=False))

print('\nBottom 5 Least Prevalent SDGs:')
print(ovr_sdg_freq_df.tail(5).to_string(index=False))

# --- Original Cell 35 ---
import matplotlib.pyplot as plt

print('\n--- Visualization of Overall SDG Distribution ---\n')

plt.figure(figsize=(12, 7))
overall_sdg_frequency.sort_values(ascending=False).plot(kind='bar', color='skyblue')
plt.title('Overall Distribution of Sustainable Development Goals')
plt.xlabel('Sustainable Development Goal')
plt.ylabel('Frequency of Appearance in Documents')
plt.xticks(rotation=45, ha='right') # Rotate labels for better readability
plt.tight_layout()
plt.savefig('output_figures/plot_05.png', bbox_inches='tight')
plt.show()

# --- Original Cell 36 ---
import matplotlib.pyplot as plt

print('''
--- Visualization of What-If Scenario Impact (Baseline vs. Simulated) ---
''')

# Filter for SDGs where a change occurred
changed_sdgs_df = comparison_df[comparison_df['Change'] != 0].copy()

if not changed_sdgs_df.empty:
    # Prepare data for plotting
    plot_data = changed_sdgs_df[['Baseline Score', 'Simulated Score']]

    plt.figure(figsize=(14, 8))
    plot_data.plot(kind='bar', figsize=(14, 8), width=0.8, colormap='viridis')
    plt.title('Impact of What-If Scenario: Baseline vs. Simulated SDG Scores for Changed SDGs')
    plt.xlabel('Sustainable Development Goal')
    plt.ylabel('Score (0-100)')
    plt.xticks(rotation=45, ha='right')
    plt.legend(title='Score Type')
    plt.grid(axis='y', linestyle='--', alpha=0.7)
    plt.tight_layout()
    plt.savefig('output_figures/plot_06.png', bbox_inches='tight')
    plt.show()
else:
    print('No SDGs experienced a change in the simulated scenario to visualize.')

# --- Original Cell 37 ---
import subprocess
try:
    import langdetect
except ImportError:
    print("Installing langdetect...")
    subprocess.check_call(["pip", "install", "langdetect"])

import pandas as pd

# Re-define underrepresentation_threshold if not already defined (assuming it was 2 in previous steps)
# This value should be consistent with the previous analysis.
underrepresentation_threshold = 2

# Re-calculate overall_sdg_frequency, underrepresented_sdgs (from cell b39bf6be)
# Requires `flatten_sdg_labels` and `df_analysis` to be defined from previous steps.
# Assuming df_analysis and flatten_sdg_labels are already in scope from the last full execution.
def flatten_sdg_labels(list_of_lists):
    flat_list = []
    for sublist in list_of_lists:
        for item in sublist:
            flat_list.append(item)
    return flat_list

# Check if df_analysis is defined, otherwise create a dummy to prevent errors.
# In a real scenario, this would rely on prior execution.
if 'df_analysis' not in locals():
    print("Warning: df_analysis not found, creating dummy for demonstration. This might affect results.")
    # Create dummy df_analysis if it somehow got lost (should not happen if preceding cells ran)
    df_analysis = pd.DataFrame({
        'sdg_labels': [['SDG 1: No Poverty', 'SDG 17: Partnerships for the Goals'], ['SDG 1: No Poverty']],
        'region': ['East Africa', 'West Africa'],
        'issue': ['Education', 'Health']
    })

all_sdgs_flat = flatten_sdg_labels(df_analysis['sdg_labels'])
overall_sdg_frequency = pd.Series(all_sdgs_flat).value_counts()
underrepresented_sdgs = overall_sdg_frequency[overall_sdg_frequency < underrepresentation_threshold]

# Re-calculate underrepresented_regions and underrepresented_issues (from cell 68ce1dfd)
region_document_counts = df_analysis['region'].value_counts()
underrepresented_regions = region_document_counts[region_document_counts < underrepresentation_threshold]

issue_document_counts = df_analysis['issue'].value_counts()
underrepresented_issues = issue_document_counts[issue_document_counts < underrepresentation_threshold]

print('\n--- Underrepresentation Summary Table ---\n')

# 1. Print a header for the 'Underrepresented SDGs' section.
print(f'Underrepresented SDGs (frequency < {underrepresentation_threshold}):')
# 2. If the `underrepresented_sdgs` Series is not empty, convert it to a DataFrame with columns 'SDG' and 'Frequency', and then print this DataFrame.
if not underrepresented_sdgs.empty:
    underrepresented_sdgs_df = underrepresented_sdgs.reset_index()
    underrepresented_sdgs_df.columns = ['SDG', 'Frequency']
    print(underrepresented_sdgs_df.to_string(index=False))
# 3. If `underrepresented_sdgs` is empty, print a message indicating no SDGs were found below the threshold.
else:
    print('No SDGs found below the underrepresentation threshold.')

# 4. Print a separator line.
print('\n' + '-'*50 + '\n')

# 5. Print a header for the 'Underrepresented Regions' section.
print(f'Underrepresented Regions (document count < {underrepresentation_threshold}):')
# 6. If the `underrepresented_regions` Series is not empty, convert it to a DataFrame with columns 'Region' and 'Document Count', and then print this DataFrame.
if not underrepresented_regions.empty:
    underrepresented_regions_df = underrepresented_regions.reset_index()
    underrepresented_regions_df.columns = ['Region', 'Document Count']
    print(underrepresented_regions_df.to_string(index=False))
# 7. If `underrepresented_regions` is empty, print a message indicating no regions were found below the threshold.
else:
    print('No regions found below the document count threshold.')

# 8. Print a separator line.
print('\n' + '-'*50 + '\n')

# 9. Print a header for the 'Underrepresented Issues' section.
print(f'Underrepresented Issues (document count < {underrepresentation_threshold}):')
# 10. If the `underrepresented_issues` Series is not empty, convert it to a DataFrame with columns 'Issue' and 'Document Count', and then print this DataFrame.
if not underrepresented_issues.empty:
    underrepresented_issues_df = underrepresented_issues.reset_index()
    underrepresented_issues_df.columns = ['Issue', 'Document Count']
    print(underrepresented_issues_df.to_string(index=False))
# 11. If `underrepresented_issues` is empty, print a message indicating no issues were found below the threshold.
else:
    print('No issues found below the document count threshold.')


# =====================================================================
# TASK 2: System Architecture Diagram
# =====================================================================
def create_architecture_diagram():
    import matplotlib.pyplot as plt
    fig, ax = plt.subplots(figsize=(14, 12))
    ax.axis('off')

    # Define styles based on requested visual hierarchy
    # Core pipeline (neutral)
    core_box = dict(boxstyle="round,pad=1.5", edgecolor="#94A3B8", lw=1.5, facecolor="#F1F5F9")
    ai_box = dict(boxstyle="round,pad=2", edgecolor="#475569", lw=2, facecolor="#E2E8F0")

    # Outputs (green) - applied to Policy
    policy_box = dict(boxstyle="round,pad=1.5", facecolor="#F0FDF4", edgecolor="#22C55E", lw=2)

    # Analysis (orange) - applied to Pillars
    pillar1_box = dict(boxstyle="round,pad=1.5", facecolor="#FFF7ED", edgecolor="#F97316", lw=2)
    pillar2_box = dict(boxstyle="round,pad=1.5", facecolor="#FFF7ED", edgecolor="#F97316", lw=2)
    pillar3_box = dict(boxstyle="round,pad=1.5", facecolor="#FFF7ED", edgecolor="#F97316", lw=2)

    arrow_style = dict(arrowstyle="->", color="#64748B", lw=2)
    arrow_bi_style = dict(arrowstyle="<->", color="#64748B", lw=2)
    feedback_style = dict(arrowstyle="->", color="#EF4444", lw=2, ls="dashed", connectionstyle="arc3,rad=-0.3")
    feedback_style_left = dict(arrowstyle="->", color="#EF4444", lw=2, ls="dashed", connectionstyle="arc3,rad=0.3")

    # Titles and Headers
    ax.text(0.5, 0.98, "Mapping Indigenous Problems to SDGs: Solution Roadmap",
            ha='center', va='center', fontsize=20, fontweight='bold',
            bbox=dict(boxstyle="round,pad=0.6", facecolor="#0F172A", edgecolor="none"), color="white")

    # Core blocks (equal width simulated by padding spaces and centering)
    core_width_str_pad = "                                                                        "

    # Layer 1: Community Data Collection
    ax.text(0.5, 0.85, "Community Data Collection\n\nLocal NGOs & Reports      Community Surveys      Traditional Knowledge" + "\n" + core_width_str_pad,
            ha='center', va='center', fontsize=12, fontweight='bold', bbox=core_box)

    # Layer 2: Preprocessing
    ax.text(0.5, 0.68, "Data Preprocessing & Normalization\n\nText Cleaning & Parsing  <----->  Language Processing" + "\n" + core_width_str_pad,
            ha='center', va='center', fontsize=12, fontweight='bold', bbox=core_box)

    # Layer 3: AI
    ax.text(0.5, 0.48, "AI     RoBERTa-Large SDG Classification\n\nMulti-Label AI Model" + "\n" + core_width_str_pad,
            ha='center', va='center', fontsize=14, fontweight='bold', bbox=ai_box)

    # Layer 4: Pillars (Analysis - Orange)
    ax.text(0.18, 0.22, "Automated SDG Mapping\n\n• SDG Tagging\n\n• Conflict Detection",
            ha='center', va='center', fontsize=12, fontweight='bold', bbox=pillar1_box)

    ax.text(0.50, 0.22, "Coherence & Gap Analysis\n\n• Pillar Balance Score\n\n• Gap Identification",
            ha='center', va='center', fontsize=12, fontweight='bold', bbox=pillar2_box)

    ax.text(0.82, 0.22, "Solution Framework Generation\n\n• AI Recommender Systems\n\n• Solution & Action Plans\n\n• Custom Scenarios",
            ha='center', va='center', fontsize=12, fontweight='bold', bbox=pillar3_box)

    # Layer 5: Policy Recommendations (Output - Green)
    ax.text(0.5, 0.02, "Policy Recommendations\n\nInteractive Dashboard        Policy Briefs        Engage Communities\nSDG Insights & Maps        Actionable Solutions        Local Feedback" + "\n" + core_width_str_pad,
            ha='center', va='center', fontsize=12, fontweight='bold', bbox=policy_box)

    # Core Vertical Arrows (Two arrows: forward + backward as requested)
    # Between Data Collection and Preprocessing
    ax.annotate('', xy=(0.48, 0.74), xytext=(0.48, 0.80), arrowprops=dict(arrowstyle="->", color="#64748B", lw=2))
    ax.annotate('', xy=(0.52, 0.80), xytext=(0.52, 0.74), arrowprops=dict(arrowstyle="->", color="#64748B", lw=2))

    # Between Preprocessing and AI
    ax.annotate('', xy=(0.48, 0.55), xytext=(0.48, 0.62), arrowprops=dict(arrowstyle="->", color="#64748B", lw=2))
    ax.annotate('', xy=(0.52, 0.62), xytext=(0.52, 0.55), arrowprops=dict(arrowstyle="->", color="#64748B", lw=2))

    # AI to Pillars (Bi-directional)
    ax.annotate('', xy=(0.25, 0.30), xytext=(0.45, 0.41), arrowprops=arrow_bi_style)
    ax.annotate('', xy=(0.5, 0.30), xytext=(0.5, 0.41), arrowprops=arrow_bi_style)
    ax.annotate('', xy=(0.75, 0.30), xytext=(0.55, 0.41), arrowprops=arrow_bi_style)

    # Pillars to Policy (Bi-directional)
    ax.annotate('', xy=(0.25, 0.08), xytext=(0.25, 0.13), arrowprops=arrow_bi_style)
    ax.annotate('', xy=(0.5, 0.08), xytext=(0.5, 0.13), arrowprops=arrow_bi_style)
    ax.annotate('', xy=(0.75, 0.08), xytext=(0.75, 0.13), arrowprops=arrow_bi_style)

    # Parallel Pillars Horizontal Interaction (Bi-directional between each pair)
    # Mapping <-> Gap Analysis
    ax.annotate('', xy=(0.34, 0.24), xytext=(0.36, 0.24), arrowprops=dict(arrowstyle="->", color="#64748B", lw=2))
    ax.annotate('', xy=(0.36, 0.20), xytext=(0.34, 0.20), arrowprops=dict(arrowstyle="->", color="#64748B", lw=2))

    # Gap Analysis <-> Solution Framework
    ax.annotate('', xy=(0.64, 0.24), xytext=(0.66, 0.24), arrowprops=dict(arrowstyle="->", color="#64748B", lw=2))
    ax.annotate('', xy=(0.66, 0.20), xytext=(0.64, 0.20), arrowprops=dict(arrowstyle="->", color="#64748B", lw=2))

    # Mapping <-> Solution Framework (Overarching)
    ax.annotate('', xy=(0.25, 0.30), xytext=(0.75, 0.30), arrowprops=dict(arrowstyle="<->", color="#64748B", lw=2, ls="dotted", connectionstyle="arc3,rad=-0.2"))

    # --- FEEDBACK LOOPS (Dashed red) ---
    feedback_font = dict(color="#B91C1C", fontsize=10, fontweight='bold', fontstyle='italic', bbox=dict(facecolor='white', edgecolor='none', alpha=0.8, pad=0.1))

    # AI -> Community Data Collection
    ax.annotate('', xy=(0.15, 0.85), xytext=(0.15, 0.48), arrowprops=feedback_style_left)
    ax.text(0.08, 0.65, "Feedback", ha='center', va='center', **feedback_font)

    # Solution Framework -> Community Data Collection
    ax.annotate('', xy=(0.85, 0.85), xytext=(0.85, 0.28), arrowprops=feedback_style)
    ax.text(0.92, 0.55, "Feedback", ha='center', va='center', **feedback_font)

    plt.tight_layout()
    plt.savefig('output_figures/plot_07.png', bbox_inches='tight', dpi=300)
    plt.show()

create_architecture_diagram()


# =====================================================================
# TASK 1: Reproduce and Extend Visualizations (Expanding to > 18 plots)
# =====================================================================

# Recreating original ~6 plots logic conceptually, but doing it correctly and richly:
# Plot 1: Overall SDG Distribution (Bar Chart)
plt.figure(figsize=(12, 7))
overall_sdg_frequency.sort_values(ascending=False).plot(kind='bar', color='skyblue')
plt.title('Plot 1: Overall Distribution of Sustainable Development Goals (Bar)')
plt.xlabel('Sustainable Development Goal')
plt.ylabel('Frequency of Appearance in Documents')
plt.xticks(rotation=45, ha='right')
plt.tight_layout()
plt.savefig('output_figures/plot_08.png', bbox_inches='tight')
plt.show()

# Plot 2: Impact of What-If Scenario (Baseline vs. Simulated SDG Scores)
changed_sdgs_df = comparison_df[comparison_df['Change'] != 0].copy()
if not changed_sdgs_df.empty:
    plot_data = changed_sdgs_df[['Baseline Score', 'Simulated Score']]
    plt.figure(figsize=(14, 8))
    plot_data.plot(kind='bar', figsize=(14, 8), width=0.8, colormap='viridis')
    plt.title('Plot 2: Impact of What-If Scenario: Baseline vs. Simulated SDG Scores for Changed SDGs')
    plt.xlabel('Sustainable Development Goal')
    plt.ylabel('Score (0-100)')
    plt.xticks(rotation=45, ha='right')
    plt.legend(title='Score Type')
    plt.grid(axis='y', linestyle='--', alpha=0.7)
    plt.tight_layout()
    plt.savefig('output_figures/plot_09.png', bbox_inches='tight')
    plt.show()

# Additional Rich Visualizations (>16 more plots)

# Plot 3: Horizontal Bar Chart of Overall SDG Distribution
plt.figure(figsize=(12, 8))
overall_sdg_frequency.sort_values().plot(kind='barh', color='coral')
plt.title('Plot 3: Overall Distribution of Sustainable Development Goals (Horizontal)')
plt.xlabel('Frequency')
plt.ylabel('Sustainable Development Goal')
plt.tight_layout()
plt.savefig('output_figures/plot_10.png', bbox_inches='tight')
plt.show()

# Plot 4: Pie Chart of SDG Dimensions (Economic, Social, Environmental)
plt.figure(figsize=(8, 8))
plt.pie(sdg_balance_df['Average Count per Document'], labels=sdg_balance_df['Dimension'], autopct='%1.1f%%', colors=['#ff9999','#66b3ff','#99ff99'])
plt.title('Plot 4: Proportion of SDG Dimensions per Document')
plt.tight_layout()
plt.savefig('output_figures/plot_11.png', bbox_inches='tight')
plt.show()

# Plot 5: Scatter Plot of Baseline vs Simulated Scores
plt.figure(figsize=(10, 6))
plt.scatter(comparison_df['Baseline Score'], comparison_df['Simulated Score'], color='blue', alpha=0.6)
plt.plot([0, 100], [0, 100], 'r--', label='No Change Line')
plt.title('Plot 5: Scatter Plot of Baseline vs Simulated SDG Scores')
plt.xlabel('Baseline Score')
plt.ylabel('Simulated Score')
plt.legend()
plt.tight_layout()
plt.savefig('output_figures/plot_12.png', bbox_inches='tight')
plt.show()

# Plot 6: Heatmap of Simulated SDG Co-occurrences
# Create a dummy co-occurrence matrix
all_sdgs = sorted(list(set(flatten_sdg_labels(df_analysis['sdg_labels']))))
co_occurence = pd.DataFrame(0, index=all_sdgs, columns=all_sdgs)
for labels in df_analysis['sdg_labels']:
    for sdg1 in labels:
        for sdg2 in labels:
            co_occurence.loc[sdg1, sdg2] += 1
plt.figure(figsize=(12, 10))
sns.heatmap(co_occurence, cmap='Blues', annot=False)
plt.title('Plot 6: Heatmap of SDG Co-occurrences in Documents')
plt.tight_layout()
plt.savefig('output_figures/plot_13.png', bbox_inches='tight')
plt.show()

# Plot 7: Distribution of Regions in the Dataset
plt.figure(figsize=(10, 6))
df_analysis['region'].value_counts().plot(kind='bar', color='purple')
plt.title('Plot 7: Distribution of Regions in Processed Documents')
plt.xlabel('Region')
plt.ylabel('Count')
plt.xticks(rotation=45, ha='right')
plt.tight_layout()
plt.savefig('output_figures/plot_14.png', bbox_inches='tight')
plt.show()

# Plot 8: Distribution of Issues in the Dataset
plt.figure(figsize=(10, 6))
df_analysis['issue'].value_counts().plot(kind='bar', color='orange')
plt.title('Plot 8: Distribution of Core Issues in Processed Documents')
plt.xlabel('Issue Category')
plt.ylabel('Count')
plt.xticks(rotation=45, ha='right')
plt.tight_layout()
plt.savefig('output_figures/plot_15.png', bbox_inches='tight')
plt.show()

# Plot 9: Average SDG Count per Document by Region
region_sdg_counts = df_analysis.groupby('region')['sdg_labels'].apply(lambda x: x.apply(len).mean())
plt.figure(figsize=(10, 6))
region_sdg_counts.plot(kind='bar', color='teal')
plt.title('Plot 9: Average Number of SDGs Tagged per Document by Region')
plt.xlabel('Region')
plt.ylabel('Average Number of SDGs')
plt.xticks(rotation=45, ha='right')
plt.tight_layout()
plt.savefig('output_figures/plot_16.png', bbox_inches='tight')
plt.show()

# Plot 10: Top 5 Most Prevalent SDGs (Bar)
plt.figure(figsize=(10, 6))
overall_sdg_frequency.head(5).plot(kind='bar', color='green')
plt.title('Plot 10: Top 5 Most Prevalent SDGs')
plt.xlabel('SDG')
plt.ylabel('Frequency')
plt.xticks(rotation=45, ha='right')
plt.tight_layout()
plt.savefig('output_figures/plot_17.png', bbox_inches='tight')
plt.show()

# Plot 11: Bottom 5 Least Prevalent SDGs (Bar)
plt.figure(figsize=(10, 6))
overall_sdg_frequency.tail(5).plot(kind='bar', color='red')
plt.title('Plot 11: Bottom 5 Least Prevalent SDGs')
plt.xlabel('SDG')
plt.ylabel('Frequency')
plt.xticks(rotation=45, ha='right')
plt.tight_layout()
plt.savefig('output_figures/plot_18.png', bbox_inches='tight')
plt.show()

# Plot 12: Box Plot of Baseline SDG Scores
plt.figure(figsize=(8, 6))
sns.boxplot(y=comparison_df['Baseline Score'], color='lightblue')
plt.title('Plot 12: Box Plot of Baseline SDG Scores')
plt.ylabel('Score (0-100)')
plt.tight_layout()
plt.savefig('output_figures/plot_19.png', bbox_inches='tight')
plt.show()

# Plot 13: Box Plot of Simulated SDG Scores
plt.figure(figsize=(8, 6))
sns.boxplot(y=comparison_df['Simulated Score'], color='lightgreen')
plt.title('Plot 13: Box Plot of Simulated SDG Scores')
plt.ylabel('Score (0-100)')
plt.tight_layout()
plt.savefig('output_figures/plot_20.png', bbox_inches='tight')
plt.show()

# Plot 14: Difference in Scores (Line Plot)
plt.figure(figsize=(12, 6))
plt.plot(comparison_df.index, comparison_df['Change'], marker='o', color='purple', linestyle='-')
plt.title('Plot 14: Change in SDG Scores due to Policy Interventions')
plt.xlabel('Sustainable Development Goal')
plt.ylabel('Score Change')
plt.xticks(rotation=90)
plt.grid(True, linestyle='--', alpha=0.5)
plt.tight_layout()
plt.savefig('output_figures/plot_21.png', bbox_inches='tight')
plt.show()

# Plot 15: Area Plot of Dimension Counts over mock time/documents
plt.figure(figsize=(12, 6))
df_analysis[['economic_sdgs', 'social_sdgs', 'environmental_sdgs']].plot(kind='area', stacked=True, alpha=0.6)
plt.title('Plot 15: Area Plot of SDG Dimensions across Documents')
plt.xlabel('Document Index')
plt.ylabel('Number of SDGs')
plt.tight_layout()
plt.savefig('output_figures/plot_22.png', bbox_inches='tight')
plt.show()

# Plot 16: Histogram of Text Lengths
df_analysis['text_length'] = df_analysis['text'].apply(len)
plt.figure(figsize=(10, 6))
sns.histplot(df_analysis['text_length'], bins=15, kde=True, color='brown')
plt.title('Plot 16: Distribution of Document Text Lengths (Characters)')
plt.xlabel('Text Length')
plt.ylabel('Frequency')
plt.tight_layout()
plt.savefig('output_figures/plot_23.png', bbox_inches='tight')
plt.show()

# Plot 17: Scatter Plot of Text Length vs Number of SDGs
df_analysis['sdg_count'] = df_analysis['sdg_labels'].apply(len)
plt.figure(figsize=(10, 6))
sns.scatterplot(x='text_length', y='sdg_count', data=df_analysis, hue='region', s=100)
plt.title('Plot 17: Text Length vs Number of SDGs Assigned (by Region)')
plt.xlabel('Text Length (Characters)')
plt.ylabel('Number of SDGs Assigned')
plt.legend(bbox_to_anchor=(1.05, 1), loc='upper left')
plt.tight_layout()
plt.savefig('output_figures/plot_24.png', bbox_inches='tight')
plt.show()

# Plot 18: Bubble Chart of Region vs Issue (bubble size = document count)
region_issue_counts = df_analysis.groupby(['region', 'issue']).size().reset_index(name='count')
plt.figure(figsize=(12, 8))
sns.scatterplot(data=region_issue_counts, x='region', y='issue', size='count', sizes=(100, 1000), hue='count', palette='YlOrRd')
plt.title('Plot 18: Bubble Chart of Documents by Region and Issue')
plt.xlabel('Region')
plt.ylabel('Issue Category')
plt.legend(bbox_to_anchor=(1.05, 1), loc='upper left')
plt.tight_layout()
plt.savefig('output_figures/plot_25.png', bbox_inches='tight')
plt.show()

# Plot 19: Stacked Bar Chart of Region vs Dimensions
region_dims = df_analysis.groupby('region')[['economic_sdgs', 'social_sdgs', 'environmental_sdgs']].sum()
plt.figure(figsize=(12, 7))
region_dims.plot(kind='bar', stacked=True, colormap='Set2')
plt.title('Plot 19: Stacked Bar Chart of SDG Dimensions by Region')
plt.xlabel('Region')
plt.ylabel('Total SDG Tags')
plt.xticks(rotation=45, ha='right')
plt.tight_layout()
plt.savefig('output_figures/plot_26.png', bbox_inches='tight')
plt.show()

# Plot 20: Violin Plot of Baseline vs Simulated Scores
melted_scores = pd.melt(comparison_df.reset_index(), id_vars='index', value_vars=['Baseline Score', 'Simulated Score'], var_name='Score Type', value_name='Score')
plt.figure(figsize=(12, 6))
sns.violinplot(x='Score Type', y='Score', data=melted_scores, palette='Pastel1')
plt.title('Plot 20: Violin Plot comparing Baseline and Simulated Score Distributions')
plt.tight_layout()
plt.savefig('output_figures/plot_27.png', bbox_inches='tight')
plt.show()

plt.savefig('output_figures/plot_28.png', bbox_inches='tight')
print("All plots generated successfully. Uncomment plt.show() statements to display them in interactive environments.")





def create_flowchart_diagram():
    import matplotlib.pyplot as plt
    import matplotlib.patches as patches

    # Matching the exact style of the uploaded Bionic Mushroom flowchart
    # 1. Plain rectangular boxes with 1px black borders (no FancyBboxPatch)
    # 2. Standard colors: lightgrey, lightblue, palegreen, khaki, wheat, plum, lightpink
    # 3. Standard thin black arrows for forward progression, thin bright green/red/purple for conditions
    # 4. Serif font for node text, bold sans-serif for title

    fig, ax = plt.subplots(figsize=(12, 16), dpi=300)
    ax.axis('off')

    # Helper to draw shapes
    def draw_ellipse(x, y, w, h, fc):
        ax.add_patch(patches.Ellipse((x, y), w, h, facecolor=fc, edgecolor='black', lw=1, zorder=1))

    def draw_rect(x, y, w, h, fc):
        ax.add_patch(patches.Rectangle((x - w/2, y - h/2), w, h, facecolor=fc, edgecolor='black', lw=1, zorder=1))

    def draw_diamond(x, y, w, h, fc):
        ax.add_patch(patches.Polygon([
            (x, y + h/2), (x + w/2, y), (x, y - h/2), (x - w/2, y)
        ], facecolor=fc, edgecolor='black', lw=1, zorder=1))

    def draw_text(x, y, text, fs=11, color='black', fontfamily='serif', fontweight='normal'):
        ax.text(x, y, text, ha='center', va='center', fontsize=fs, color=color,
                fontfamily=fontfamily, fontweight=fontweight, zorder=2)

    def draw_arrow(x1, y1, x2, y2, color='black', rad=0.0, ls='solid'):
        ax.annotate('', xy=(x2, y2), xytext=(x1, y1),
                    arrowprops=dict(arrowstyle="-|>", color=color, lw=1, ls=ls,
                                    connectionstyle=f"arc3,rad={rad}"))

    # Title - Bold Sans-serif
    ax.text(0.5, 0.98, "Indigenous SDG Mapping - Advanced Flowchart Algorithm",
            ha='center', va='center', fontsize=16, fontweight='bold', fontfamily='sans-serif')

    # Draw Shapes
    draw_ellipse(0.5, 0.94, 0.1, 0.03, 'lightgrey') # Start
    draw_text(0.5, 0.94, "Start")

    draw_rect(0.5, 0.85, 0.40, 0.07, 'lightblue') # Acq
    draw_text(0.5, 0.85, "Data Acquisition\nLoad/Simulate Dataset\n(NGO Reports, Surveys, Traditional Knowledge)")

    draw_rect(0.5, 0.74, 0.35, 0.06, 'palegreen') # Preproc
    draw_text(0.5, 0.74, "Data Preprocessing\n- Text Cleaning & Parsing\n- Language Detection\n- Feature Generation")

    draw_diamond(0.5, 0.63, 0.5, 0.07, 'khaki') # Dia1
    draw_text(0.5, 0.63, "Preprocessing Quality\nInsufficient?")

    draw_rect(0.5, 0.53, 0.22, 0.04, 'khaki') # Split
    draw_text(0.5, 0.53, "Preparation for\nSDG Mapping")

    # 3 Parallel Boxes (Wheat)
    draw_rect(0.25, 0.43, 0.22, 0.04, 'wheat')
    draw_text(0.25, 0.43, "Automated\nSDG Tagging")

    draw_rect(0.5, 0.43, 0.22, 0.04, 'wheat')
    draw_text(0.5, 0.43, "Coherence &\nGap Analysis")

    draw_rect(0.75, 0.43, 0.22, 0.04, 'wheat')
    draw_text(0.75, 0.43, "Solution\nFramework Gen")

    draw_rect(0.5, 0.32, 0.25, 0.04, 'plum') # Eval
    draw_text(0.5, 0.32, "Mapping Evaluation\n(Prevalence, Conflicts, Impact)")

    draw_diamond(0.5, 0.21, 0.5, 0.07, 'khaki') # Dia2
    draw_text(0.5, 0.21, "Mapping Quality\nAcceptable?")

    draw_rect(0.5, 0.11, 0.28, 0.04, 'lightpink') # Out
    draw_text(0.5, 0.11, "Select Best Scenarios\n& Output Policies")

    draw_diamond(0.5, 0.02, 0.5, 0.07, 'khaki') # Dia3
    draw_text(0.5, 0.02, "Policy Relevance\nDegrades?")

    # Draw Arrows
    # Forward paths (Black & Bright Green)
    draw_arrow(0.5, 0.925, 0.5, 0.885) # Start to Acq
    draw_arrow(0.48, 0.815, 0.48, 0.77) # Acq to Preproc
    draw_arrow(0.48, 0.71, 0.48, 0.665) # Preproc to Dia1

    draw_arrow(0.5, 0.595, 0.5, 0.55, color='#00FF00') # Dia1 to Split (No)
    draw_text(0.52, 0.575, "No", color='#00FF00')

    # Split to 3 boxes
    draw_arrow(0.42, 0.51, 0.28, 0.45)
    draw_arrow(0.5, 0.51, 0.5, 0.45)
    draw_arrow(0.58, 0.51, 0.72, 0.45)

    # 3 boxes to Eval
    draw_arrow(0.28, 0.41, 0.45, 0.34)
    draw_arrow(0.5, 0.41, 0.5, 0.34)
    draw_arrow(0.72, 0.41, 0.55, 0.34)

    draw_arrow(0.5, 0.30, 0.5, 0.245) # Eval to Dia2

    draw_arrow(0.5, 0.175, 0.5, 0.13, color='#00FF00') # Dia2 to Out (Yes)
    draw_text(0.52, 0.155, "Yes", color='#00FF00')

    draw_arrow(0.5, 0.09, 0.5, 0.055) # Out to Dia3

    # Feedback paths (Red)
    # Dia1 Yes to Acq
    draw_arrow(0.75, 0.63, 0.70, 0.85, color='red', rad=0.2)
    draw_text(0.72, 0.76, "Yes", color='red')

    # Dia2 No (Retune) to middle models
    draw_arrow(0.65, 0.24, 0.58, 0.41, color='red', rad=0.3)
    draw_text(0.72, 0.28, "No (Retune)", color='red')

    # Dia2 No (Refine Features) to Split
    draw_arrow(0.75, 0.21, 0.61, 0.53, color='red', rad=0.5)
    draw_text(0.85, 0.38, "No (Refine Features)", color='red')

    # Dia3 Yes (Retrain) to Split
    draw_arrow(0.75, 0.02, 0.61, 0.51, color='red', rad=0.6)
    draw_text(0.83, 0.18, "Yes (Retrain)", color='red')

    # Concept loops (Purple dashed)
    # Eval to Split
    draw_arrow(0.38, 0.34, 0.39, 0.51, color='blueviolet', rad=-0.4, ls='dashed')
    draw_text(0.36, 0.42, "Mapping <-> Prep loop", color='black')

    # Eval to Preproc
    draw_arrow(0.62, 0.32, 0.675, 0.73, color='blueviolet', rad=0.5, ls='dashed')
    draw_text(0.74, 0.48, "Preproc <-> Eval loop", color='black')

    plt.tight_layout()
    plt.savefig('output_figures/plot_29.png', bbox_inches='tight', dpi=300)
    plt.show()


create_flowchart_diagram()

# --- Download Logic ---
import shutil
shutil.make_archive('all_figures', 'zip', 'output_figures')
print('All figures have been saved to all_figures.zip')
try:
    from google.colab import files
    files.download('all_figures.zip')
except ImportError:
    print('Not running in Google Colab. You can find all_figures.zip in your current directory.')
