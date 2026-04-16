import numpy as np
import pandas as pd
import os
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler, OneHotEncoder
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from sklearn.impute import SimpleImputer
import tensorflow as tf
from tensorflow.keras import layers, models, Model

np.random.seed(42)
tf.random.set_seed(42)

df = pd.read_csv('../data/integrated_phytoremediation_dataset.csv')

features_X1_num = ['root_depth_cm', 'growth_rate_cm_day', 'leaf_area_index', 'geo_pca_1', 'geo_pca_2']
features_X1_cat = ['species_name']
features_X2_num = ['soil_ph', 'soil_cec_cmol_kg', 'clay_percent']
features_X2_cat = []
features_X3_num = ['molecular_weight', 'solubility_mg_l']
features_X3_cat = ['contaminant_id', 'toxicity_class']
features_X4_num = ['temp_annual_c', 'precip_annual_mm']
features_X4_cat = []

all_num_features = features_X1_num + features_X2_num + features_X3_num + features_X4_num
all_cat_features = features_X1_cat + features_X2_cat + features_X3_cat + features_X4_cat

targets_reg = ['BCF', 'TF', 'Remediation_Efficiency_Pct']
target_clf = 'Affinity_Class'

X = df[all_num_features + all_cat_features]
y_reg = df[targets_reg]
y_clf = df[target_clf]

X_train, X_test, y_reg_train, y_reg_test, y_clf_train, y_clf_test = train_test_split(
    X, y_reg, y_clf, test_size=0.2, random_state=42, stratify=y_clf
)

def create_branch_preprocessor(num_cols, cat_cols):
    transformers = []
    if num_cols:
        transformers.append(('num', Pipeline([('imputer', SimpleImputer(strategy='median')), ('scaler', StandardScaler())]), num_cols))
    if cat_cols:
        transformers.append(('cat', Pipeline([('imputer', SimpleImputer(strategy='most_frequent')), ('encoder', OneHotEncoder(handle_unknown='ignore', sparse_output=False))]), cat_cols))
    return ColumnTransformer(transformers)

prep_x1 = create_branch_preprocessor(features_X1_num, features_X1_cat)
prep_x2 = create_branch_preprocessor(features_X2_num, features_X2_cat)
prep_x3 = create_branch_preprocessor(features_X3_num, features_X3_cat)
prep_x4 = create_branch_preprocessor(features_X4_num, features_X4_cat)

X1_train = prep_x1.fit_transform(X_train)
X2_train = prep_x2.fit_transform(X_train)
X3_train = prep_x3.fit_transform(X_train)
X4_train = prep_x4.fit_transform(X_train)

X1_test = prep_x1.transform(X_test)
X2_test = prep_x2.transform(X_test)
X3_test = prep_x3.transform(X_test)
X4_test = prep_x4.transform(X_test)

input_x1 = layers.Input(shape=(X1_train.shape[1],), name='Plant_Traits_Input')
input_x2 = layers.Input(shape=(X2_train.shape[1],), name='Soil_Features_Input')
input_x3 = layers.Input(shape=(X3_train.shape[1],), name='Contaminant_Input')
input_x4 = layers.Input(shape=(X4_train.shape[1],), name='Climate_Input')

dense_x1 = layers.Dense(32, activation='relu')(input_x1)
dense_x1 = layers.Dropout(0.2)(dense_x1)
dense_x2 = layers.Dense(16, activation='relu')(input_x2)
dense_x3 = layers.Dense(16, activation='relu')(input_x3)
dense_x4 = layers.Dense(16, activation='relu')(input_x4)

concat = layers.Concatenate(name='Fusion_Layer')([dense_x1, dense_x2, dense_x3, dense_x4])
shared_dense = layers.Dense(64, activation='relu')(concat)
shared_dense = layers.Dropout(0.3)(shared_dense)
shared_dense = layers.Dense(32, activation='relu')(shared_dense)

out_reg = layers.Dense(3, activation='linear', name='Regression_Head')(shared_dense)
out_clf = layers.Dense(1, activation='sigmoid', name='Classification_Head')(shared_dense)

model = Model(inputs=[input_x1, input_x2, input_x3, input_x4], outputs=[out_reg, out_clf])

model.compile(
    optimizer=tf.keras.optimizers.Adam(learning_rate=0.001),
    loss={
        'Regression_Head': 'mse',
        'Classification_Head': 'binary_crossentropy'
    },
    metrics={
        'Regression_Head': [tf.keras.metrics.RootMeanSquaredError(name='rmse')],
        'Classification_Head': ['accuracy', tf.keras.metrics.AUC(name='auc')]
    },
    loss_weights={'Regression_Head': 1.0, 'Classification_Head': 2.0}
)

early_stopping = tf.keras.callbacks.EarlyStopping(monitor='val_loss', patience=15, restore_best_weights=True)

model.fit(
    {'Plant_Traits_Input': X1_train, 'Soil_Features_Input': X2_train, 'Contaminant_Input': X3_train, 'Climate_Input': X4_train},
    [y_reg_train.to_numpy(), y_clf_train.to_numpy()],
    validation_split=0.2,
    epochs=100,
    batch_size=32,
    callbacks=[early_stopping],
    verbose=1
)

model.save('../models/phytoremediation_multimodal_script.h5')
print("Model saved to ../models/phytoremediation_multimodal_script.h5")
