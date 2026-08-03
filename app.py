import streamlit as st
import pandas as pd
import joblib
import matplotlib.pyplot as plt
import time
from fpdf import FPDF

st.set_page_config(
    page_title="Carbon Emission Predictor | Textile Industry",
    page_icon="🌍",
    layout="wide",
    initial_sidebar_state="expanded"
)

model = joblib.load('carbon_model.pkl')

DATASET_MEAN = 599.94
DATASET_MIN = 199.65
DATASET_MAX = 1117.96
ELEC_EF = 0.82
COAL_EF = 2.42
GAS_EF = 2.03

# ---------- Custom CSS ----------
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Poppins:wght@400;500;600;700&display=swap');
    html, body, [class*="css"] { font-family: 'Poppins', sans-serif; }

    .hero {
        background: linear-gradient(135deg, #1B5E20 0%, #43A047 60%, #81C784 100%);
        padding: 50px 30px;
        border-radius: 18px;
        color: white;
        text-align: center;
        margin-bottom: 25px;
    }
    .hero h1 { font-size: 42px; font-weight: 700; margin-bottom: 6px; }
    .hero p { font-size: 17px; opacity: 0.95; }
    .badge-row { margin-top: 14px; }
    .badge {
        display: inline-block;
        background: rgba(255,255,255,0.18);
        padding: 6px 14px;
        border-radius: 20px;
        font-size: 13px;
        margin: 0 5px;
    }

    .feature-card {
        background-color: #FFFFFF;
        border: 1px solid #E0E0E0;
        border-radius: 14px;
        padding: 22px;
        text-align: center;
        height: 100%;
        box-shadow: 0 2px 8px rgba(0,0,0,0.04);
    }
    .feature-card .icon { font-size: 32px; margin-bottom: 8px; }
    .feature-card h4 { color: #1B5E20; font-size: 16px; margin-bottom: 6px; }
    .feature-card p { font-size: 13px; color: #555; }

    .metric-card {
        background-color: #F1F8E9;
        border-radius: 12px;
        padding: 18px;
        text-align: center;
        box-shadow: 0 2px 6px rgba(0,0,0,0.06);
    }
    .metric-card h3 { color: #2E7D32; font-size: 13px; margin-bottom: 6px; text-transform: uppercase; letter-spacing: 0.5px; }
    .metric-card p { font-size: 22px; font-weight: 700; color: #1B1B1B; }

    .result-box {
        background: linear-gradient(135deg, #E8F5E9 0%, #F1F8E9 100%);
        border: 1px solid #A5D6A7;
        padding: 25px;
        border-radius: 14px;
        text-align: center;
        margin-top: 10px;
    }
    .result-box h2 { color: #1B5E20; font-size: 32px; font-weight: 700; }

    .step-card {
        text-align: center;
        padding: 10px;
    }
    .step-num {
        background-color: #2E7D32;
        color: white;
        width: 34px; height: 34px;
        border-radius: 50%;
        display: inline-flex;
        align-items: center;
        justify-content: center;
        font-weight: 700;
        margin-bottom: 8px;
    }

    .stButton>button {
        background-color: #2E7D32;
        color: white;
        font-weight: 600;
        border-radius: 10px;
        padding: 12px 40px;
        border: none;
        font-size: 16px;
    }
    .stButton>button:hover { background-color: #1B5E20; }

    .footer-box {
        background-color: #F5F5F5;
        border-radius: 14px;
        padding: 20px;
        text-align: center;
        margin-top: 30px;
    }
    .footer-icons a { margin: 0 10px; text-decoration: none; font-size: 20px; }

    footer {visibility: hidden;}
    </style>
""", unsafe_allow_html=True)

# ---------- Sidebar ----------
with st.sidebar:
    st.markdown("### 🌍 Project Overview")
    st.write(
        "Estimates CO₂ emissions from the **dyeing & finishing** stage of "
        "textile manufacturing using Machine Learning, trained on process data."
    )
    st.markdown("---")
    st.markdown("### 📊 Model Performance")
    st.write("**Algorithm:** Linear Regression")
    st.write("**R² Score:** 0.991")
    st.write("**MAE:** 15.38 kg CO2e")
    st.markdown("---")
    st.markdown("### 🔗 Links")
    st.write("[GitHub Repository](#)")
    st.write("[Project Report](#)")
    st.markdown("---")
    st.caption("Mini Project — Carbon Emission Prediction in the Textile Industry")

# ---------- Hero ----------
st.markdown("""
    <div class="hero">
        <h1>🌍 Carbon Emission Predictor</h1>
        <p>Textile Dyeing & Finishing Process — Machine Learning based CO₂ Estimation</p>
        <div class="badge-row">
            <span class="badge">🤖 Linear Regression</span>
            <span class="badge">📈 R² = 0.991</span>
            <span class="badge">♻️ Sustainability Tool</span>
        </div>
    </div>
""", unsafe_allow_html=True)

# ---------- Feature highlights ----------
f1, f2, f3, f4 = st.columns(4)
features = [
    ("⚡", "Instant Prediction", "Get CO2 estimates in real time from process inputs."),
    ("📊", "Visual Insights", "Compare results and see emission source breakdown."),
    ("📄", "Downloadable Report", "Export a PDF summary of each prediction."),
    ("🌱", "Sustainability Focus", "Built to support greener textile manufacturing."),
]
for col, (icon, title, desc) in zip([f1, f2, f3, f4], features):
    with col:
        st.markdown(f"""
            <div class="feature-card">
                <div class="icon">{icon}</div>
                <h4>{title}</h4>
                <p>{desc}</p>
            </div>
        """, unsafe_allow_html=True)

st.write("")

# ---------- Tabs for navigation ----------
tab1, tab2, tab3 = st.tabs(["🧮 Predict", "📖 How It Works", "ℹ️ About the Project"])

with tab1:
    m1, m2, m3 = st.columns(3)
    with m1:
        st.markdown(f'<div class="metric-card"><h3>Dataset Average</h3><p>{DATASET_MEAN:.0f} kg</p></div>', unsafe_allow_html=True)
    with m2:
        st.markdown(f'<div class="metric-card"><h3>Lowest Recorded</h3><p>{DATASET_MIN:.0f} kg</p></div>', unsafe_allow_html=True)
    with m3:
        st.markdown(f'<div class="metric-card"><h3>Highest Recorded</h3><p>{DATASET_MAX:.0f} kg</p></div>', unsafe_allow_html=True)

    st.write("")
    st.markdown("### Enter Your Process Details")

    col1, col2 = st.columns(2)
    with col1:
        st.markdown("**Process Details**")
        fabric_type = st.selectbox("🧵 Fabric Type", ['Cotton', 'Polyester', 'Cotton-Poly Blend', 'Viscose'])
        dye_type = st.selectbox("🎨 Dye Type", ['Reactive', 'Disperse', 'Vat', 'Direct'])
        fuel_type = st.selectbox("🔥 Fuel Type", ['Coal', 'Gas'])
        season = st.selectbox("🌦️ Season", ['Summer', 'Winter', 'Monsoon'])
    with col2:
        st.markdown("**Production Parameters**")
        production_kg = st.number_input("📦 Production (kg)", min_value=0.0, value=500.0)
        machine_runtime_hours = st.number_input("⏱️ Machine Runtime (hours)", min_value=0.0, value=8.0)
        electricity_kwh = st.number_input("⚡ Electricity Used (kWh)", min_value=0.0, value=300.0)
        water_liters = st.number_input("💧 Water Used (liters)", min_value=0.0, value=15000.0)
        dye_chemical_kg = st.number_input("🧪 Dye/Chemical Used (kg)", min_value=0.0, value=20.0)
        fuel_qty = st.number_input("🛢️ Fuel Quantity (kg coal / m³ gas)", min_value=0.0, value=100.0)

    st.write("")
    center = st.columns([1, 2, 1])
    with center[1]:
        predict_clicked = st.button("Predict CO2 Emissions", use_container_width=True)

    def generate_pdf_report(inputs, prediction):
        pdf = FPDF()
        pdf.add_page()
        pdf.set_font("Helvetica", "B", 16)
        pdf.set_text_color(46, 125, 50)
        pdf.cell(0, 12, "Carbon Emission Prediction Report", ln=True, align="C")
        pdf.set_draw_color(46, 125, 50)
        pdf.line(10, 22, 200, 22)
        pdf.ln(10)
        pdf.set_font("Helvetica", "B", 13)
        pdf.set_text_color(27, 94, 32)
        pdf.cell(0, 10, f"Estimated CO2 Emissions: {prediction:.2f} kg CO2e", ln=True)
        pdf.ln(5)
        pdf.set_font("Helvetica", "", 11)
        pdf.set_text_color(0, 0, 0)
        pdf.cell(0, 8, "Process Details:", ln=True)
        for key in ['fabric_type', 'dye_type', 'fuel_type', 'season']:
            pdf.cell(0, 7, f"  - {key.replace('_', ' ').title()}: {inputs[key]}", ln=True)
        pdf.ln(3)
        pdf.cell(0, 8, "Production Parameters:", ln=True)
        for key in ['production_kg', 'machine_runtime_hours', 'electricity_kwh',
                    'water_liters', 'dye_chemical_kg', 'fuel_qty']:
            pdf.cell(0, 7, f"  - {key.replace('_', ' ').title()}: {inputs[key]}", ln=True)
        pdf.ln(5)
        pdf.set_font("Helvetica", "I", 9)
        pdf.set_text_color(100, 100, 100)
        pdf.multi_cell(0, 6, "Generated by the Textile Carbon Emission Predictor. Model: Linear Regression (R2 = 0.991), trained on textile dyeing and finishing process data.")
        return bytes(pdf.output(dest="S"))

    if predict_clicked:
        input_dict = {
            'fabric_type': fabric_type, 'dye_type': dye_type, 'fuel_type': fuel_type, 'season': season,
            'production_kg': production_kg, 'machine_runtime_hours': machine_runtime_hours,
            'electricity_kwh': electricity_kwh, 'water_liters': water_liters,
            'dye_chemical_kg': dye_chemical_kg, 'fuel_qty': fuel_qty
        }
        input_df = pd.DataFrame([input_dict])

        with st.spinner("Calculating emissions..."):
            time.sleep(0.8)
            prediction = model.predict(input_df)[0]

        st.markdown(f"""
            <div class="result-box">
                <h2>{prediction:.2f} kg CO2e</h2>
                <p>Estimated Carbon Emission for this batch</p>
            </div>
        """, unsafe_allow_html=True)

        if prediction < 400:
            st.info("🟢 Low emission batch — efficient process.")
        elif prediction < 800:
            st.warning("🟡 Moderate emission batch — room for optimization.")
        else:
            st.error("🔴 High emission batch — consider fuel/energy efficiency improvements.")

        chart_col1, chart_col2 = st.columns(2)
        with chart_col1:
            st.markdown("#### How this compares")
            labels = ['Your\nPrediction', 'Dataset\nAverage', 'Dataset\nMin', 'Dataset\nMax']
            values = [prediction, DATASET_MEAN, DATASET_MIN, DATASET_MAX]
            colors = ['#2E7D32', '#B0BEC5', '#B0BEC5', '#B0BEC5']
            fig1, ax1 = plt.subplots(figsize=(5, 4))
            bars = ax1.bar(labels, values, color=colors)
            ax1.set_ylabel("CO2 Emissions (kg)")
            for bar in bars:
                height = bar.get_height()
                ax1.annotate(f'{height:.0f}', xy=(bar.get_x() + bar.get_width()/2, height),
                            xytext=(0, 3), textcoords="offset points", ha='center', fontsize=8)
            ax1.spines['top'].set_visible(False)
            ax1.spines['right'].set_visible(False)
            plt.tight_layout()
            st.pyplot(fig1)

        with chart_col2:
            st.markdown("#### Emission source breakdown")
            electricity_emissions = electricity_kwh * ELEC_EF
            fuel_ef = COAL_EF if fuel_type == 'Coal' else GAS_EF
            fuel_emissions = fuel_qty * fuel_ef
            pie_labels = ['Electricity', f'Fuel ({fuel_type})']
            pie_values = [electricity_emissions, fuel_emissions]
            pie_colors = ['#42A5F5', '#66BB6A']
            fig2, ax2 = plt.subplots(figsize=(5, 4))
            ax2.pie(pie_values, labels=pie_labels, autopct='%1.1f%%',
                    colors=pie_colors, startangle=90, textprops={'fontsize': 10})
            plt.tight_layout()
            st.pyplot(fig2)

        st.write("")
        pdf_bytes = generate_pdf_report(input_dict, prediction)
        dl_col = st.columns([1, 2, 1])
        with dl_col[1]:
            st.download_button(
                label="📄 Download PDF Report", data=pdf_bytes,
                file_name="carbon_emission_report.pdf", mime="application/pdf",
                use_container_width=True
            )

with tab2:
    st.markdown("### How It Works")
    s1, s2, s3, s4 = st.columns(4)
    steps = [
        ("1", "📥", "Enter Process Data", "Provide fabric type, fuel, production volume and energy usage."),
        ("2", "🤖", "Model Predicts", "A trained Linear Regression model estimates CO2 output instantly."),
        ("3", "📊", "Visual Comparison", "See how your result compares to dataset benchmarks."),
        ("4", "📄", "Export Report", "Download a PDF summary for records or presentations."),
    ]
    for col, (num, icon, title, desc) in zip([s1, s2, s3, s4], steps):
        with col:
            st.markdown(f"""
                <div class="step-card">
                    <div class="step-num">{num}</div>
                    <h4>{icon} {title}</h4>
                    <p style="font-size:13px;color:#555;">{desc}</p>
                </div>
            """, unsafe_allow_html=True)

with tab3:
    st.markdown("### About This Project")
    st.write(
        "Textile dyeing and finishing is one of the most energy-intensive stages "
        "of fabric manufacturing, consuming large amounts of electricity and thermal "
        "energy (steam/heat) for processing. This project uses a Machine Learning "
        "model trained on process-level data to estimate the carbon footprint of a "
        "production batch, helping manufacturers make more sustainable decisions."
    )
    st.markdown("**Model:** Linear Regression &nbsp;|&nbsp; **R² Score:** 0.991 &nbsp;|&nbsp; **MAE:** 15.38 kg CO2e")
    st.markdown("**Key drivers of emissions:** Fuel consumption (~66%) and Electricity usage (~26%)")

# ---------- Footer ----------
st.markdown("""
    <div class="footer-box">
        <p style="font-weight:600; color:#1B5E20;">🌍 Carbon Emission Predictor — Mini Project</p>
        <p style="font-size:13px; color:#777;">Built with Python, scikit-learn & Streamlit</p>
        <div class="footer-icons">
            <a href="#">🔗 GitHub</a>
            <a href="#">📧 Contact</a>
            <a href="#">📄 Report</a>
        </div>
    </div>
""", unsafe_allow_html=True)