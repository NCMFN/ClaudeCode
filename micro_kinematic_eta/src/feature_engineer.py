import pandas as pd
import numpy as np
import logging
from config import MICRO_KINEMATIC_ZONE_THRESHOLD_KM

class KinematicFeatureEngineer:
    def __init__(self):
        self.logger = logging.getLogger(__name__)

    def transform(self, df):
        self.logger.info("Starting feature engineering")

        # Ensure correct types and sorting
        df = df.sort_values(['MMSI', 'BaseDateTime'])

        # 5a. Kinematic features
        df['SOG_kmh'] = df['SOG'] * 1.852

        # Group by MMSI for rolling stats
        grouped = df.groupby('MMSI')
        df['SOG_rolling_mean_3'] = grouped['SOG_kmh'].rolling(window=3, min_periods=1).mean().reset_index(level=0, drop=True)
        # fillna(0) for std where window < 2
        df['SOG_rolling_std_3'] = grouped['SOG_kmh'].rolling(window=3, min_periods=1).std().reset_index(level=0, drop=True).fillna(0)

        df['COG_sin'] = np.sin(np.radians(df['COG']))
        df['COG_cos'] = np.cos(np.radians(df['COG']))
        df['Heading_sin'] = np.sin(np.radians(df['Heading']))
        df['Heading_cos'] = np.cos(np.radians(df['Heading']))

        # angular difference
        diff = (df['COG'] - df['Heading']) % 360
        df['COG_Heading_delta'] = np.minimum(diff, 360 - diff)

        df['SOG_accel'] = grouped['SOG_kmh'].diff().fillna(0)

        # 5b. Spatial features
        # dist_to_dest_km already calculated
        if 'dist_to_dest_km' in df.columns:
            df['is_micro_kinematic_zone'] = (df['dist_to_dest_km'] <= MICRO_KINEMATIC_ZONE_THRESHOLD_KM).astype(int)

            # calculate bearing to dest
            # simplified bearing calculation for performance, or precise if needed
            # delta_lon = np.radians(df['dest_lon'] - df['LON'])
            # lat1, lat2 = np.radians(df['LAT']), np.radians(df['dest_lat'])
            # y = np.sin(delta_lon) * np.cos(lat2)
            # x = np.cos(lat1) * np.sin(lat2) - np.sin(lat1) * np.cos(lat2) * np.cos(delta_lon)
            # bearing_rad = np.arctan2(y, x)

            # We'll use a simpler vectorized bearing approximation for large datasets,
            # or the exact formula
            lat1 = np.radians(df['LAT'])
            lat2 = np.radians(df['dest_lat'])
            dLon = np.radians(df['dest_lon'] - df['LON'])
            y = np.sin(dLon) * np.cos(lat2)
            x = np.cos(lat1) * np.sin(lat2) - np.sin(lat1) * np.cos(lat2) * np.cos(dLon)
            bearing = (np.degrees(np.arctan2(y, x)) + 360) % 360

            df['bearing_to_dest'] = bearing
            df['bearing_sin'] = np.sin(np.radians(bearing))
            df['bearing_cos'] = np.cos(np.radians(bearing))

            # bearing_COG_alignment = cosine similarity between bearing and COG vectors
            df['bearing_COG_alignment'] = (df['COG_sin'] * df['bearing_sin']) + (df['COG_cos'] * df['bearing_cos'])
        else:
            self.logger.warning("dist_to_dest_km not found in dataframe")

        # 5c. Temporal features
        df['hour_of_day'] = df['BaseDateTime'].dt.hour
        df['day_of_week'] = df['BaseDateTime'].dt.dayofweek
        df['month'] = df['BaseDateTime'].dt.month
        df['is_weekend'] = (df['day_of_week'] >= 5).astype(int)
        df['is_night'] = df['hour_of_day'].isin([22, 23, 0, 1, 2, 3, 4, 5]).astype(int)

        # 5d. Structural features
        # top 10 vessel types
        top_types = df['VesselType'].value_counts().nlargest(10).index
        df['VesselType_enc'] = np.where(df['VesselType'].isin(top_types), df['VesselType'], 'Other')
        # Convert to category codes for model
        df['VesselType_enc'] = df['VesselType_enc'].astype('category').cat.codes

        cargo_types = ['cargo', 'Cargo', '70', '71', '72', '73', '74', '75', '76', '77', '78', '79']
        df['is_cargo'] = df['VesselType'].isin(cargo_types).astype(int)

        # 5e. Target variable: ETA_hours
        # For each vessel, find the timestamp when it first enters dist_to_dest_km < 2.0
        df['arrived'] = df['dist_to_dest_km'] < 2.0

        # Get first arrival time per vessel
        first_arrival = df[df['arrived']].groupby('MMSI')['BaseDateTime'].min().reset_index()
        first_arrival.rename(columns={'BaseDateTime': 'arrival_timestamp'}, inplace=True)

        df = df.merge(first_arrival, on='MMSI', how='left')

        # calculate ETA_hours
        df['ETA_hours'] = (df['arrival_timestamp'] - df['BaseDateTime']).dt.total_seconds() / 3600.0

        # Filter out invalid ETA
        initial_count = len(df)
        df = df[(df['ETA_hours'] > 0) & (df['ETA_hours'] <= 168)]
        self.logger.info(f"Filtered out {initial_count - len(df)} rows with invalid ETA_hours (<=0 or >168)")

        self.logger.info(f"Feature engineering complete. Output shape: {df.shape}")

        return df
