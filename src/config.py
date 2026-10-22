class PipelineConfig:
    SEED = 42
    CHRONO_TRAIN_END = 0.6
    CHRONO_VAL_END = 0.8
    N_SPLITS = 5
    TEST_SIZE = 0.2
    FEATURES_TEMPORAL = ['hour_cos', 'day_of_week']
    FEATURES_BEHAVIORAL = ['auth_type_encoded', 'logon_type_encoded']
    FEATURES_GRAPH = ['graph_degree', 'graph_betweenness', 'peer_z_score']
    FEATURE_VARIANTS = {
        'A': FEATURES_TEMPORAL,
        'B': FEATURES_BEHAVIORAL,
        'C': FEATURES_GRAPH,
        'D': FEATURES_TEMPORAL + FEATURES_BEHAVIORAL + FEATURES_GRAPH
    }
    TARGET_COL = 'is_malicious'
    ADV_HOUR_COS_MAGNITUDE = 0.5
    ADV_POISONING_RATE = 0.05
    TARGET_MALICIOUS_COUNT = 148
    TARGET_BENIGN_COUNT = 4229
    DIR_FIGURES = 'outputs/figures'
    DIR_TABLES = 'outputs/tables'
    DIR_DATASETS = 'outputs/datasets'
    DIR_PAPER_ASSETS = 'outputs/paper_assets'
    STYLE = {'primary': '#2E5EAA', 'secondary': '#D9534F'}
