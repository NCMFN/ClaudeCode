CHRONO_TRAIN_FRAC = 0.6
CHRONO_VAL_FRAC = 0.8
FEATURE_GROUPS = {
    "Temporal": ['hour_sin', 'hour_cos', 'dow_sin', 'dow_cos'],
    "Behavioral": ['peer_z_score'],
    "Graph": ['graph_degree', 'graph_betweenness']
}
HOUR_COS_PERTURBATION = 0.5
EVASION_PERTURBATION_MULTIPLIER = 0.5
RANDOM_SEED = 42
