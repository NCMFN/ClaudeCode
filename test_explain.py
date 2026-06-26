import pandas as pd
import numpy as np
import explain
import lightgbm as lgb
import os

X_train = pd.DataFrame(np.random.rand(100, 5), columns=[f'f{i}' for i in range(5)])
y_train = pd.Series([0]*50 + [1]*50)

model = lgb.LGBMClassifier(n_estimators=10)
model.fit(X_train, y_train)

explain.explain_model(model, X_train)
assert os.path.exists('outputs/shap_summary_beeswarm.png')
print("Explainability test passed.")
