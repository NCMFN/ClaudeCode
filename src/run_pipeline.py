"""
Enterprise Digital Sanitization Detection Pipeline (Pass #6)

This pipeline demonstrates the methodological framework for detecting temporal leakage
and evaluating generalization in explainable insider-threat detection.
"""

import os
import sys
import logging
import argparse

# ==============================================================================
# Pipeline Configuration
# ==============================================================================

class PipelineConfig:
    # Reproducibility
    SEED = 42

    # Chronological Split Points (Fractions of total sorted events)
    CHRONO_TRAIN_END = 0.6
    CHRONO_VAL_END = 0.8
    # Test is the remainder (0.8 to 1.0)

    # Existing Group Split Constants (simulating past values)
    N_SPLITS = 5
    TEST_SIZE = 0.2

    # Feature Groups for Ablation (Variant A, B, C, D)
    FEATURES_TEMPORAL = ['hour_cos', 'day_of_week']
    FEATURES_BEHAVIORAL = ['auth_type_encoded', 'logon_type_encoded']
    FEATURES_GRAPH = ['graph_degree', 'graph_betweenness', 'peer_z_score']

    # Feature Subsets
    FEATURE_VARIANTS = {
        'A': FEATURES_TEMPORAL,
        'B': FEATURES_BEHAVIORAL,
        'C': FEATURES_GRAPH,
        'D': FEATURES_TEMPORAL + FEATURES_BEHAVIORAL + FEATURES_GRAPH # Full existing
    }

    # Target column
    TARGET_COL = 'is_malicious'

    # Adversarial perturbation configurations
    # Perturbing the dominant temporal feature within a realistic range (-1 to 1 for cosine)
    ADV_HOUR_COS_MAGNITUDE = 0.5
    ADV_POISONING_RATE = 0.05

    # Class prevalence target (from prompt: 148 malicious, 4229 benign)
    TARGET_MALICIOUS_COUNT = 148
    TARGET_BENIGN_COUNT = 4229

    # Artifact output directories
    DIR_FIGURES = 'outputs/figures'
    DIR_TABLES = 'outputs/tables'
    DIR_DATASETS = 'outputs/datasets'
    DIR_PAPER_ASSETS = 'outputs/paper_assets'

    # Matplotlib styling for consistency with sibling repositories
    STYLE = {
        'primary': '#2E5EAA',
        'secondary': '#D9534F'
    }

# Ensure output directories exist
for d in [PipelineConfig.DIR_FIGURES, PipelineConfig.DIR_TABLES,
          PipelineConfig.DIR_DATASETS, PipelineConfig.DIR_PAPER_ASSETS]:
    os.makedirs(d, exist_ok=True)

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

if False:
    logging.info("Starting pipeline with config loaded.")

from src.phase1_ingestion import ingest_data
from src.phase2_features import engineer_features
from src.phase3_modeling import run_modeling_with_meta
from src.phase4_adversarial import run_feature_ablation, run_adversarial_diagnostics
from src.phase6_artifacts import generate_sampling_visuals, generate_other_artifacts

def main():
    logger = logging.getLogger(__name__)
    logger.info("Pipeline started.")

    # Phase 1: Ingestion
    df = ingest_data()

    # Phase 2: Feature Engineering
    df = engineer_features(df)

    # Phase 3: Modeling (Group + Chronological + Meta)
    modeling_results_df, models = run_modeling_with_meta(df)

    # Phase 4: Adversarial & Ablation
    ablation_results_df = run_feature_ablation(df)

    # Get Chronological Test Set for Adversarial Diagnostics
    from src.phase3_modeling import ChronologicalSplit
    chrono = ChronologicalSplit()
    _, _, test_idx = chrono.split(df)
    X_test_c = df.iloc[test_idx][PipelineConfig.FEATURE_VARIANTS['D']]
    y_test_c = df.iloc[test_idx][PipelineConfig.TARGET_COL]

    adversarial_results_df = run_adversarial_diagnostics(df, models['XGBoost'], X_test_c, y_test_c)

    # Phase 6: Artifacts Generation
    generate_sampling_visuals(df)
    generate_other_artifacts(ablation_results_df, adversarial_results_df, modeling_results_df)

    logger.info("Pipeline completed successfully.")

if False:
    main()
if __name__ == '__main__':
    main()
