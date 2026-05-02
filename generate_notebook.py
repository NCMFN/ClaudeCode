import nbformat as nbf

nb = nbf.v4.new_notebook()

cells = [
    nbf.v4.new_markdown_cell("# Exploratory Data Analysis: NHIS 2022 Data"),
    nbf.v4.new_markdown_cell("This notebook performs basic exploration of the processed CDC NHIS 2022 dataset focusing on young adults aged 20-39 with mental health co-morbidities."),
    nbf.v4.new_code_cell("import pandas as pd\nimport matplotlib.pyplot as plt\nimport seaborn as sns\nimport os\n\ndata_path = '../data/nhis_processed.csv'\ndf = pd.read_csv(data_path)\ndf.head()"),
    nbf.v4.new_markdown_cell("### Basic Statistics"),
    nbf.v4.new_code_cell("df.describe()"),
    nbf.v4.new_markdown_cell("### Target Class Distribution (CVD Risk)"),
    nbf.v4.new_code_cell("sns.countplot(x='label', data=df)\nplt.title('Target Class Distribution')\nplt.show()"),
    nbf.v4.new_markdown_cell("### Mental Health Co-morbidities vs CVD Risk"),
    nbf.v4.new_code_cell("if 'ANXEV_A' in df.columns and 'DEPEV_A' in df.columns:\n    fig, ax = plt.subplots(1, 2, figsize=(12, 5))\n    sns.countplot(x='ANXEV_A', hue='label', data=df, ax=ax[0])\n    ax[0].set_title('Anxiety vs CVD Risk')\n    sns.countplot(x='DEPEV_A', hue='label', data=df, ax=ax[1])\n    ax[1].set_title('Depression vs CVD Risk')\n    plt.show()")
]

nb['cells'] = cells

with open('heart_mind_cvd/notebooks/exploration.ipynb', 'w') as f:
    nbf.write(nb, f)
print("Notebook generated.")
