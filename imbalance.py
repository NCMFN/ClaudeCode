import pandas as pd
import logging
from imblearn.over_sampling import SMOTE
from imblearn.under_sampling import RandomUnderSampler
from imblearn.pipeline import Pipeline  # useful context reminder: pipeline oversampling applied later if doing full cv, but here we explicitly resample before LightGBM training.

logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')

def handle_imbalance(X_train, y_train, strategy='smote'):
    """
    Handles class imbalance using specified strategy.

    Args:
        X_train: Training features.
        y_train: Training labels.
        strategy: 'smote', 'undersample', or 'weight'.

    Returns:
        X_resampled, y_resampled (if strategy modifies data)
        or dict of scale_pos_weight if 'weight'
    """

    logging.info(f"Class distribution BEFORE {strategy}:")
    counts_before = pd.Series(y_train).value_counts()
    logging.info(f"\n{counts_before}")

    # ensure dataframe to return same type
    is_df = isinstance(X_train, pd.DataFrame)
    columns = X_train.columns if is_df else None

    kwargs = {}

    if strategy == 'smote':
        smote = SMOTE(k_neighbors=5, random_state=42)
        X_resampled, y_resampled = smote.fit_resample(X_train, y_train)
    elif strategy == 'undersample':
        rus = RandomUnderSampler(random_state=42)
        X_resampled, y_resampled = rus.fit_resample(X_train, y_train)
    elif strategy == 'weight':
        # Don't resample data, return weights calculation
        count_neg = counts_before.get(0, 0)
        count_pos = counts_before.get(1, 1)
        scale_pos_weight = count_neg / count_pos
        kwargs['scale_pos_weight'] = scale_pos_weight
        X_resampled, y_resampled = X_train, y_train
        logging.info(f"Calculated scale_pos_weight: {scale_pos_weight:.2f}")
    else:
        raise ValueError(f"Unknown strategy {strategy}. Use 'smote', 'undersample', or 'weight'.")

    logging.info(f"Class distribution AFTER {strategy}:")
    counts_after = pd.Series(y_resampled).value_counts()
    logging.info(f"\n{counts_after}")

    if is_df and not isinstance(X_resampled, pd.DataFrame):
        X_resampled = pd.DataFrame(X_resampled, columns=columns)

    return X_resampled, y_resampled, kwargs
