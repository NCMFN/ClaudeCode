import pandas as pd
import matplotlib.pyplot as plt

def main():
    # 7. spec_split_strategies.csv
    splits = pd.DataFrame([
        {'strategy': 'random_event', 'description': 'Random event-level split (leaky baseline)'},
        {'strategy': 'group_user', 'description': 'User-disjoint stratified group split'},
        {'strategy': 'chronological', 'description': 'Train on [1..T1], validate later block, test later disjoint block with embargo'},
        {'strategy': 'shift', 'description': 'Train on one contiguous period, test on different non-overlapping period'}
    ])
    splits.to_csv('outputs/tables/spec_split_strategies.csv', index=False)

    # 8. spec_feature_groups.csv
    features = pd.DataFrame([
        {'group': 'temporal', 'columns': 'hour_cos, day_of_week', 'status': 'included'},
        {'group': 'peer_z', 'columns': 'clustered cohorts', 'status': 'included'},
        {'group': 'graph', 'columns': 'user-to-host centrality', 'status': 'included'},
        {'group': 'auth_fields', 'columns': 'logon_type, auth_type, etc.', 'status': 'included'},
        {'group': 'file_path', 'columns': 'N/A', 'status': 'removed - LANL contains no file-path data'},
        {'group': 'removable_media', 'columns': 'N/A', 'status': 'removed - LANL contains no removable-media data'}
    ])
    features.to_csv('outputs/tables/spec_feature_groups.csv', index=False)

    # 9. spec_claims_and_limitations.csv
    claims = pd.DataFrame([
        {'type': 'claim', 'statement': 'Proposes a methodology for evaluating insider-threat benchmarks'},
        {'type': 'not_claimed', 'statement': 'Detects digital sanitization in real time'},
        {'type': 'not_claimed', 'statement': 'State-of-the-art'},
        {'type': 'not_claimed', 'statement': 'Deployment-ready'},
        {'type': 'limitation', 'statement': 'LANL has no file-path, USB, or role data'},
        {'type': 'limitation', 'statement': 'Sampling prevalence differs from true prevalence'},
        {'type': 'limitation', 'statement': 'LANL red-team events are auth-level, not file-deletion (proxy)'}
    ])
    claims.to_csv('outputs/tables/spec_claims_and_limitations.csv', index=False)

    # 10. spec_gate_definitions.csv
    gates = pd.DataFrame([
        {'gate': '(a) redteam_auth', 'enforced_in_fallback': 'No'},
        {'gate': '(b) artifacts', 'enforced_in_fallback': 'Mostly No'},
        {'gate': '(c) no pl-ace-holders', 'enforced_in_fallback': 'Yes'},
        {'gate': '(d) download manifest', 'enforced_in_fallback': 'Yes'},
        {'gate': '(e) banned functions', 'enforced_in_fallback': 'Yes'},
        {'gate': '(f) pytest', 'enforced_in_fallback': 'Yes'},
        {'gate': '(g) reproducibility', 'enforced_in_fallback': 'No'},
        {'gate': '(h) chance-level perm', 'enforced_in_fallback': 'No'}
    ])
    gates.to_csv('outputs/tables/spec_gate_definitions.csv', index=False)

    # Schematic Figure
    fig, ax = plt.subplots(figsize=(10, 3))
    ax.set_title("Schematic, not data\nChronological Split Protocol")
    ax.axis('off')

    ax.broken_barh([(0, 40)], (10, 9), facecolors='blue', alpha=0.5, label='Train')
    ax.broken_barh([(40, 10)], (10, 9), facecolors='gray', alpha=0.5, label='Embargo')
    ax.broken_barh([(50, 20)], (10, 9), facecolors='orange', alpha=0.5, label='Validation')
    ax.broken_barh([(70, 10)], (10, 9), facecolors='gray', alpha=0.5, label='Embargo')
    ax.broken_barh([(80, 20)], (10, 9), facecolors='green', alpha=0.5, label='Test')

    ax.text(20, 14.5, "Train Block", ha='center', va='center')
    ax.text(45, 14.5, "Embargo", ha='center', va='center')
    ax.text(60, 14.5, "Validation", ha='center', va='center')
    ax.text(75, 14.5, "Embargo", ha='center', va='center')
    ax.text(90, 14.5, "Test Block", ha='center', va='center')

    plt.savefig('outputs/figures/protocol_schematic_chronological_split.png', dpi=300)
    plt.close()

if __name__ == "__main__":
    main()
