import streamlit as st
import pandas as pd
import numpy as np
import pickle

st.title("SAF Drop-In Compatibility Predictor")
st.write("Predict whether a Sustainable Aviation Fuel (SAF) blend is drop-in compatible based on its chemical and physical properties.")

# Load models and transformers
@st.cache_resource
def load_models():
    with open('best_saf_model.pkl', 'rb') as f:
        model = pickle.load(f)
    with open('scaler.pkl', 'rb') as f:
        scaler = pickle.load(f)
    with open('imputer.pkl', 'rb') as f:
        imputer = pickle.load(f)
    return model, scaler, imputer

try:
    model, scaler, imputer = load_models()

    st.sidebar.header("Input Features")

    # Input sliders/fields based on our dataset properties
    arom = st.sidebar.slider("Aromatics vol %", 0.0, 50.0, 15.0)
    alk = st.sidebar.slider("Alkanes vol %", 0.0, 100.0, 60.0)
    cyc = st.sidebar.slider("Cycloalkanes vol %", 0.0, 50.0, 20.0)
    ole = st.sidebar.slider("Olefins vol %", 0.0, 20.0, 1.0)
    visc = st.sidebar.slider("Kinematic Viscosity (mm2/s)", 0.0, 15.0, 5.0)
    dens = st.sidebar.slider("Density (kg/m3)", 700.0, 900.0, 800.0)
    flash = st.sidebar.slider("Flash Point (C)", 0.0, 100.0, 45.0)
    freez = st.sidebar.slider("Freezing Point (C)", -80.0, 0.0, -50.0)
    heat = st.sidebar.slider("Net Heat of Combustion (MJ/kg)", 40.0, 48.0, 43.5)

    input_data = pd.DataFrame([{
        'Aromatics_vol_percent': arom,
        'Alkanes_vol_percent': alk,
        'Cycloalkanes_vol_percent': cyc,
        'Olefins_vol_percent': ole,
        'Kinematic_Viscosity_mms2': visc,
        'Density_kgm3': dens,
        'Flash_Point_C': flash,
        'Freezing_Point_C': freez,
        'Net_Heat_of_Combustion_MJkg': heat
    }])

    st.subheader("Selected Features")
    st.write(input_data)

    if st.button("Predict Compatibility"):
        # Preprocess
        imputed_input = imputer.transform(input_data)
        scaled_input = scaler.transform(imputed_input)

        # Predict
        prediction = model.predict(scaled_input)[0]
        probability = model.predict_proba(scaled_input)[0][1]

        st.subheader("Prediction Result")
        if prediction == 1:
            st.success(f"✅ Drop-In Compatible! (Probability: {probability:.2%})")
        else:
            st.error(f"❌ Not Compatible. (Probability of compatibility: {probability:.2%})")

except Exception as e:
    st.error(f"Error loading models or predicting: {e}")
    st.write("Ensure you have run `train_model.py` to generate the `.pkl` files.")
