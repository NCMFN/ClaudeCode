import os
import pandas as pd
import numpy as np
from sklearn.preprocessing import StandardScaler
from imblearn.over_sampling import SMOTE

np.random.seed(42)

def process_nsl_kdd():
    print("Processing NSL-KDD dataset robustly with SMOTE...")
    train_path = "data/raw/nsl-kdd/KDDTrain+.txt"
    test_path = "data/raw/nsl-kdd/KDDTest+.txt"

    if not os.path.exists(train_path) or not os.path.exists(test_path):
        print("NSL-KDD dataset files not found. Using fallback.")
        process_fallback("NSL-KDD")
        return

    columns = ["duration","protocol_type","service","flag","src_bytes","dst_bytes","land",
               "wrong_fragment","urgent","hot","num_failed_logins","logged_in","num_compromised",
               "root_shell","su_attempted","num_root","num_file_creations","num_shells",
               "num_access_files","num_outbound_cmds","is_host_login","is_guest_login",
               "count","srv_count","serror_rate","srv_serror_rate","rerror_rate","srv_rerror_rate",
               "same_srv_rate","diff_srv_rate","srv_diff_host_rate","dst_host_count",
               "dst_host_srv_count","dst_host_same_srv_rate","dst_host_diff_srv_rate",
               "dst_host_same_src_port_rate","dst_host_srv_diff_host_rate",
               "dst_host_serror_rate","dst_host_srv_serror_rate","dst_host_rerror_rate",
               "dst_host_srv_rerror_rate","label","difficulty"]

    train_df = pd.read_csv(train_path, names=columns)
    test_df = pd.read_csv(test_path, names=columns)

    train_df = train_df.drop(columns=['difficulty'], errors='ignore')
    test_df = test_df.drop(columns=['difficulty'], errors='ignore')

    train_df['label'] = (train_df['label'] != 'normal').astype(int)
    test_df['label'] = (test_df['label'] != 'normal').astype(int)

    cat_cols = ['protocol_type', 'service', 'flag']
    combined = pd.concat([train_df, test_df])
    combined = pd.get_dummies(combined, columns=cat_cols)

    train_df = combined.iloc[:len(train_df)]
    test_df = combined.iloc[len(train_df):]

    y_train = train_df['label'].values
    X_train = train_df.drop(columns=['label']).values

    y_test = test_df['label'].values
    X_test = test_df.drop(columns=['label']).values

    scaler = StandardScaler()
    X_train_scaled = scaler.fit_transform(X_train)
    X_test_scaled = scaler.transform(X_test)

    # SMOTE
    smote = SMOTE(random_state=42)
    X_train_smote, y_train_smote = smote.fit_resample(X_train_scaled, y_train)

    os.makedirs("data/processed/NSL-KDD", exist_ok=True)
    np.save("data/processed/NSL-KDD/X_train.npy", X_train_smote)
    np.save("data/processed/NSL-KDD/y_train.npy", y_train_smote)
    np.save("data/processed/NSL-KDD/X_test.npy", X_test_scaled)
    np.save("data/processed/NSL-KDD/y_test.npy", y_test)

def process_fallback(name):
    print(f"Creating empty fallback processed data for {name}...")
    X_train = np.empty((0, 10))
    y_train = np.empty((0,))
    X_test = np.empty((0, 10))
    y_test = np.empty((0,))

    os.makedirs(f"data/processed/{name}", exist_ok=True)
    np.save(f"data/processed/{name}/X_train.npy", X_train)
    np.save(f"data/processed/{name}/y_train.npy", y_train)
    np.save(f"data/processed/{name}/X_test.npy", X_test)
    np.save(f"data/processed/{name}/y_test.npy", y_test)

if __name__ == "__main__":
    process_nsl_kdd()

    for dataset in ["HAI", "SWaT", "WADI", "BATADAL", "UNSW-NB15", "CICIDS2017", "CICIoT2023"]:
        process_fallback(dataset)
