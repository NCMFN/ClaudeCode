import os
import numpy as np
import pandas as pd
import time
from sklearn.ensemble import IsolationForest
from sklearn.svm import OneClassSVM
from sklearn.metrics import precision_score, recall_score, f1_score, roc_auc_score, confusion_matrix, roc_curve, precision_recall_curve
from tensorflow.keras.models import Model, Sequential
from tensorflow.keras.layers import Input, Dense, LSTM, RepeatVector, TimeDistributed, Conv1D, MaxPooling1D, UpSampling1D, Flatten, Reshape, Bidirectional
from tensorflow.keras.callbacks import EarlyStopping
import matplotlib.pyplot as plt
import seaborn as sns
from models_attention import Attention

import warnings
warnings.filterwarnings('ignore')
np.random.seed(42)

# Set matplotlib parameters for standardization as per memory
plt.rcParams.update({
    'font.size': 11, 'axes.titlesize': 13, 'axes.labelsize': 11,
    'xtick.labelsize': 10, 'ytick.labelsize': 10, 'figure.dpi': 300, 'savefig.dpi': 300
})

DATASETS = ["NSL-KDD", "HAI", "UNSW-NB15", "CICIDS2017", "CICIoT2023", "SWaT", "WADI", "BATADAL"]

TIME_SERIES_DATASETS = ["NSL-KDD", "HAI", "SWaT", "WADI", "BATADAL"]

def load_data(dataset):
    X_train = np.load(f"data/processed/{dataset}/X_train.npy")
    y_train = np.load(f"data/processed/{dataset}/y_train.npy")
    X_test = np.load(f"data/processed/{dataset}/X_test.npy")
    y_test = np.load(f"data/processed/{dataset}/y_test.npy")
    return X_train, y_train, X_test, y_test

def evaluate_predictions(y_true, y_pred_prob, threshold=0.5):
    y_pred = (y_pred_prob > threshold).astype(int)
    # Check if we only have one class in test (could happen with fallback data)
    if len(np.unique(y_true)) <= 1:
        auc = 0.5
    else:
        auc = roc_auc_score(y_true, y_pred_prob)

    return {
        'precision': precision_score(y_true, y_pred, zero_division=0),
        'recall': recall_score(y_true, y_pred, zero_division=0),
        'f1': f1_score(y_true, y_pred, zero_division=0),
        'roc_auc': auc
    }

def run_isolation_forest(X_train, X_test, y_test):
    print("Running Isolation Forest...")
    start_time = time.time()

    clf = IsolationForest(contamination=0.1, random_state=42, n_jobs=-1)
    if len(X_train) == 0:
        return {'precision': 0, 'recall': 0, 'f1': 0, 'roc_auc': 0, 'inference_latency_ms': 0}, np.zeros(len(y_test))
    clf.fit(X_train)

    inference_start = time.time()
    scores = clf.decision_function(X_test) if len(X_test) > 0 else np.zeros(0)
    inference_time = (time.time() - inference_start) / max(len(X_test), 1) * 1000 # ms per sample

    y_pred_prob = -scores
    metrics = evaluate_predictions(y_test, y_pred_prob, threshold=0) if len(y_test) > 0 else {'precision': 0, 'recall': 0, 'f1': 0, 'roc_auc': 0}
    metrics['inference_latency_ms'] = inference_time

    return metrics, y_pred_prob

def run_ocsvm(X_train, X_test, y_test):
    print("Running One-Class SVM...")
    start_time = time.time()

    clf = OneClassSVM(nu=0.1, gamma='scale')
    if len(X_train) == 0:
        return {'precision': 0, 'recall': 0, 'f1': 0, 'roc_auc': 0, 'inference_latency_ms': 0}, np.zeros(len(y_test))
    clf.fit(X_train[:min(10000, len(X_train))])

    inference_start = time.time()
    scores = clf.decision_function(X_test) if len(X_test) > 0 else np.zeros(0)
    inference_time = (time.time() - inference_start) / max(len(X_test), 1) * 1000

    y_pred_prob = -scores
    metrics = evaluate_predictions(y_test, y_pred_prob, threshold=0) if len(y_test) > 0 else {'precision': 0, 'recall': 0, 'f1': 0, 'roc_auc': 0}
    metrics['inference_latency_ms'] = inference_time

    return metrics, y_pred_prob

def run_autoencoder(X_train, X_test, y_test):
    print("Running Autoencoder...")
    if len(X_train) == 0 or len(X_test) == 0:
        return {'precision': 0, 'recall': 0, 'f1': 0, 'roc_auc': 0, 'inference_latency_ms': 0}, np.zeros(len(y_test))
    input_dim = X_train.shape[1]

    input_layer = Input(shape=(input_dim,))
    encoded = Dense(int(input_dim/2), activation="relu")(input_layer)
    encoded = Dense(int(input_dim/4), activation="relu")(encoded)
    decoded = Dense(int(input_dim/2), activation="relu")(encoded)
    decoded = Dense(input_dim, activation="linear")(decoded)

    autoencoder = Model(inputs=input_layer, outputs=decoded)
    autoencoder.compile(optimizer='adam', loss='mse')

    autoencoder.fit(X_train, X_train, epochs=10, batch_size=64, validation_split=0.1,
                    callbacks=[EarlyStopping(patience=3)], verbose=0)

    inference_start = time.time()
    predictions = autoencoder.predict(X_test, verbose=0)
    inference_time = (time.time() - inference_start) / len(X_test) * 1000

    mse = np.mean(np.power(X_test - predictions, 2), axis=1)

    train_preds = autoencoder.predict(X_train, verbose=0)
    train_mse = np.mean(np.power(X_train - train_preds, 2), axis=1)
    threshold = np.mean(train_mse) + 3*np.std(train_mse)

    metrics = evaluate_predictions(y_test, mse, threshold=threshold)
    metrics['inference_latency_ms'] = inference_time

    return metrics, mse

def create_sequences(X, y, time_steps=10):
    if len(X) <= time_steps:
        return np.array([]), np.array([])
    Xs, ys = [], []
    for i in range(len(X) - time_steps):
        Xs.append(X[i:(i + time_steps)])
        ys.append(y[i + time_steps])
    return np.array(Xs), np.array(ys)

def run_lstm_autoencoder(X_train, X_test, y_test):
    print("Running LSTM Autoencoder...")
    time_steps = 10

    X_train_seq, _ = create_sequences(X_train[:min(10000, len(X_train))], np.zeros(min(10000, len(X_train))), time_steps)
    X_test_seq, y_test_seq = create_sequences(X_test, y_test, time_steps)

    if len(X_train_seq) == 0 or len(X_test_seq) == 0:
        return {'precision': 0, 'recall': 0, 'f1': 0, 'roc_auc': 0, 'inference_latency_ms': 0}, np.zeros(len(y_test))

    n_features = X_train_seq.shape[2]

    model = Sequential([
        LSTM(32, activation='relu', input_shape=(time_steps, n_features), return_sequences=True),
        LSTM(16, activation='relu', return_sequences=False),
        RepeatVector(time_steps),
        LSTM(16, activation='relu', return_sequences=True),
        LSTM(32, activation='relu', return_sequences=True),
        TimeDistributed(Dense(n_features))
    ])

    model.compile(optimizer='adam', loss='mse')
    model.fit(X_train_seq, X_train_seq, epochs=5, batch_size=64, validation_split=0.1,
              callbacks=[EarlyStopping(patience=2)], verbose=0)

    inference_start = time.time()
    predictions = model.predict(X_test_seq, verbose=0)
    inference_time = (time.time() - inference_start) / len(X_test_seq) * 1000

    mse = np.mean(np.power(X_test_seq - predictions, 2), axis=(1, 2))

    train_preds = model.predict(X_train_seq, verbose=0)
    train_mse = np.mean(np.power(X_train_seq - train_preds, 2), axis=(1, 2))
    threshold = np.mean(train_mse) + 3*np.std(train_mse)

    metrics = evaluate_predictions(y_test_seq, mse, threshold=threshold)
    metrics['inference_latency_ms'] = inference_time

    full_mse = np.zeros(len(y_test))
    full_mse[time_steps:] = mse

    return metrics, full_mse

def run_proposed_cnn_bilstm_attention(X_train, X_test, y_test, dataset_name):
    print("Running Proposed CNN-BiLSTM with Attention...")
    time_steps = 10

    X_train_seq, y_train_seq = create_sequences(X_train[:min(10000, len(X_train))], np.zeros(min(10000, len(X_train))), time_steps)
    X_test_seq, y_test_seq = create_sequences(X_test, y_test, time_steps)

    if len(X_train_seq) == 0 or len(X_test_seq) == 0:
        return {'precision': 0, 'recall': 0, 'f1': 0, 'roc_auc': 0, 'inference_latency_ms': 0}, np.zeros(len(y_test))

    n_features = X_train_seq.shape[2]

    input_layer = Input(shape=(time_steps, n_features))

    x = Conv1D(filters=32, kernel_size=3, padding='same', activation='relu')(input_layer)
    x = Bidirectional(LSTM(16, return_sequences=True))(x)
    x = Attention(return_sequences=True)(x)
    x = Bidirectional(LSTM(16, return_sequences=True))(x)
    decoded = TimeDistributed(Dense(n_features))(x)

    model = Model(inputs=input_layer, outputs=decoded)
    model.compile(optimizer='adam', loss='mse')

    history = model.fit(X_train_seq, X_train_seq, epochs=5, batch_size=64, validation_split=0.1, verbose=0)

    # Save training curves here for the proposed model
    plt.figure(figsize=(6, 5))
    plt.plot(history.history['loss'], label='Train Loss')
    plt.plot(history.history['val_loss'], label='Val Loss')
    plt.title(f'Training Loss Curve (CNN-BiLSTM-Attn on {dataset_name})')
    plt.xlabel('Epoch')
    plt.ylabel('MSE Loss')
    plt.legend()
    plt.grid(True)
    plt.tight_layout()
    plt.savefig(f'results/figures/training_loss_curve_{dataset_name}.png')
    plt.close()

    inference_start = time.time()
    predictions = model.predict(X_test_seq, verbose=0)
    inference_time = (time.time() - inference_start) / len(X_test_seq) * 1000

    mse = np.mean(np.power(X_test_seq - predictions, 2), axis=(1, 2))

    train_preds = model.predict(X_train_seq, verbose=0)
    train_mse = np.mean(np.power(X_train_seq - train_preds, 2), axis=(1, 2))
    threshold = np.mean(train_mse) + 3*np.std(train_mse)

    metrics = evaluate_predictions(y_test_seq, mse, threshold=threshold)
    metrics['inference_latency_ms'] = inference_time

    # Generate real Confusion Matrix and PR Curve
    if len(np.unique(y_test_seq)) > 1:
        y_pred = (mse > threshold).astype(int)
        cm = confusion_matrix(y_test_seq, y_pred)
        plt.figure(figsize=(6, 5))
        sns.heatmap(cm, annot=True, fmt='d', cmap='Blues')
        plt.title(f'Confusion Matrix (CNN-BiLSTM-Attn on {dataset_name})')
        plt.xlabel('Predicted Label')
        plt.ylabel('True Label')
        plt.tight_layout()
        plt.savefig(f'results/figures/confusion_matrix_{dataset_name}_CNN_BiLSTM_Attn.png')
        plt.close()

        precision, recall, _ = precision_recall_curve(y_test_seq, mse)
        plt.figure(figsize=(6, 5))
        plt.plot(recall, precision, marker='.')
        plt.title(f'Precision-Recall Curve (CNN-BiLSTM-Attn on {dataset_name})')
        plt.xlabel('Recall')
        plt.ylabel('Precision')
        plt.grid(True)
        plt.tight_layout()
        plt.savefig(f'results/figures/pr_curve_{dataset_name}_CNN_BiLSTM_Attn.png')
        plt.close()

    full_mse = np.zeros(len(y_test))
    full_mse[time_steps:] = mse
    return metrics, full_mse

results = []

for ds in DATASETS:
    print(f"\nEvaluating dataset: {ds}")
    try:
        X_train, y_train, X_test, y_test = load_data(ds)


        models = {}

        metrics_if, pred_if = run_isolation_forest(X_train, X_test, y_test)
        models['IF'] = metrics_if

        metrics_ocsvm, pred_ocsvm = run_ocsvm(X_train, X_test, y_test)
        models['OCSVM'] = metrics_ocsvm

        metrics_ae, pred_ae = run_autoencoder(X_train, X_test, y_test)
        models['AE'] = metrics_ae

        if ds in TIME_SERIES_DATASETS:
            metrics_lstm, pred_lstm = run_lstm_autoencoder(X_train, X_test, y_test)
            models['LSTM-AE'] = metrics_lstm

            metrics_prop, pred_prop = run_proposed_cnn_bilstm_attention(X_train, X_test, y_test, ds)
            models['CNN-BiLSTM-Attn'] = metrics_prop

        for model_name, metrics in models.items():
            results.append({
                'Dataset': ds,
                'Model': model_name,
                'F1': metrics['f1'],
                'Precision': metrics['precision'],
                'Recall': metrics['recall'],
                'ROC_AUC': metrics['roc_auc'],
                'Latency_ms': metrics['inference_latency_ms']
            })

    except Exception as e:
        print(f"Error evaluating {ds}: {e}")

df_results = pd.DataFrame(results)
os.makedirs("results/metrics", exist_ok=True)
df_results.to_csv("results/metrics/all_results.csv", index=False)
print("\nEvaluation complete. Results saved.")
