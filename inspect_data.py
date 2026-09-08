import pandas as pd

try:
    df1 = pd.read_csv('wsn_data1/WSN_Dataset.csv')
    print("WSN_Dataset.csv")
    print(df1.head())
    print(df1.columns)
    print(df1.shape)
except Exception as e: print(e)

try:
    df2 = pd.read_csv('wsn_data2/WSN-DS.csv')
    print("\nWSN-DS.csv")
    print(df2.head())
    print(df2.columns)
    print(df2.shape)
except Exception as e: print(e)

try:
    df3 = pd.read_csv('wsn_data3/WSN_Localization_Dataset.csv')
    print("\nWSN_Localization_Dataset.csv")
    print(df3.head())
    print(df3.columns)
    print(df3.shape)
except Exception as e: print(e)
