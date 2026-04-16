import nbformat as nbf

with open('Flight_Delay_Prediction.ipynb', 'r') as f:
    nb = nbf.read(f, as_version=4)

realtime_cell = nbf.v4.new_code_cell('''import requests
import json

# --- 6. Real-Time Prediction System Pipeline ---
print("Simulating Real-Time Prediction Pipeline...")

def get_real_time_weather(airport_code):
    """Fetch real-time METAR data using Aviation Weather API."""
    url = f"https://aviationweather.gov/api/data/metar?ids={airport_code}&format=json"
    try:
        response = requests.get(url)
        data = response.json()
        if data:
            obs = data[0]
            # Map to our feature names
            weather = {
                'Temp_F': obs.get('temp', 0) * 9/5 + 32 if obs.get('temp') is not None else 50.0, # default if missing
                'Wind_Speed_kt': obs.get('wspd', 0),
                'Visibility_mi': 10.0 if obs.get('visib') == '10+' else float(obs.get('visib', 10.0)),
                'Precip_in': 0.0 # Standard METAR might not have hourly precip easily accessible in simple JSON, assume 0 for demo
            }
            return weather
    except Exception as e:
        print(f"Error fetching real-time weather: {e}")

    # Fallback default weather
    return {'Temp_F': 50.0, 'Wind_Speed_kt': 5.0, 'Visibility_mi': 10.0, 'Precip_in': 0.0}

def predict_flight_delay(origin, dest, airline, distance, scheduled_time, traffic_vol):
    """Pipeline to predict delay for a new scheduled flight."""

    # 1. Get real-time weather for origin
    current_weather = get_real_time_weather(origin)
    print(f"Real-time weather for {origin}: {current_weather}")

    # 2. Construct feature vector (must match training feature order exactly)
    # Using the X dataframe from training to get the right columns and structure
    input_data = pd.DataFrame(columns=X.columns)
    input_data.loc[0] = 0 # Initialize with zeros

    # Fill known base features
    input_data.loc[0, 'Distance'] = distance
    input_data.loc[0, 'Origin_Traffic_Vol'] = traffic_vol
    input_data.loc[0, 'Month'] = scheduled_time.month
    input_data.loc[0, 'DayOfWeek'] = scheduled_time.dayofweek
    input_data.loc[0, 'Hour'] = scheduled_time.hour

    # Fill weather features
    for k, v in current_weather.items():
         if k in input_data.columns:
                input_data.loc[0, k] = v

    # Fill categorical one-hot features
    airline_col = f'Reporting_Airline_{airline}'
    if airline_col in input_data.columns:
        input_data.loc[0, airline_col] = 1

    origin_col = f'Origin_{origin}'
    if origin_col in input_data.columns:
        input_data.loc[0, origin_col] = 1

    dest_col = f'Dest_{dest}'
    if dest_col in input_data.columns:
        input_data.loc[0, dest_col] = 1

    # 3. Scale input
    input_scaled = scaler.transform(input_data)

    # 4. Predict
    pred = xgb_model.predict(input_scaled)[0]
    return pred

# Simulate a flight
test_origin = 'ORD'
test_dest = 'JFK'
test_airline = 'AA'
test_distance = 733.0
test_time = datetime.now() + timedelta(hours=2)
test_traffic = 50 # Assuming 50 scheduled flights this hour at ORD

predicted_delay = predict_flight_delay(
    origin=test_origin,
    dest=test_dest,
    airline=test_airline,
    distance=test_distance,
    scheduled_time=test_time,
    traffic_vol=test_traffic
)

print(f"\\nPredicted Departure Delay for {test_airline} flight from {test_origin} to {test_dest} scheduled at {test_time.strftime('%Y-%m-%d %H:%00')}:")
print(f"{predicted_delay:.2f} minutes")
''')

nb['cells'].append(realtime_cell)

with open('Flight_Delay_Prediction.ipynb', 'w') as f:
    nbf.write(nb, f)

print("Appended Realtime cells.")
