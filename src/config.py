# Central Configuration
RANDOM_SEED = 42
DATA_PATH = "redteam.txt.gz"
CHRONO_TRAIN_FRAC = 0.6
CHRONO_VAL_FRAC = 0.2
CHRONO_TEST_FRAC = 0.2
GROUP_TRAIN_FRAC = 0.8
GROUP_VAL_FRAC = 0.75
RANDOM_TRAIN_FRAC = 0.8
RANDOM_VAL_FRAC = 0.25
SHIFT_TRAIN_FRAC = 0.3
SHIFT_VAL_FRAC = 0.5
SHIFT_TEST_FRAC = 0.8
EVASION_PEER_Z_MULTIPLIER = 1.5
EVASION_GRAPH_DEGREE_MULTIPLIER = 1.2
POISON_FRACTION = 0.05
N_MALICIOUS_OBS = 148
N_BENIGN_OBS = 4229

FEATURE_GROUPS = {
    'A_temporal': ['hour_cos', 'hour_sin', 'day_of_week'],
    'B_behavioral': ['event_count'],
    'C_graph_peer': ['graph_degree', 'graph_betweenness', 'peer_z_score'],
}
FEATURE_GROUPS['D_all'] = FEATURE_GROUPS['A_temporal'] + FEATURE_GROUPS['B_behavioral'] + FEATURE_GROUPS['C_graph_peer']
STYLE = {'primary': '#2E5EAA', 'secondary': '#D9534F'}
