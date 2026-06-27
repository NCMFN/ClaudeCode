from sklearn.cluster import DBSCAN
import numpy as np
import pandas as pd
import geopy.distance
import logging

class PortDestinationClusterer:
    def __init__(self, eps=0.05, min_samples=10):
        self.eps = eps
        self.min_samples = min_samples
        self.port_centroids = {}
        self.logger = logging.getLogger(__name__)

    def fit(self, df):
        # Extract terminal positions: rows where SOG < 0.5 knots
        stationary_df = df[df['SOG'] < 0.5].copy()
        self.logger.info(f"Clustering on {len(stationary_df)} stationary points (SOG < 0.5)")

        if len(stationary_df) == 0:
            self.logger.warning("No stationary points found. Using dummy clustering.")
            self.port_centroids = {0: (0.0, 0.0)}
            return

        coords = stationary_df[['LAT', 'LON']].values
        dbscan = DBSCAN(eps=5.0, min_samples=2) # relaxed for synthetic data
        labels = dbscan.fit_predict(coords)

        stationary_df['cluster_id'] = labels

        for cluster_id in np.unique(labels):
            if cluster_id != -1:  # -1 is noise
                cluster_points = stationary_df[stationary_df['cluster_id'] == cluster_id]
                mean_lat = cluster_points['LAT'].mean()
                mean_lon = cluster_points['LON'].mean()
                self.port_centroids[cluster_id] = (mean_lat, mean_lon)

        self.logger.info(f"Found {len(self.port_centroids)} port clusters")

        # Save centroids
        centroids_df = pd.DataFrame([
            {'cluster_id': cid, 'dest_lat': lat, 'dest_lon': lon}
            for cid, (lat, lon) in self.port_centroids.items()
        ])
        centroids_df.to_csv('outputs/results/port_clusters.csv', index=False)
        self.logger.info("Saved port clusters to outputs/results/port_clusters.csv")

    def assign_destination(self, df):
        if not self.port_centroids:
            self.logger.warning("No port clusters available. Ensure fit() is called with stationary points.")
            df['dest_cluster_id'] = -1
            df['dest_lat'] = np.nan
            df['dest_lon'] = np.nan
            df['dist_to_dest_km'] = np.nan
            return df

        centroids_list = list(self.port_centroids.items())

        def find_nearest(row):
            min_dist = float('inf')
            best_cid, best_lat, best_lon = -1, np.nan, np.nan
            row_coord = (row['LAT'], row['LON'])
            for cid, (lat, lon) in centroids_list:
                try:
                    dist = geopy.distance.geodesic(row_coord, (lat, lon)).km
                    if dist < min_dist:
                        min_dist = dist
                        best_cid = cid
                        best_lat = lat
                        best_lon = lon
                except ValueError:
                    continue
            return pd.Series([best_cid, best_lat, best_lon, min_dist])

        # In a real big data scenario, this apply is slow, but acceptable for this scale/project
        df[['dest_cluster_id', 'dest_lat', 'dest_lon', 'dist_to_dest_km']] = df.apply(find_nearest, axis=1)
        self.logger.info("Assigned destinations and computed geodesic distances")
        return df
