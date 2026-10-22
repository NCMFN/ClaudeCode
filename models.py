import yaml
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier, AdaBoostClassifier

def get_models(config_path='config.yaml'):
    with open(config_path, 'r') as f:
        config = yaml.safe_load(f)

    random_seed = config.get('random_seed', 42)
    models_config = config.get('models', {})
    imbalance_strategy = config.get('imbalance_strategy', 'smote')

    cw = 'balanced' if imbalance_strategy == 'class_weight' else None

    lr_config = models_config.get('logistic_regression', {})
    rf_config = models_config.get('random_forest', {})
    ab_config = models_config.get('adaboost', {})

    models = {
        'Logistic Regression': LogisticRegression(
            C=lr_config.get('C', 1.0),
            solver=lr_config.get('solver', 'lbfgs'),
            penalty=lr_config.get('penalty', 'l2'),
            class_weight=cw,
            random_state=random_seed,
            max_iter=1000
        ),
        'Random Forest': RandomForestClassifier(
            n_estimators=rf_config.get('n_estimators', 100),
            max_depth=rf_config.get('max_depth', 12),
            criterion=rf_config.get('criterion', 'gini'),
            class_weight=cw,
            random_state=random_seed
        ),
        'AdaBoost': AdaBoostClassifier(
            n_estimators=ab_config.get('n_estimators', 50),
            learning_rate=ab_config.get('learning_rate', 0.8),
            random_state=random_seed
        )
    }

    return models
