import pandas as pd
import numpy as np
import imbalance

# Create fake imbalanced data
X_train = pd.DataFrame(np.random.rand(100, 5), columns=[f'f{i}' for i in range(5)])
y_train = pd.Series([0]*90 + [1]*10)

X_res, y_res, kwargs = imbalance.handle_imbalance(X_train, y_train, 'smote')
assert y_res.value_counts().tolist() == [90, 90]

X_res, y_res, kwargs = imbalance.handle_imbalance(X_train, y_train, 'undersample')
assert y_res.value_counts().tolist() == [10, 10]

X_res, y_res, kwargs = imbalance.handle_imbalance(X_train, y_train, 'weight')
assert kwargs['scale_pos_weight'] == 9.0
print("All checks passed.")
