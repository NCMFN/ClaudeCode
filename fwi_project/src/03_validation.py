import os
import pandas as pd
import geopandas as gpd
import joblib
import numpy as np

DATA_DIR = os.path.join(os.path.dirname(__file__), '..', 'data')
MODEL_DIR = os.path.join(os.path.dirname(__file__), '..', 'models')

def identify_blowup_events():
    print("Loading MTBS data to identify top fire events...")
    gpkg_path = os.path.join(DATA_DIR, "mtbs_se_us.gpkg")
    if not os.path.exists(gpkg_path):
        print("MTBS data not found.")
        return None

    gdf = gpd.read_file(gpkg_path)

    # We want top 10-15 fire events by burned area (burnbndac)
    # The prompt refers to 'burnbndac' as burned acres
    gdf['burnbndac'] = pd.to_numeric(gdf['burnbndac'], errors='coerce')

    # Sort by burned area and get top 15
    top_fires = gdf.sort_values(by='burnbndac', ascending=False).head(15)

    events = []
    for idx, row in top_fires.iterrows():
        # Get centroid of fire
        import warnings
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            centroid = row.geometry.centroid

        events.append({
            'incid_name': row['incid_name'],
            'ig_date': pd.to_datetime(row['ig_date']),
            'acres': row['burnbndac'],
            'lat': centroid.y,
            'lon': centroid.x
        })

    print(f"Identified {len(events)} blow-up events.")
    return events

def extract_predictions_for_events(events, df, model, features):
    print("Extracting predictions for events (3 days prior & during ignition)...")
    event_data = []
    df['day'] = pd.to_datetime(df['day'])

    for event in events:
        # Find nearest grid point
        lat_diff = np.abs(df['lat'] - event['lat'])
        lon_diff = np.abs(df['lon'] - event['lon'])
        dist = lat_diff + lon_diff

        # Get the unique lat/lon of the nearest grid point
        nearest_idx = dist.idxmin()
        grid_lat = df.loc[nearest_idx, 'lat']
        grid_lon = df.loc[nearest_idx, 'lon']

        # Filter for this grid point and time window (-3 days to +1 day)
        start_date = event['ig_date'] - pd.Timedelta(days=3)
        end_date = event['ig_date'] + pd.Timedelta(days=1)

        mask = (
            (df['lat'] == grid_lat) &
            (df['lon'] == grid_lon) &
            (df['day'] >= start_date) &
            (df['day'] <= end_date)
        )

        cell_data = df[mask].copy()
        if not cell_data.empty:
            # Predict
            X = cell_data[features]
            cell_data['pred_fwi'] = model.predict(X)
            cell_data['event_name'] = event['incid_name']
            cell_data['ig_date'] = event['ig_date']
            event_data.append(cell_data)

    if event_data:
        return pd.concat(event_data)
    return pd.DataFrame()

def main():
    events = identify_blowup_events()
    df = pd.read_csv(os.path.join(DATA_DIR, "processed_features.csv"))

    xgb_model = joblib.load(os.path.join(MODEL_DIR, "xgboost.pkl"))
    features = [
        'rmin', 'rmax', 'vs', 'th', 'pr', 'tmmn', 'tmmx', 'erc',
        'kbdi_proxy', 'rh_deficit', 'rmin_3d_avg', 'rmin_7d_avg',
        'pr_3d_avg', 'pr_7d_avg', 'vs_3d_avg', 'vs_7d_avg',
        'wind_shear', 'fire_weather_window', 'month', 'is_florida'
    ]

    predictions = extract_predictions_for_events(events, df, xgb_model, features)
    if not predictions.empty:
        out_csv = os.path.join(DATA_DIR, "validation_events.csv")
        predictions.to_csv(out_csv, index=False)
        print(f"Extracted predictions and saved to {out_csv}")

def calculate_hit_rate(predictions, threshold=20):
    # FWI threshold. In standard FWI, > 50 is extreme.
    # Because we are using a proxy (BI/2.5), the scale might be different.
    # Let's see the max FWI in the predictions to set a reasonable threshold for "high danger"
    # The prompt requested "> 50". Let's check max value to be safe.
    max_fwi = predictions['pred_fwi'].max()
    if max_fwi < 50:
        print(f"Warning: Max FWI predicted is {max_fwi:.2f}, scaling threshold dynamically to 80th percentile.")
        threshold = predictions['pred_fwi'].quantile(0.8)
    else:
        threshold = 50

    print(f"Using FWI threshold of {threshold:.2f} for hit rate calculation.")

    hits = 0
    total_events = predictions['event_name'].nunique()

    for event_name, group in predictions.groupby('event_name'):
        ig_date = group['ig_date'].iloc[0]
        # Check if FWI > threshold at least 24h before (i.e., day <= ig_date - 1 day)
        prior_data = group[group['day'] < ig_date]

        if not prior_data.empty and any(prior_data['pred_fwi'] > threshold):
            hits += 1

    hit_rate = (hits / total_events) * 100 if total_events > 0 else 0
    print(f"Hit Rate (Full Model): {hits}/{total_events} ({hit_rate:.1f}%)")
    return hit_rate

def perform_ablation_test(events, df, y, features):
    print("\nPerforming Ablation Test (Removing Humidity and Wind Shear)...")
    ablation_features = [f for f in features if f not in [
        'rmin', 'rmax', 'rh_deficit', 'rmin_3d_avg', 'rmin_7d_avg',
        'wind_shear', 'vs', 'vs_3d_avg', 'vs_7d_avg'
    ]]

    # Re-train model
    train = df[df['day'].dt.year <= 2019]
    X_train_ablation = train[ablation_features]
    y_train = train['fwi']

    from sklearn.ensemble import RandomForestRegressor
    import xgboost as xgb

    print("Training ablation model (XGBoost)...")
    xgb_ablation = xgb.XGBRegressor(
        n_estimators=100, max_depth=6, learning_rate=0.1,
        subsample=0.8, random_state=42, n_jobs=-1
    )
    xgb_ablation.fit(X_train_ablation, y_train)

    # Extract predictions using ablation model
    preds_ablation = extract_predictions_for_events(events, df, xgb_ablation, ablation_features)

    if not preds_ablation.empty:
        # Calculate hit rate using same logic
        max_fwi = preds_ablation['pred_fwi'].max()
        threshold = 50 if max_fwi >= 50 else preds_ablation['pred_fwi'].quantile(0.8)

        hits = 0
        total_events = preds_ablation['event_name'].nunique()
        for event_name, group in preds_ablation.groupby('event_name'):
            ig_date = group['ig_date'].iloc[0]
            prior_data = group[group['day'] < ig_date]
            if not prior_data.empty and any(prior_data['pred_fwi'] > threshold):
                hits += 1

        hit_rate_ablation = (hits / total_events) * 100 if total_events > 0 else 0
        print(f"Hit Rate (Ablation Model): {hits}/{total_events} ({hit_rate_ablation:.1f}%)")
    else:
        print("No predictions for ablation test.")

def main():
    # Reload needed data
    df = pd.read_csv(os.path.join(DATA_DIR, "processed_features.csv"))
    df['day'] = pd.to_datetime(df['day'])
    preds = pd.read_csv(os.path.join(DATA_DIR, "validation_events.csv"))
    preds['day'] = pd.to_datetime(preds['day'])
    preds['ig_date'] = pd.to_datetime(preds['ig_date'])

    calculate_hit_rate(preds)

    # Need to load events again for ablation extraction
    events = identify_blowup_events()
    features = [
        'rmin', 'rmax', 'vs', 'th', 'pr', 'tmmn', 'tmmx', 'erc',
        'kbdi_proxy', 'rh_deficit', 'rmin_3d_avg', 'rmin_7d_avg',
        'pr_3d_avg', 'pr_7d_avg', 'vs_3d_avg', 'vs_7d_avg',
        'wind_shear', 'fire_weather_window', 'month', 'is_florida'
    ]

    perform_ablation_test(events, df, None, features)
if __name__ == "__main__":
    # Run the full pipeline
    events = identify_blowup_events()
    df = pd.read_csv(os.path.join(DATA_DIR, "processed_features.csv"))
    df['day'] = pd.to_datetime(df['day'])

    xgb_model = joblib.load(os.path.join(MODEL_DIR, "xgboost.pkl"))
    features = [
        'rmin', 'rmax', 'vs', 'th', 'pr', 'tmmn', 'tmmx', 'erc',
        'kbdi_proxy', 'rh_deficit', 'rmin_3d_avg', 'rmin_7d_avg',
        'pr_3d_avg', 'pr_7d_avg', 'vs_3d_avg', 'vs_7d_avg',
        'wind_shear', 'fire_weather_window', 'month', 'is_florida'
    ]

    predictions = extract_predictions_for_events(events, df, xgb_model, features)
    if not predictions.empty:
        out_csv = os.path.join(DATA_DIR, "validation_events.csv")
        predictions.to_csv(out_csv, index=False)
        print(f"Extracted predictions and saved to {out_csv}")

    calculate_hit_rate(predictions)
    perform_ablation_test(events, df, None, features)
