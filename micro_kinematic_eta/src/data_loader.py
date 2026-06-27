import pandas as pd
import numpy as np
import logging
import datetime
from config import AIS_COLUMNS, SOG_VALID_RANGE, LAT_VALID_RANGE, LON_VALID_RANGE, COG_VALID_RANGE

class AISDataLoader:
    def __init__(self):
        self.logger = logging.getLogger(__name__)

    def load(self, filepath):
        self.logger.info(f"Loading data from {filepath}")
        df = pd.read_csv(filepath)

        # Keep only required columns
        cols_to_keep = [c for c in AIS_COLUMNS if c in df.columns]
        df = df[cols_to_keep]

        if 'BaseDateTime' in df.columns:
            df['BaseDateTime'] = pd.to_datetime(df['BaseDateTime'])

        type_mapping = {
            'LAT': 'float64',
            'LON': 'float64',
            'SOG': 'float32',
            'COG': 'float32',
            'Heading': 'float32',
            'Draft': 'float32',
            'MMSI': 'Int64',
            'IMO': 'Int64'
        }
        for col, dtype in type_mapping.items():
            if col in df.columns:
                df[col] = df[col].astype(dtype)

        self.logger.info(f"Data loaded. Shape: {df.shape}")
        for col in df.columns:
            null_pct = df[col].isnull().mean() * 100
            self.logger.info(f"Column: {col} | Nulls: {null_pct:.2f}% | Dtype: {df[col].dtype}")

        return df

    def validate(self, df):
        initial_count = len(df)
        report = {}

        # LAT filter
        if 'LAT' in df.columns:
            valid_lat = df['LAT'].between(LAT_VALID_RANGE[0], LAT_VALID_RANGE[1])
            removed_lat = (~valid_lat).sum()
            df = df[valid_lat]
            self.logger.info(f"Removed {removed_lat} rows with invalid LAT")
            report['removed_lat'] = removed_lat

        # LON filter
        if 'LON' in df.columns:
            valid_lon = df['LON'].between(LON_VALID_RANGE[0], LON_VALID_RANGE[1])
            removed_lon = (~valid_lon).sum()
            df = df[valid_lon]
            self.logger.info(f"Removed {removed_lon} rows with invalid LON")
            report['removed_lon'] = removed_lon

        # SOG filter (also removes 999 sentinel)
        if 'SOG' in df.columns:
            valid_sog = df['SOG'].between(SOG_VALID_RANGE[0], SOG_VALID_RANGE[1])
            removed_sog = (~valid_sog).sum()
            df = df[valid_sog]
            self.logger.info(f"Removed {removed_sog} rows with invalid SOG (including 999)")
            report['removed_sog'] = removed_sog

        # COG filter
        if 'COG' in df.columns:
            valid_cog = df['COG'].between(COG_VALID_RANGE[0], COG_VALID_RANGE[1])
            removed_cog = (~valid_cog).sum()
            df = df[valid_cog]
            self.logger.info(f"Removed {removed_cog} rows with invalid COG")
            report['removed_cog'] = removed_cog

        # Future timestamps filter
        if 'BaseDateTime' in df.columns:
            now = pd.Timestamp.now()
            # For testing with synthetic data, allow future dates if generated, but to satisfy
            # requirements, let's clip it or just log. The spec says:
            # "Assert BaseDateTime has no future timestamps beyond current date"
            # But our generated data goes up to 2026. Let's just filter out strictly future ones relative to a far future or ignore the assert for synthetic.
            # Actually, let's filter correctly as requested.
            valid_time = df['BaseDateTime'] <= now
            removed_time = (~valid_time).sum()
            if removed_time > 0:
                self.logger.info(f"Removed {removed_time} rows with future BaseDateTime (beyond {now})")
                df = df[valid_time]
            report['removed_future_time'] = removed_time

            assert (df['BaseDateTime'] > now).sum() == 0, "Found future timestamps"

        report['total_removed'] = initial_count - len(df)
        report['final_count'] = len(df)
        self.logger.info(f"Validation complete. Final shape: {df.shape}")

        return df, report

    def sample_for_dev(self, df, filepath, n=100000):
        if len(df) > n and 'VesselType' in df.columns:
            df_sample = df.groupby('VesselType', group_keys=False).apply(lambda x: x.sample(min(len(x), n // df['VesselType'].nunique())))
        else:
            df_sample = df.head(n)
        df_sample.to_parquet(filepath)
        self.logger.info(f"Saved sample of shape {df_sample.shape} to {filepath}")
        return df_sample
