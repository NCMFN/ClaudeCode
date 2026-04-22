import pandas as pd
import numpy as np
from biom import load_table
from sklearn.decomposition import PCA
import warnings
warnings.filterwarnings('ignore')

def engineered_features():
    print("Loading EMP mapping file...")
    df_map = pd.read_csv('emp_qiime_mapping_qc_filtered_20170912.tsv', sep='\t', low_memory=False, index_col=0)

    # Filter for soil
    soil_map = df_map[df_map['empo_3'].str.contains('Soil', na=False, case=False)]

    # Parse Real Targets
    for c in ['nitrate_umol_per_l', 'ammonium_umol_per_l', 'ph']:
        soil_map[c] = pd.to_numeric(soil_map[c], errors='coerce')

    soil_map['total_nitrogen'] = soil_map['nitrate_umol_per_l'].fillna(0) + soil_map['ammonium_umol_per_l'].fillna(0)

    # STRICTLY KEEP ONLY SAMPLES WITH ACTUAL NITROGEN DATA
    soil_map = soil_map[soil_map['total_nitrogen'] > 0]
    print(f"Total soil samples with real Nitrogen Target found: {len(soil_map)}")

    print("Loading BIOM table...")
    table = load_table('emp_deblur_150bp.release1.biom')
    common_samples = list(set(soil_map.index) & set(table.ids(axis='sample')))
    soil_map = soil_map.loc[common_samples]
    print(f"Intersection of samples with real nitrogen data in BIOM: {len(common_samples)}")

    print("Extracting counts...")
    otu_counts = []
    for sample_id in common_samples:
        otu_counts.append(table.data(sample_id, dense=True))

    # Resolve Taxonomy dictionary
    otu_taxonomy = {}
    for obs_id, obs_meta, _ in table.iter(axis='observation'):
        tax = ['Unknown']*7
        if isinstance(obs_meta, dict) and 'taxonomy' in obs_meta:
             tax = obs_meta['taxonomy']
        elif isinstance(obs_meta, list) or isinstance(obs_meta, tuple):
             tax = obs_meta
        clean_tax = [t.strip() for t in tax[:6] if isinstance(t, str) and t.strip() not in ('', '__')]
        otu_taxonomy[str(obs_id)] = '; '.join(clean_tax) if clean_tax else str(obs_id)

    # Convert to dataframe
    otu_df = pd.DataFrame(np.array(otu_counts), index=common_samples, columns=table.ids(axis='observation'))

    # Apply taxonomy to columns
    otu_df.rename(columns={str(col): otu_taxonomy.get(str(col), str(col)) for col in otu_df.columns}, inplace=True)

    # Compute relative abundance
    otu_rel = otu_df.div(otu_df.sum(axis=1).replace(0, 1), axis=0)

    # Apply CLR transformation
    print("Applying CLR transformation...")
    otu_pseudo = otu_rel + 1e-6
    geom_mean = np.exp(np.mean(np.log(otu_pseudo), axis=1))
    otu_clr = np.log(otu_pseudo.div(geom_mean, axis=0))

    # Option B: keep the top 150 varying taxa for SHAP
    print("Filtering down to 150 top varying biological taxa features for SHAP interpretability...")
    variances = otu_clr.var()
    top_150_taxa = variances.sort_values(ascending=False).head(150).index
    otu_clr_filtered = otu_clr[top_150_taxa]

    # Compute Alpha Diversity
    print("Computing Alpha Diversity...")
    p = otu_rel + 1e-10
    div_df = pd.DataFrame({
        'shannon_entropy': -np.sum(p * np.log(p), axis=1),
        'simpson_index': 1 - np.sum(p**2, axis=1),
        'observed_taxa': (otu_df > 0).sum(axis=1)
    }, index=common_samples)

    print("Merging features...")
    targets = soil_map[['total_nitrogen', 'nitrate_umol_per_l', 'ammonium_umol_per_l', 'ph', 'latitude_deg', 'longitude_deg']]

    final_df = pd.concat([otu_clr_filtered, div_df], axis=1).join(targets)

    final_df.to_csv('engineered_features.csv')
    print("Feature engineering complete!")

if __name__ == "__main__":
    engineered_features()
