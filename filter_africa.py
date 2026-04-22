import pandas as pd

df = pd.read_csv('data/data/gfd_qcdatabase_2019_08_01.csv')
print(df.columns)
print(df.shape)
print(df.dtypes)
print(df.describe())
