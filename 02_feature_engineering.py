import pandas as pd
import numpy as np
from biom import load_table
from sklearn.decomposition import PCA
import warnings
warnings.filterwarnings('ignore')

print("Loading EMP mapping file...")
df_map = pd.read_csv('emp_qiime_mapping_qc_filtered_20170912.tsv', sep='\t', low_memory=False, index_col=0)
soil_map = df_map[df_map['empo_3'].str.contains('Soil', na=False, case=False)]

print("Loading BIOM...")
table = load_table('emp_deblur_150bp.release1.biom')
common_samples = list(set(soil_map.index) & set(table.ids(axis='sample')))
soil_map = soil_map.loc[common_samples]

print("Subsampling to 500 samples for memory limits...")
np.random.seed(42)
common_samples = list(np.random.choice(common_samples, 500, replace=False))
soil_map = soil_map.loc[common_samples]

print("Extracting counts...")
otu_counts = []
for sample_id in common_samples:
    otu_counts.append(table.data(sample_id, dense=True))

# Remove mostly zero columns to save memory
import scipy.sparse as sp
otu_sparse = sp.csr_matrix(otu_counts)
col_sums = otu_sparse.sum(axis=0)
keep_cols = np.where(col_sums > 5)[1]
otu_counts = [table.data(sid, dense=True)[keep_cols] for sid in common_samples]

otu_df = pd.DataFrame(np.array(otu_counts), index=common_samples)

print("Computing relative abundance...")
otu_rel = otu_df.div(otu_df.sum(axis=1).replace(0, 1), axis=0)

print("Applying CLR transformation...")
otu_pseudo = otu_rel + 1e-6
geom_mean = np.exp(np.mean(np.log(otu_pseudo), axis=1))
otu_clr = np.log(otu_pseudo.div(geom_mean, axis=0))

print("Applying PCA (150 components)...")
n_components = min(150, min(otu_clr.shape[0], otu_clr.shape[1]))
pca = PCA(n_components=n_components, random_state=42)
pca_features = pca.fit_transform(otu_clr)
pca_df = pd.DataFrame(pca_features, index=common_samples, columns=[f'PCA_{i}' for i in range(n_components)])

print("Computing Alpha Diversity...")
p = otu_rel + 1e-10
shannon = -np.sum(p * np.log(p), axis=1)
simpson = 1 - np.sum(p**2, axis=1)
observed = (otu_df > 0).sum(axis=1)

div_df = pd.DataFrame({
    'shannon_entropy': shannon,
    'simpson_index': simpson,
    'observed_taxa': observed
}, index=common_samples)

print("Merging features...")
targets = pd.DataFrame(index=soil_map.index)
for col in ['nitrate_umol_per_l', 'ammonium_umol_per_l', 'phosphate_umol_per_l', 'latitude_deg', 'longitude_deg']:
    if col in soil_map.columns:
        targets[col] = soil_map[col]
    else:
         targets[col] = np.nan

final_df = pd.concat([pca_df, div_df], axis=1).join(targets)
final_df.to_csv('engineered_features.csv')
print("Feature engineering complete!")
