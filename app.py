import streamlit as st

st.title("Flight Delay Prediction API")
st.write("This app simulates predicting flight delays using the trained XGBoost model.")

st.sidebar.header("Input Flight Features")
distance = st.sidebar.slider("Distance (miles)", 200, 3000, 1500)
visibility = st.sidebar.slider("Visibility (miles)", 0.5, 10.0, 8.0)
wind_speed = st.sidebar.slider("Wind Speed (mph)", 0.0, 40.0, 15.0)
precipitation = st.sidebar.slider("Precipitation (inches)", 0.0, 2.0, 0.0)
temperature = st.sidebar.slider("Temperature (F)", -10.0, 40.0, 22.0)
traffic_volume = st.sidebar.slider("Traffic Volume", 50, 500, 300)

if st.button("Predict Delay"):
    st.write("Processing input through the model pipeline...")
    mock_delay = (wind_speed * 0.5) + (traffic_volume * 0.05) - (visibility * 1.5)
    mock_delay = max(0, mock_delay)
    st.success(f"Predicted Flight Delay: {mock_delay:.2f} minutes")

st.write("Note: This is a mocked UI representation of the Real-Time Prediction System.")
