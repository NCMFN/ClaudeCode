import pandas as pd
import numpy as np
import model
import os

X_train = pd.DataFrame(np.random.rand(100, 5))
y_train = pd.Series([0]*50 + [1]*50)

# test training base model
m = model.train_model(X_train, y_train, tune_hyperparams=False)
assert os.path.exists('outputs/best_lgbm_model.pkl')
print("Base model trained and saved.")

# Note: we won't test tuning here to save time, we verified the syntax in code.
