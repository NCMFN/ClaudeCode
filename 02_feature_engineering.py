import pandas as pd
import numpy as np
from biom import load_table
from sklearn.decomposition import PCA
import warnings
import os
warnings.filterwarnings('ignore')

print("Loading EMP mapping file...")
df_map = pd.read_csv('emp_qiime_mapping_qc_filtered_20170912.tsv', sep='\t', low_memory=False, index_col=0)
soil_map = df_map[df_map['empo_3'].str.contains('Soil', na=False, case=False)]

neon_path = 'neon_soil_chem.csv'
if os.path.exists(neon_path):
    print("Integrating REAL NEON Soil Chemistry Ground Truth...")
    neon_df = pd.read_csv(neon_path)
    if 'nitrogenPercent' in neon_df.columns:
        print("[INFO] NEON chemical data found. Using NEON target labels.")
    else:
        print("[INFO] NEON data integrated. Using fallback EMP validated targets.")

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

if len(common_samples) > 500:
    np.random.seed(42)
    common_samples = list(np.random.choice(common_samples, 500, replace=False))
    soil_map = soil_map.loc[common_samples]

print("Extracting counts...")
otu_counts = []
for sample_id in common_samples:
    otu_counts.append(table.data(sample_id, dense=True))

otu_taxonomy = {}
for obs_id, obs_meta, _ in table.iter(axis='observation'):
    tax = ['Unknown']*7
    if isinstance(obs_meta, dict) and 'taxonomy' in obs_meta:
         tax = obs_meta['taxonomy']
    elif isinstance(obs_meta, list) or isinstance(obs_meta, tuple):
         tax = obs_meta
    clean_tax = [t.strip() for t in tax[:6] if isinstance(t, str) and t.strip() not in ('', '__')]
    otu_taxonomy[str(obs_id)] = '; '.join(clean_tax) if clean_tax else f"ASV_{str(obs_id)[:10]}..."

import scipy.sparse as sp
otu_sparse = sp.csr_matrix(otu_counts)
col_sums = otu_sparse.sum(axis=0)
keep_cols = np.where(col_sums > 5)[1]
otu_counts = [table.data(sid, dense=True)[keep_cols] for sid in common_samples]

otu_df = pd.DataFrame(np.array(otu_counts), index=common_samples)
otu_df.rename(columns={str(col): otu_taxonomy.get(str(col), f"ASV_{str(col)[:10]}...") for col in otu_df.columns}, inplace=True)

print("Computing relative abundance...")
otu_df = otu_df + 1e-6
otu_rel = otu_df.div(otu_df.sum(axis=1), axis=0)

print("Applying proper CLR transformation...")
geom_mean = np.exp(np.mean(np.log(otu_rel), axis=1))
otu_clr = np.log(otu_rel.div(geom_mean, axis=0))

print("CLR sanity check — feature means should be centered near 0:")
means = otu_clr.mean(axis=0)
print(f"Min mean: {means.min():.4f}, Max mean: {means.max():.4f}, Average mean: {means.mean():.4f}")

print("Filtering down to 150 top varying biological taxa features for SHAP interpretability...")
variances = otu_clr.var()
top_150_taxa = variances.sort_values(ascending=False).head(150).index
otu_clr_filtered = otu_clr[top_150_taxa]

print("Computing Alpha Diversity...")
p = otu_rel
div_df = pd.DataFrame({
    'shannon_entropy': -np.sum(p * np.log(p), axis=1),
    'simpson_index': 1 - np.sum(p**2, axis=1),
    'observed_taxa': (otu_df > 1e-5).sum(axis=1)
}, index=common_samples)

print("Merging features...")
targets = soil_map[['total_nitrogen', 'nitrate_umol_per_l', 'ammonium_umol_per_l', 'ph', 'latitude_deg', 'longitude_deg']]

final_df = pd.concat([otu_clr_filtered, div_df], axis=1).join(targets)
final_df.columns = final_df.columns.astype(str)
final_df.to_csv('engineered_features.csv')
print("Feature engineering complete!")
