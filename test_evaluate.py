import pandas as pd
import numpy as np
import evaluate

class DummyModel:
    def predict_proba(self, X):
        return np.array([[0.8, 0.2], [0.1, 0.9], [0.6, 0.4], [0.3, 0.7]])
    def predict(self, X):
        return np.array([0, 1, 0, 1])

model = DummyModel()
X_test = pd.DataFrame(np.random.rand(4, 5))
y_test = pd.Series([0, 1, 1, 1])

evaluate.evaluate_model(model, X_test, y_test, mean_loan_amount=15000)
