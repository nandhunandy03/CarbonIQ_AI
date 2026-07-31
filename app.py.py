import streamlit as st
import pandas as pd
import joblib

model = joblib.load('carbon_model.pkl')

st.title("Textile Dyeing & Finishing — CO2 Emission Predictor")

fabric_type = st.selectbox("Fabric Type", ['Cotton', 'Polyester', 'Cotton-Poly Blend', 'Viscose'])
dye_type = st.selectbox("Dye Type", ['Reactive', 'Disperse', 'Vat', 'Direct'])
fuel_type = st.selectbox("Fuel Type", ['Coal', 'Gas'])
season = st.selectbox("Season", ['Summer', 'Winter', 'Monsoon'])

production_kg = st.number_input("Production (kg)", min_value=0.0, value=500.0)
machine_runtime_hours = st.number_input("Machine Runtime (hours)", min_value=0.0, value=8.0)
electricity_kwh = st.number_input("Electricity Used (kWh)", min_value=0.0, value=300.0)
water_liters = st.number_input("Water Used (liters)", min_value=0.0, value=15000.0)
dye_chemical_kg = st.number_input("Dye/Chemical Used (kg)", min_value=0.0, value=20.0)
fuel_qty = st.number_input("Fuel Quantity (kg coal or m3 gas)", min_value=0.0, value=100.0)

if st.button("Predict CO2 Emissions"):
    input_df = pd.DataFrame([{
        'fabric_type': fabric_type,
        'dye_type': dye_type,
        'fuel_type': fuel_type,
        'season': season,
        'production_kg': production_kg,
        'machine_runtime_hours': machine_runtime_hours,
        'electricity_kwh': electricity_kwh,
        'water_liters': water_liters,
        'dye_chemical_kg': dye_chemical_kg,
        'fuel_qty': fuel_qty
    }])

    prediction = model.predict(input_df)[0]
    st.success(f"Estimated CO2 Emissions: {prediction:.2f} kg CO2e")