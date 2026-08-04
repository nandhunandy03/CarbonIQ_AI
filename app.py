"""
Carbon Emission Predictor - Streamlit App
==========================================
Landing page (animated, green theme) -> Factory Login/Signup
(Factory ID + Email + Password) -> Profile page (factory info + ML predictor).

Run:
    pip install -r requirements.txt
    streamlit run app.py
"""

import streamlit as st
import sqlite3
import hashlib
import datetime

# ------------------------------------------------------------------
# 1. PAGE CONFIG (must be the first Streamlit command)
# ------------------------------------------------------------------
st.set_page_config(
    page_title="Carbon Emission Predictor",
    page_icon="🌍",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ------------------------------------------------------------------
# 2. DATABASE (SQLite - stores factories so logins persist)
# ------------------------------------------------------------------
DB_PATH = "factories.db"


def init_db():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute(
        """CREATE TABLE IF NOT EXISTS factories (
                factory_id     TEXT PRIMARY KEY,
                factory_name   TEXT,
                email          TEXT,
                password_hash  TEXT,
                created_at     TEXT
           )"""
    )
    conn.commit()
    conn.close()


def hash_password(password: str) -> str:
    return hashlib.sha256(password.encode()).hexdigest()


def register_factory(factory_id, factory_name, email, password, confirm_password):
    factory_id = factory_id.strip()
    email = email.strip()

    if not factory_id or not factory_name or not email or not password:
        return False, "⚠️ Please fill in all fields."
    if password != confirm_password:
        return False, "⚠️ Passwords do not match."
    if len(password) < 6:
        return False, "⚠️ Password must be at least 6 characters."

    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("SELECT factory_id FROM factories WHERE factory_id=?", (factory_id,))
    if c.fetchone():
        conn.close()
        return False, "⚠️ This Factory ID is already registered. Please log in instead."

    c.execute(
        "INSERT INTO factories VALUES (?,?,?,?,?)",
        (factory_id, factory_name, email, hash_password(password), str(datetime.date.today())),
    )
    conn.commit()
    conn.close()
    return True, "✅ Registration successful! Please switch to Login and sign in."


def verify_login(factory_id, email, password):
    factory_id = factory_id.strip()
    email = email.strip()

    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute(
        "SELECT factory_name, email, password_hash, created_at FROM factories WHERE factory_id=?",
        (factory_id,),
    )
    row = c.fetchone()
    conn.close()

    if not row:
        return False, None, "⚠️ Factory ID not found. Please sign up first."
    if row[1] != email:
        return False, None, "⚠️ Email does not match this Factory ID."
    if row[2] != hash_password(password):
        return False, None, "⚠️ Incorrect password."

    user = {
        "factory_id": factory_id,
        "factory_name": row[0],
        "email": row[1],
        "joined": row[3],
    }
    return True, user, "✅ Login successful!"


init_db()

# ------------------------------------------------------------------
# 3. YOUR ML MODEL — replace this with your actual trained model
# ------------------------------------------------------------------
# e.g. import joblib; model = joblib.load("carbon_model.pkl")

def predict_emission(fabric_type, dye_type, fuel_type, season,
                      production_kg, machine_hours, electricity_kwh, water_liters):
    """
    Placeholder logic. Swap this out for:
        features = preprocess(...)
        prediction = model.predict(features)
    """
    fuel_factor = {"Coal": 2.3, "Diesel": 1.9, "Natural Gas": 1.2, "Electric": 0.6}.get(fuel_type, 1.5)
    dye_factor = {"Reactive": 1.1, "Vat": 1.3, "Disperse": 1.0, "Acid": 0.9}.get(dye_type, 1.0)
    season_factor = {"Summer": 1.05, "Winter": 1.15, "Monsoon": 1.0}.get(season, 1.0)

    base = (electricity_kwh * 0.82) + (machine_hours * 12.5 * fuel_factor)
    base += (water_liters * 0.0003) + (production_kg * 0.15 * dye_factor)
    total_co2 = base * season_factor
    per_kg = total_co2 / production_kg if production_kg else 0

    return total_co2, per_kg


# ------------------------------------------------------------------
# 4. THEME CSS (green, professional, animated)
# ------------------------------------------------------------------
st.markdown(
    """
    <style>
    :root {
        --brand-green: #1e7d4f;
        --brand-green-light: #2fae76;
        --brand-dark: #103c26;
    }

    /* Hide default streamlit chrome for a cleaner landing feel */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}

    .block-container { padding-top: 2rem; max-width: 1100px; }

    /* ---------- Hero ---------- */
    .hero {
        text-align: center;
        padding: 55px 20px 35px 20px;
        border-radius: 20px;
        background: linear-gradient(120deg, #e9fbf1, #d5f3e3, #e9fbf1);
        background-size: 200% 200%;
        animation: gradientShift 8s ease infinite;
        margin-bottom: 25px;
    }
    @keyframes gradientShift {
        0% { background-position: 0% 50%; }
        50% { background-position: 100% 50%; }
        100% { background-position: 0% 50%; }
    }
    .hero-icon { font-size: 62px; animation: float 3s ease-in-out infinite; }
    @keyframes float {
        0%, 100% { transform: translateY(0px); }
        50% { transform: translateY(-12px); }
    }
    .hero h1 {
        font-size: 2.5rem; font-weight: 800; color: var(--brand-green);
        margin: 8px 0 4px 0; animation: fadeInUp 1s ease;
    }
    .hero p { color: #3c5c4c; font-size: 1.05rem; animation: fadeInUp 1.3s ease; }
    @keyframes fadeInUp {
        from { opacity: 0; transform: translateY(15px); }
        to   { opacity: 1; transform: translateY(0); }
    }

    /* ---------- Feature / info cards ---------- */
    .feature-card {
        background: white; border: 1px solid #e3f2ea; border-radius: 16px;
        padding: 18px; text-align: center; transition: all 0.25s ease;
        height: 100%;
    }
    .feature-card:hover {
        transform: translateY(-6px);
        box-shadow: 0 10px 24px rgba(30,125,79,0.15);
    }

    /* ---------- Buttons ---------- */
    div.stButton > button {
        border-radius: 10px !important;
        font-weight: 600 !important;
        transition: all 0.2s ease !important;
    }
    div.stButton > button[kind="primary"] {
        background: linear-gradient(90deg, var(--brand-green), var(--brand-green-light)) !important;
        border: none !important;
        color: white !important;
    }
    div.stButton > button[kind="primary"]:hover { transform: scale(1.02); }
    div.stButton > button[kind="secondary"] {
        border: 1px solid var(--brand-green-light) !important;
        color: var(--brand-green) !important;
        background: white !important;
    }
    div.stButton > button[kind="secondary"]:hover {
        background: var(--brand-green) !important;
        color: white !important;
    }

    /* ---------- Auth card ---------- */
    .auth-wrap { display: flex; justify-content: center; }
    .auth-card {
        max-width: 440px; width: 100%; margin: 10px auto; padding: 30px;
        border-radius: 18px; background: white; border: 1px solid #e3f2ea;
        box-shadow: 0 10px 30px rgba(16,60,38,0.08); animation: fadeInUp 0.6s ease;
    }

    /* ---------- Profile ---------- */
    .profile-card {
        background: linear-gradient(135deg, var(--brand-green), var(--brand-dark));
        color: white; border-radius: 18px; padding: 24px 28px;
        margin-bottom: 22px; animation: fadeInUp 0.6s ease;
    }
    .profile-card h2 { margin: 0 0 4px 0; }
    .profile-card p { margin: 2px 0; opacity: 0.9; }

    .result-card {
        background: #f2fbf6; border: 1px solid var(--brand-green-light);
        border-radius: 14px; padding: 20px; margin-top: 10px;
        animation: fadeInUp 0.5s ease;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# ------------------------------------------------------------------
# 5. SESSION STATE (controls which "page" is shown)
# ------------------------------------------------------------------
if "page" not in st.session_state:
    st.session_state.page = "landing"     # landing | auth | profile
if "auth_mode" not in st.session_state:
    st.session_state.auth_mode = "Login"  # Login | Sign Up
if "user" not in st.session_state:
    st.session_state.user = None
if "show_about" not in st.session_state:
    st.session_state.show_about = False
if "show_contact" not in st.session_state:
    st.session_state.show_contact = False


def go_to(page):
    st.session_state.page = page
    st.rerun()


# ==================================================================
# PAGE: LANDING
# ==================================================================
def render_landing():
    st.markdown(
        """
        <div class="hero">
            <div class="hero-icon">🌍</div>
            <h1>Carbon Emission Predictor</h1>
            <p>Textile Dyeing &amp; Finishing Process — ML-based CO₂ Emission Estimation</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    col1, col2, col3 = st.columns(3)
    with col1:
        if st.button("ℹ️ About", use_container_width=True, type="secondary"):
            st.session_state.show_about = not st.session_state.show_about
    with col2:
        if st.button("✉️ Contact Us", use_container_width=True, type="secondary"):
            st.session_state.show_contact = not st.session_state.show_contact
    with col3:
        if st.button("🚀 Get Started", use_container_width=True, type="primary"):
            go_to("auth")

    if st.session_state.show_about:
        st.info(
            "**About this project:** This tool uses a machine learning model "
            "trained on textile dyeing & finishing process data to estimate the "
            "carbon footprint (CO₂ emissions) of a production batch — based on "
            "fabric type, dye chemistry, fuel source, seasonal conditions, and "
            "resource consumption (electricity, water, machine runtime). Built "
            "to help textile factories track and reduce their environmental impact."
        )

    if st.session_state.show_contact:
        st.info(
            "**Contact us:** support@carbonpredictor.example  \n"
            "**Location:** Chennai, Tamil Nadu, India  \n"
            "For factory onboarding, sign up with your Factory ID on the login page."
        )

    st.markdown("### ✨ Why factories use this tool")
    c1, c2, c3 = st.columns(3)
    with c1:
        st.markdown(
            '<div class="feature-card"><h4>📊 Accurate Estimates</h4>'
            'ML-driven predictions from real process data</div>',
            unsafe_allow_html=True,
        )
    with c2:
        st.markdown(
            '<div class="feature-card"><h4>🏭 Factory Profiles</h4>'
            "Track every factory's emissions separately</div>",
            unsafe_allow_html=True,
        )
    with c3:
        st.markdown(
            '<div class="feature-card"><h4>🌿 Sustainability</h4>'
            'Spot high-impact steps and cut CO₂ output</div>',
            unsafe_allow_html=True,
        )


# ==================================================================
# PAGE: LOGIN / SIGNUP
# ==================================================================
def render_auth():
    st.markdown('<div class="auth-wrap">', unsafe_allow_html=True)
    st.markdown('<div class="auth-card">', unsafe_allow_html=True)

    st.markdown("## 🔐 Factory Login")
    st.session_state.auth_mode = st.radio(
        "", ["Login", "Sign Up"], horizontal=True,
        index=0 if st.session_state.auth_mode == "Login" else 1,
        label_visibility="collapsed",
    )

    if st.session_state.auth_mode == "Login":
        with st.form("login_form"):
            factory_id = st.text_input("🏭 Factory ID")
            email = st.text_input("📧 Email")
            password = st.text_input("🔑 Password", type="password")
            submitted = st.form_submit_button("Login", type="primary", use_container_width=True)

        if submitted:
            ok, user, msg = verify_login(factory_id, email, password)
            if ok:
                st.session_state.user = user
                go_to("profile")
            else:
                st.error(msg)

    else:  # Sign Up
        with st.form("signup_form"):
            factory_id = st.text_input("🏭 Factory ID (choose a unique ID)")
            factory_name = st.text_input("🏢 Factory Name")
            email = st.text_input("📧 Email")
            password = st.text_input("🔑 Password", type="password")
            confirm = st.text_input("🔑 Confirm Password", type="password")
            submitted = st.form_submit_button("Create Account", type="primary", use_container_width=True)

        if submitted:
            ok, msg = register_factory(factory_id, factory_name, email, password, confirm)
            if ok:
                st.success(msg)
                st.session_state.auth_mode = "Login"
            else:
                st.error(msg)

    st.markdown("</div>", unsafe_allow_html=True)  # auth-card
    st.markdown("</div>", unsafe_allow_html=True)  # auth-wrap

    if st.button("← Back to Home"):
        go_to("landing")


# ==================================================================
# PAGE: PROFILE / DASHBOARD
# ==================================================================
def render_profile():
    user = st.session_state.user
    if not user:
        go_to("landing")
        return

    st.markdown(
        f"""
        <div class="profile-card">
            <h2>👤 {user['factory_name']}</h2>
            <p><b>Factory ID:</b> {user['factory_id']}</p>
            <p><b>Email:</b> {user['email']}</p>
            <p><b>Member since:</b> {user['joined']}</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    top_l, top_r = st.columns([5, 1])
    with top_r:
        if st.button("Logout", use_container_width=True):
            st.session_state.user = None
            go_to("landing")

    st.markdown("## 🧪 Carbon Emission Prediction")
    col1, col2 = st.columns(2)

    with col1:
        st.markdown("### Process Details")
        fabric_type = st.selectbox("🧵 Fabric Type", ["Cotton", "Polyester", "Silk", "Wool", "Linen", "Viscose"])
        dye_type = st.selectbox("🎨 Dye Type", ["Reactive", "Vat", "Disperse", "Acid"])
        fuel_type = st.selectbox("🔥 Fuel Type", ["Coal", "Diesel", "Natural Gas", "Electric"])
        season = st.selectbox("🌦️ Season", ["Summer", "Winter", "Monsoon"])

    with col2:
        st.markdown("### Production Parameters")
        production_kg = st.number_input("📦 Production (kg)", min_value=0.0, value=500.0, step=10.0)
        machine_hours = st.number_input("⏱️ Machine Runtime (hours)", min_value=0.0, value=8.0, step=0.5)
        electricity_kwh = st.number_input("⚡ Electricity Used (kWh)", min_value=0.0, value=300.0, step=10.0)
        water_liters = st.number_input("💧 Water Used (liters)", min_value=0.0, value=15000.0, step=100.0)

    if st.button("Predict Emissions", type="primary", use_container_width=True):
        total_co2, per_kg = predict_emission(
            fabric_type, dye_type, fuel_type, season,
            production_kg, machine_hours, electricity_kwh, water_liters
        )
        st.markdown(
            f"""
            <div class="result-card">
                <h3>🌍 Estimated CO₂ Emissions</h3>
                <p><b>Total emissions:</b> {total_co2:,.2f} kg CO₂</p>
                <p><b>Emission intensity:</b> {per_kg:,.3f} kg CO₂ / kg fabric</p>
                <hr>
                <p style="color:#666;font-size:0.9rem;">
                    Fabric: {fabric_type} | Dye: {dye_type} | Fuel: {fuel_type} | Season: {season}
                </p>
            </div>
            """,
            unsafe_allow_html=True,
        )


# ------------------------------------------------------------------
# 6. ROUTER
# ------------------------------------------------------------------
if st.session_state.page == "landing":
    render_landing()
elif st.session_state.page == "auth":
    render_auth()
elif st.session_state.page == "profile":
    render_profile()