import pandas as pd
import numpy as np
from biom import load_table

def engineered_features():
    print("Loading mapping file...")
    # Load mapping file
    df_map = pd.read_csv('emp_qiime_mapping_subset_2k.tsv', sep='\t', low_memory=False, index_col=0)

    # Filter for soil
    soil_map = df_map[df_map['empo_3'].str.contains('Soil', na=False, case=False)]
    print(f"Total soil samples found: {len(soil_map)}")

    # Load BIOM table
    print("Loading BIOM table...")
    table = load_table('emp_cr_gg_13_8.subset_2k.biom')

    # Get intersection of samples
    common_samples = list(set(soil_map.index) & set(table.ids(axis='sample')))
    print(f"Intersection of samples: {len(common_samples)}")

    soil_map = soil_map.loc[common_samples]

    # Extract OTU counts for common samples
    # Keep top 1000 OTUs by variance or abundance to manage dimensionality
    print("Extracting counts and filtering OTUs...")
    otu_counts = []
    for sample_id in common_samples:
        otu_counts.append(table.data(sample_id, dense=True))

    otu_df = pd.DataFrame(np.array(otu_counts), index=common_samples, columns=table.ids(axis='observation'))

    # Compute relative abundance
    row_sums = otu_df.sum(axis=1)
    # Avoid division by zero
    otu_rel = otu_df.div(row_sums.replace(0, 1), axis=0)

    # Filter to top 500 most abundant taxa across all samples
    top_taxa = otu_rel.mean(axis=0).sort_values(ascending=False).head(500).index
    otu_top = otu_rel[top_taxa]

    # Apply CLR transformation
    # First, add pseudo-count to handle zeros
    print("Applying CLR transformation...")
    pseudo_count = 1e-6
    otu_pseudo = otu_top + pseudo_count
    geom_mean = np.exp(np.mean(np.log(otu_pseudo), axis=1))
    otu_clr = np.log(otu_pseudo.div(geom_mean, axis=0))

    # Compute Alpha Diversity (Shannon proxy)
    print("Computing Alpha Diversity...")
    p = otu_rel + 1e-10 # prevent log(0)
    shannon = -np.sum(p * np.log(p), axis=1)

    # Merge engineered features
    features_df = pd.concat([otu_clr, pd.Series(shannon, name='shannon_entropy', index=common_samples)], axis=1)

    # Add target variables for saving
    targets = soil_map[['nitrate_umol_per_l', 'ammonium_umol_per_l', 'phosphate_umol_per_l', 'latitude_deg', 'longitude_deg', 'temperature_deg_c', 'ph']]

    final_df = features_df.join(targets)

    # Save the output
    print("Saving engineered features to 'engineered_features.csv'...")
    final_df.to_csv('engineered_features.csv')
    print("Feature engineering complete!")

if __name__ == "__main__":
    engineered_features()
