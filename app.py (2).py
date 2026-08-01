import streamlit as st
import pandas as pd
import joblib
import matplotlib.pyplot as plt

st.set_page_config(
    page_title="Carbon Emission Predictor",
    page_icon="🌍",
    layout="wide"
)

model = joblib.load('carbon_model.pkl')

# Reference stats from training dataset (for comparison chart)
DATASET_MEAN = 599.94
DATASET_MIN = 199.65
DATASET_MAX = 1117.96

# Emission factors (for pie chart breakdown only)
ELEC_EF = 0.82
COAL_EF = 2.42
GAS_EF = 2.03

# ---------- Custom CSS for styling ----------
st.markdown("""
    <style>
    .main-title {
        font-size: 42px;
        font-weight: 700;
        color: #2E7D32;
        text-align: center;
        margin-bottom: 0px;
    }
    .subtitle {
        font-size: 18px;
        color: #555;
        text-align: center;
        margin-bottom: 30px;
    }
    .result-box {
        background-color: #E8F5E9;
        border-left: 6px solid #2E7D32;
        padding: 20px;
        border-radius: 10px;
        font-size: 24px;
        font-weight: 600;
        color: #1B5E20;
        text-align: center;
    }
    .stButton>button {
        background-color: #2E7D32;
        color: white;
        font-weight: 600;
        border-radius: 8px;
        padding: 10px 30px;
        border: none;
    }
    .stButton>button:hover {
        background-color: #1B5E20;
        color: white;
    }
    </style>
""", unsafe_allow_html=True)

# ---------- Header ----------
st.markdown('<div class="main-title">🌍 Carbon Emission Predictor</div>', unsafe_allow_html=True)
st.markdown('<div class="subtitle">Textile Dyeing & Finishing Process — ML-based CO₂ Emission Estimation</div>', unsafe_allow_html=True)

st.divider()

# ---------- Input layout in columns ----------
col1, col2 = st.columns(2)

with col1:
    st.subheader("Process Details")
    fabric_type = st.selectbox("🧵 Fabric Type", ['Cotton', 'Polyester', 'Cotton-Poly Blend', 'Viscose'])
    dye_type = st.selectbox("🎨 Dye Type", ['Reactive', 'Disperse', 'Vat', 'Direct'])
    fuel_type = st.selectbox("🔥 Fuel Type", ['Coal', 'Gas'])
    season = st.selectbox("🌦️ Season", ['Summer', 'Winter', 'Monsoon'])

with col2:
    st.subheader("Production Parameters")
    production_kg = st.number_input("📦 Production (kg)", min_value=0.0, value=500.0)
    machine_runtime_hours = st.number_input("⏱️ Machine Runtime (hours)", min_value=0.0, value=8.0)
    electricity_kwh = st.number_input("⚡ Electricity Used (kWh)", min_value=0.0, value=300.0)
    water_liters = st.number_input("💧 Water Used (liters)", min_value=0.0, value=15000.0)
    dye_chemical_kg = st.number_input("🧪 Dye/Chemical Used (kg)", min_value=0.0, value=20.0)
    fuel_qty = st.number_input("🛢️ Fuel Quantity (kg coal / m³ gas)", min_value=0.0, value=100.0)

st.divider()

# ---------- Predict button and result ----------
center = st.columns([1, 2, 1])
with center[1]:
    predict_clicked = st.button("Predict CO2 Emissions", use_container_width=True)

if predict_clicked:
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

    st.markdown(f"""
        <div class="result-box">
            Estimated CO₂ Emissions: {prediction:.2f} kg CO2e
        </div>
    """, unsafe_allow_html=True)

    if prediction < 400:
        st.info("🟢 Low emission batch — efficient process.")
    elif prediction < 800:
        st.warning("🟡 Moderate emission batch — room for optimization.")
    else:
        st.error("🔴 High emission batch — consider fuel/energy efficiency improvements.")

    # ---------- Two charts side by side ----------
    chart_col1, chart_col2 = st.columns(2)

    with chart_col1:
        st.subheader("How this compares")
        labels = ['Your\nPrediction', 'Dataset\nAverage', 'Dataset\nMin', 'Dataset\nMax']
        values = [prediction, DATASET_MEAN, DATASET_MIN, DATASET_MAX]
        colors = ['#2E7D32', '#90A4AE', '#90A4AE', '#90A4AE']

        fig1, ax1 = plt.subplots(figsize=(5, 4))
        bars = ax1.bar(labels, values, color=colors)
        ax1.set_ylabel("CO2 Emissions (kg)")
        ax1.set_title("Prediction vs Reference Values")
        for bar in bars:
            height = bar.get_height()
            ax1.annotate(f'{height:.0f}', xy=(bar.get_x() + bar.get_width()/2, height),
                        xytext=(0, 3), textcoords="offset points", ha='center', fontsize=8)
        plt.tight_layout()
        st.pyplot(fig1)

    with chart_col2:
        st.subheader("Emission source breakdown")

        electricity_emissions = electricity_kwh * ELEC_EF
        fuel_ef = COAL_EF if fuel_type == 'Coal' else GAS_EF
        fuel_emissions = fuel_qty * fuel_ef

        pie_labels = ['Electricity', f'Fuel ({fuel_type})']
        pie_values = [electricity_emissions, fuel_emissions]
        pie_colors = ['#42A5F5', '#EF5350']

        fig2, ax2 = plt.subplots(figsize=(5, 4))
        wedges, texts, autotexts = ax2.pie(
            pie_values, labels=pie_labels, autopct='%1.1f%%',
            colors=pie_colors, startangle=90,
            textprops={'fontsize': 10}
        )
        ax2.set_title("Contribution to Emissions")
        plt.tight_layout()
        st.pyplot(fig2)

st.divider()
st.caption("Built with a Linear Regression model trained on textile dyeing & finishing process data.")