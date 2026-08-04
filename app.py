"""
CarbonIQ AI - Streamlit starter app
------------------------------------
HOW TO RUN:
1. Save this file as app.py
2. In terminal:  pip install streamlit plotly pandas numpy
3. Run:           streamlit run app.py

This is ONE file so you can see the whole flow at once. Once you understand
it, split it into the folder structure from the earlier guide if you want.
"""

import streamlit as st
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
import numpy as np
from datetime import datetime, timedelta

# ============================================================
# STEP 1: PAGE CONFIG + HIDE STREAMLIT DEFAULT UI
# This must be the very first Streamlit command in the file.
# ============================================================
st.set_page_config(page_title="CarbonIQ AI", page_icon="🌿", layout="wide")

st.markdown("""
<style>
/* Hide Streamlit's default menu, footer, header */
#MainMenu {visibility: hidden;}
footer {visibility: hidden;}
header {visibility: hidden;}

/* Import font + set base colors */
@import url('https://fonts.googleapis.com/css2?family=Poppins:wght@400;600;700;800&display=swap');
html, body, [class*="css"] { font-family: 'Poppins', sans-serif; }
.stApp { background-color: #F8FAFC; }

/* Reusable card style */
.kpi-card {
    background: white;
    border-radius: 20px;
    padding: 22px;
    box-shadow: 0 8px 30px rgba(6, 95, 70, 0.08);
    text-align: center;
    margin-bottom: 10px;
}
.kpi-value { font-size: 28px; font-weight: 700; color: #065F46; }
.kpi-label { font-size: 14px; color: #6B7280; margin-top: 4px; }

.hero-title { font-size: 48px; font-weight: 800; color: #065F46; line-height: 1.2; }
.hero-sub { font-size: 18px; color: #4B5563; margin: 16px 0 28px 0; }

/* Sidebar dark green */
[data-testid="stSidebar"] { background: linear-gradient(180deg, #065F46, #064E3B); }
[data-testid="stSidebar"] * { color: #E5F7EF !important; }
</style>
""", unsafe_allow_html=True)


# ============================================================
# STEP 2: SESSION STATE = "MEMORY" ACROSS RERUNS
# Streamlit reruns the whole script top-to-bottom every time
# you click something. session_state is how you remember
# which page the user is on, and whether they're logged in.
# ============================================================
if "page" not in st.session_state:
    st.session_state.page = "landing"
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

def go_to(page_name):
    """Call this instead of manually changing pages."""
    st.session_state.page = page_name
    st.rerun()


# ============================================================
# STEP 3: FAKE / DEMO DATA
# In a real app this comes from a database. For a hackathon
# demo, generate it once and keep it in session_state.
# ============================================================
if "history" not in st.session_state:
    dates = pd.date_range(end=datetime.today(), periods=30)
    st.session_state.history = pd.DataFrame({
        "date": dates,
        "co2": np.random.uniform(80, 150, size=30).round(1),
        "factory": np.random.choice(["Factory A", "Factory B", "Factory C"], size=30),
    })


# ============================================================
# STEP 4: A SIMPLE "AI MODEL"
# For the demo you don't need real ML - a weighted formula
# behaves the same way in a live demo and is 100% reliable.
# Swap this for a real trained sklearn model later if you want.
# ============================================================
def predict_co2(steam, electricity, water, chemicals, qty, efficiency):
    base = (steam * 0.9) + (electricity * 0.6) + (water * 0.3) + (chemicals * 1.2)
    scaled = base * (qty / 100)
    adjusted = scaled * (1 - (efficiency / 200))  # better efficiency = lower emissions
    confidence = min(97, 80 + efficiency / 10)
    return round(adjusted, 2), round(confidence, 1)


# ============================================================
# STEP 5: LANDING PAGE
# ============================================================
def landing_page():
    left, right = st.columns([1.1, 0.9])
    with left:
        st.markdown('<div class="hero-title">🌿 AI-Powered Carbon<br>Intelligence Platform</div>', unsafe_allow_html=True)
        st.markdown('<div class="hero-sub">Helping textile industries predict, analyze and reduce carbon emissions using Artificial Intelligence.</div>', unsafe_allow_html=True)
        c1, c2 = st.columns(2)
        if c1.button("Get Started", use_container_width=True):
            go_to("login")
        if c2.button("Login", use_container_width=True):
            go_to("login")

        st.write("")
        s1, s2, s3, s4 = st.columns(4)
        for col, val, label in [(s1, "96%", "Prediction Accuracy"), (s2, "150+", "Factories"),
                                 (s3, "35%", "Carbon Reduction"), (s4, "24/7", "AI Monitoring")]:
            col.markdown(f'<div class="kpi-card"><div class="kpi-value">{val}</div><div class="kpi-label">{label}</div></div>', unsafe_allow_html=True)

    with right:
        st.markdown('<div class="kpi-card">🏭 Factory · ☀️ Solar · 🌬️ Wind · 📊 AI Dashboard</div>', unsafe_allow_html=True)
        st.markdown('<div class="kpi-card">Today\'s CO₂: <b>112 kg</b> &nbsp;|&nbsp; Sustainability Score: <b>82/100</b></div>', unsafe_allow_html=True)


# ============================================================
# STEP 6: LOGIN PAGE
# ============================================================
def login_page():
    _, mid, _ = st.columns([1, 1.2, 1])
    with mid:
        st.markdown('<div class="kpi-card">', unsafe_allow_html=True)
        st.markdown("### 🌿 CarbonIQ AI — Login")
        email = st.text_input("Email")
        password = st.text_input("Password", type="password")
        st.checkbox("Remember Me")
        if st.button("Login", use_container_width=True):
            # DEMO ONLY: accept any non-empty input.
            # Replace with real auth (DB check / Firebase / etc.) later.
            if email and password:
                st.session_state.logged_in = True
                go_to("dashboard")
            else:
                st.error("Enter email and password")
        st.markdown('</div>', unsafe_allow_html=True)


# ============================================================
# STEP 7: SIDEBAR (shown only after login)
# ============================================================
def sidebar():
    with st.sidebar:
        st.markdown("## 🌿 CarbonIQ AI")
        pages = {
            "dashboard": "📊 Dashboard",
            "prediction": "🤖 AI Prediction",
            "analytics": "📈 Analytics",
            "recommendations": "💡 AI Recommendations",
            "reports": "📄 Reports",
            "about": "ℹ️ About",
        }
        for key, label in pages.items():
            if st.button(label, use_container_width=True, key=f"nav_{key}"):
                go_to(key)
        st.markdown("---")
        if st.button("🚪 Logout", use_container_width=True):
            st.session_state.logged_in = False
            go_to("landing")


# ============================================================
# STEP 8: DASHBOARD
# ============================================================
def dashboard_page():
    st.markdown("## Dashboard")
    df = st.session_state.history

    kpis = [("Total CO₂", f"{df['co2'].sum():.0f} kg"), ("Today's Emission", f"{df['co2'].iloc[-1]} kg"),
            ("Prediction Accuracy", "96.2%"), ("Carbon Score", "82/100"),
            ("Sustainability Rating", "A-"), ("Factory Efficiency", "88%")]
    cols = st.columns(6)
    for col, (label, val) in zip(cols, kpis):
        col.markdown(f'<div class="kpi-card"><div class="kpi-value">{val}</div><div class="kpi-label">{label}</div></div>', unsafe_allow_html=True)

    c1, c2 = st.columns(2)
    with c1:
        fig = px.line(df, x="date", y="co2", title="CO₂ Trend", template="plotly_white",
                       color_discrete_sequence=["#16A34A"])
        st.plotly_chart(fig, use_container_width=True)
    with c2:
        by_factory = df.groupby("factory")["co2"].sum().reset_index()
        fig = px.bar(by_factory, x="factory", y="co2", title="Emissions by Factory",
                      template="plotly_white", color_discrete_sequence=["#10B981"])
        st.plotly_chart(fig, use_container_width=True)

    c3, c4 = st.columns(2)
    with c3:
        fig = px.pie(names=["Steam", "Electricity", "Water", "Chemicals"], values=[35, 30, 15, 20],
                      title="Emission Source Breakdown", color_discrete_sequence=px.colors.sequential.Greens_r)
        st.plotly_chart(fig, use_container_width=True)
    with c4:
        fig = go.Figure(go.Indicator(
            mode="gauge+number", value=82, title={"text": "Sustainability Score"},
            gauge={"axis": {"range": [0, 100]}, "bar": {"color": "#16A34A"}}))
        st.plotly_chart(fig, use_container_width=True)

    st.markdown("### Recent Predictions")
    st.dataframe(df.tail(5), use_container_width=True)


# ============================================================
# STEP 9: AI PREDICTION PAGE
# ============================================================
def prediction_page():
    st.markdown("## AI Prediction")
    c1, c2 = st.columns(2)
    with c1:
        factory = st.text_input("Factory Name", "Factory A")
        qty = st.number_input("Production Quantity", 1, 10000, 500)
        steam = st.number_input("Steam", 0.0, 1000.0, 50.0)
        electricity = st.number_input("Electricity", 0.0, 1000.0, 60.0)
    with c2:
        water = st.number_input("Water", 0.0, 1000.0, 40.0)
        chemicals = st.number_input("Chemicals", 0.0, 1000.0, 20.0)
        fabric_weight = st.number_input("Fabric Weight", 0.0, 1000.0, 100.0)
        efficiency = st.slider("Machine Efficiency (%)", 0, 100, 75)

    if st.button("🔮 Predict", use_container_width=True):
        co2, confidence = predict_co2(steam, electricity, water, chemicals, qty, efficiency)
        category = "Low" if co2 < 100 else "Medium" if co2 < 200 else "High"
        risk_color = {"Low": "🟢", "Medium": "🟡", "High": "🔴"}[category]

        st.markdown(f"""
        <div class="kpi-card">
        <h3>Prediction Result — {factory}</h3>
        <p><b>Predicted CO₂:</b> {co2} kg</p>
        <p><b>Confidence Score:</b> {confidence}%</p>
        <p><b>Emission Category:</b> {category} {risk_color}</p>
        <p><b>Estimated Cost:</b> ${co2 * 0.45:.2f}</p>
        <p><b>Carbon Risk:</b> {risk_color} {category}</p>
        </div>
        """, unsafe_allow_html=True)

        # add to history so Dashboard/Reports reflect it
        new_row = pd.DataFrame([{"date": datetime.today(), "co2": co2, "factory": factory}])
        st.session_state.history = pd.concat([st.session_state.history, new_row], ignore_index=True)


# ============================================================
# STEP 10: ANALYTICS PAGE
# ============================================================
def analytics_page():
    st.markdown("## Analytics")
    df = st.session_state.history
    c1, c2 = st.columns(2)
    with c1:
        fig = px.area(df, x="date", y="co2", title="Monthly Trend", template="plotly_white",
                       color_discrete_sequence=["#16A34A"])
        st.plotly_chart(fig, use_container_width=True)
    with c2:
        fig = px.imshow(np.random.rand(5, 5), title="Factory Heat Map",
                         color_continuous_scale="Greens")
        st.plotly_chart(fig, use_container_width=True)

    fig = go.Figure()
    categories = ["Steam", "Electricity", "Water", "Chemicals", "Efficiency"]
    fig.add_trace(go.Scatterpolar(r=[70, 60, 50, 65, 80], theta=categories, fill="toself", name="Factory A"))
    fig.update_layout(title="Factory Comparison (Radar)", template="plotly_white")
    st.plotly_chart(fig, use_container_width=True)


# ============================================================
# STEP 11: RECOMMENDATIONS PAGE
# ============================================================
def recommendations_page():
    st.markdown("## AI Recommendations")
    recs = [
        ("Reduce Steam Usage", "12%", "$420/mo", "High"),
        ("Recycle Water", "8%", "$180/mo", "Medium"),
        ("Optimize Electricity", "15%", "$560/mo", "High"),
        ("Improve Machine Efficiency", "10%", "$300/mo", "Medium"),
        ("Switch to Renewable Energy", "25%", "$900/mo", "High"),
    ]
    cols = st.columns(3)
    for i, (title, reduction, savings, priority) in enumerate(recs):
        with cols[i % 3]:
            st.markdown(f"""
            <div class="kpi-card">
            <h4>{title}</h4>
            <p>Estimated Reduction: <b>{reduction}</b></p>
            <p>Monthly Savings: <b>{savings}</b></p>
            <p>Priority: <b>{priority}</b></p>
            </div>
            """, unsafe_allow_html=True)


# ============================================================
# STEP 12: REPORTS PAGE (CSV export shown; Excel/PDF same idea)
# ============================================================
def reports_page():
    st.markdown("## Reports")
    df = st.session_state.history
    st.dataframe(df, use_container_width=True)

    csv = df.to_csv(index=False).encode("utf-8")
    st.download_button("⬇️ Download CSV", data=csv, file_name="carboniq_report.csv", mime="text/csv")

    st.caption("For Excel: use `df.to_excel()` into a BytesIO buffer with openpyxl. "
               "For PDF: build the report with fpdf2 and download the bytes the same way.")


# ============================================================
# STEP 13: ABOUT PAGE
# ============================================================
def about_page():
    st.markdown("## About CarbonIQ AI")
    st.markdown("""
    <div class="kpi-card">
    <p><b>Mission:</b> Help textile factories cut carbon emissions using AI.</p>
    <p><b>Tech Stack:</b> Streamlit, Plotly, scikit-learn, Python.</p>
    <p><b>Future Scope:</b> Real IoT sensor integration, live factory data feeds.</p>
    </div>
    """, unsafe_allow_html=True)


# ============================================================
# STEP 14: ROUTER — decides what to show based on session_state
# This is the last thing that runs each time the script executes.
# ============================================================
if not st.session_state.logged_in:
    if st.session_state.page == "login":
        login_page()
    else:
        landing_page()
else:
    sidebar()
    page = st.session_state.page
    if page == "dashboard":
        dashboard_page()
    elif page == "prediction":
        prediction_page()
    elif page == "analytics":
        analytics_page()
    elif page == "recommendations":
        recommendations_page()
    elif page == "reports":
        reports_page()
    elif page == "about":
        about_page()
    else:
        dashboard_page()