from flask import Flask, render_template, request, redirect, url_for, flash, session
import sqlite3
import pickle
import pandas as pd

app = Flask(__name__)
app.secret_key = "carboniq_secret_key"

#ML MODEL
model = pickle.load(open("model.pkl", "rb"))
encoder = pickle.load(open("encoder.pkl", "rb"))

# ---------- DATABASE ----------

def init_db():
    conn = sqlite3.connect("database.db")
    cursor = conn.cursor()

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS users(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT,
        email TEXT UNIQUE,
        password TEXT
    )
    """)
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS prediction_history(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        electricity REAL,
        fuel REAL,
        water REAL,
        production REAL,
        machine_hours REAL,
        fabric TEXT,
        carbon_emission REAL
    )
    """)


    conn.commit()
    conn.close()

init_db()

# ---------- HOME ----------

@app.route("/")
def home():
    return render_template("index.html")

# ---------- FEATURES ----------

@app.route("/features")
def features():
    return render_template("features.html")

# ---------- HOW IT WORKS ----------

@app.route("/how-it-works")
def how_it_works():
    return render_template("how_it_works.html")

# ---------- ABOUT ----------

@app.route("/about")
def about():
    return render_template("about.html")

# ---------- CONTACT ----------

@app.route("/contact")
def contact():
    return render_template("contact.html")

# ---------- SIGNUP ----------

@app.route("/signup", methods=["GET", "POST"])
def signup():

    if request.method == "POST":

        name = request.form["name"]
        email = request.form["email"]
        password = request.form["password"]

        conn = sqlite3.connect("database.db")
        cursor = conn.cursor()

        cursor.execute("SELECT * FROM users WHERE email=?", (email,))
        user = cursor.fetchone()

        if user:
            flash("Email already exists")
            conn.close()
            return redirect(url_for("signup"))

        cursor.execute(
            "INSERT INTO users(name,email,password) VALUES(?,?,?)",
            (name, email, password)
        )

        conn.commit()
        conn.close()

        flash("Registration Successful")
        return redirect(url_for("login"))

    return render_template("signup.html")

# ---------- LOGIN ----------

@app.route("/login", methods=["GET", "POST"])
def login():

    if request.method == "POST":

        email = request.form["email"]
        password = request.form["password"]

        conn = sqlite3.connect("database.db")
        cursor = conn.cursor()

        cursor.execute(
            "SELECT * FROM users WHERE email=? AND password=?",
            (email, password)
        )

        user = cursor.fetchone()
        conn.close()

        if user:
            session["user"] = user[1]
            return redirect(url_for("dashboard"))

        flash("Invalid Email or Password")
        return redirect(url_for("login"))

    return render_template("login.html")

# ---------- DASHBOARD ----------
@app.route("/dashboard")
def dashboard():

    # Login check
    if "user" not in session:
        return redirect(url_for("login"))

    conn = sqlite3.connect("database.db")
    cursor = conn.cursor()

    # -----------------------------
    # Fabric wise carbon emission
    # -----------------------------

    cursor.execute("""
        SELECT fabric, AVG(carbon_emission)
        FROM prediction_history
        GROUP BY fabric
    """)

    fabric_data = cursor.fetchall()

    fabrics = [row[0] for row in fabric_data]
    fabric_emissions = [round(float(row[1]), 2) for row in fabric_data]


    # -----------------------------
    # Production vs emission
    # -----------------------------

    cursor.execute("""
        SELECT production, carbon_emission
        FROM prediction_history
        ORDER BY id
    """)

    production_data = cursor.fetchall()

    production = [row[0] for row in production_data]
    production_emission = [row[1] for row in production_data]


    # -----------------------------
    # Electricity vs emission
    # -----------------------------

    cursor.execute("""
        SELECT electricity, carbon_emission
        FROM prediction_history
        ORDER BY id
    """)

    electricity_data = cursor.fetchall()

    electricity = [row[0] for row in electricity_data]
    electricity_emission = [row[1] for row in electricity_data]


    conn.close()


    # -----------------------------
    # Dashboard
    # -----------------------------

    return render_template(
        "dashboard.html",

        username=session["user"],

        fabrics=fabrics,
        fabric_emissions=fabric_emissions,

        production=production,
        production_emission=production_emission,

        electricity=electricity,
        electricity_emission=electricity_emission
    )

# ---------- SETTINGS ----------

@app.route("/settings")
def settings():

    if "user" not in session:
        return redirect(url_for("login"))

    return render_template("settings.html")

# ---------- LOGOUT ----------

@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("login"))

@app.route("/predict")
def predict():
    return render_template("predict.html")

# ---------- HISTORY ----------

@app.route("/history")
def history():

    if "user" not in session:
        return redirect(url_for("login"))

    conn = sqlite3.connect("database.db")
    conn.row_factory = sqlite3.Row

    cursor = conn.cursor()

    # All prediction records
    cursor.execute("""
        SELECT *
        FROM prediction_history
        ORDER BY id DESC
    """)

    records = cursor.fetchall()

    # Total predictions
    cursor.execute("""
        SELECT COUNT(*) AS total
        FROM prediction_history
    """)

    total = cursor.fetchone()["total"]

    # Average emission
    cursor.execute("""
        SELECT AVG(carbon_emission) AS average
        FROM prediction_history
    """)

    average = cursor.fetchone()["average"]

    # High emission records
    cursor.execute("""
        SELECT COUNT(*) AS high
        FROM prediction_history
        WHERE carbon_emission > 500
    """)

    high = cursor.fetchone()["high"]

    conn.close()

    return render_template(
        "history.html",
        records=records,
        total=total,
        average=round(average or 0, 1),
        high=high
    )


# ---------- HISTORY VIEW ----------

@app.route("/history/<int:prediction_id>")
def history_view(prediction_id):

    if "user" not in session:
        return redirect(url_for("login"))

    conn = sqlite3.connect("database.db")
    conn.row_factory = sqlite3.Row

    cursor = conn.cursor()

    cursor.execute("""
        SELECT *
        FROM prediction_history
        WHERE id = ?
    """, (prediction_id,))

    record = cursor.fetchone()

    conn.close()

    if record is None:
        return "Prediction record not found", 404

    return render_template(
        "history_view.html",
        record=record
    )

# ---------- REPORTS ----------

@app.route("/reports")
def reports():

    if "user" not in session:
        return redirect(url_for("login"))

    conn = sqlite3.connect("database.db")
    cursor = conn.cursor()

    # Total predictions
    cursor.execute("""
        SELECT COUNT(*)
        FROM prediction_history
    """)
    total_predictions = cursor.fetchone()[0]

    # Total emission
    cursor.execute("""
        SELECT COALESCE(SUM(carbon_emission), 0)
        FROM prediction_history
    """)
    total_emission = cursor.fetchone()[0]

    # Average emission
    cursor.execute("""
        SELECT COALESCE(AVG(carbon_emission), 0)
        FROM prediction_history
    """)
    average_emission = cursor.fetchone()[0]

    # Average emission by fabric
    cursor.execute("""
        SELECT fabric, AVG(carbon_emission)
        FROM prediction_history
        GROUP BY fabric
    """)

    fabric_data = cursor.fetchall()

    fabrics = [row[0] for row in fabric_data]
    fabric_emissions = [
        round(float(row[1]), 2)
        for row in fabric_data
    ]

    # Resource consumption
    cursor.execute("""
        SELECT
            COALESCE(SUM(electricity), 0),
            COALESCE(SUM(fuel), 0),
            COALESCE(SUM(water), 0)
        FROM prediction_history
    """)

    resource_data = cursor.fetchone()

    electricity_total = resource_data[0]
    fuel_total = resource_data[1]
    water_total = resource_data[2]

    conn.close()

    return render_template(
        "reports.html",

        username=session["user"],

        total_predictions=total_predictions,

        total_emission=round(float(total_emission), 2),

        average_emission=round(float(average_emission), 2),

        fabrics=fabrics,

        fabric_emissions=fabric_emissions,

        electricity_total=round(float(electricity_total), 2),

        fuel_total=round(float(fuel_total), 2),

        water_total=round(float(water_total), 2)
    )

@app.route("/result", methods=["POST"])
def result():

    electricity = float(request.form["electricity"])
    fuel = float(request.form["fuel"])
    water = float(request.form["water"])
    production = float(request.form["production"])
    machine_hours = float(request.form["machine_hours"])
    fabric = request.form["fabric"]

    # ML Prediction
    fabric_number = encoder.transform([fabric])[0]

    prediction = model.predict([[
        electricity,
        fuel,
        water,
        production,
        machine_hours,
        fabric_number
    ]])[0]

    prediction = round(float(prediction), 2)

    # -----------------------------
    # Feature Importance
    # -----------------------------

    feature_names = [
        "Electricity",
        "Fuel",
        "Water",
        "Production",
        "Machine Hours",
        "Fabric"
    ]

    importance = model.feature_importances_

    feature_importance = dict(
        zip(feature_names, importance)
    )

    highest_factor = max(
        feature_importance,
        key=feature_importance.get
    )

    highest_percentage = round(
        feature_importance[highest_factor] * 100,
        2
    )

    # -----------------------------
    # Save prediction
    # -----------------------------

    conn = sqlite3.connect("database.db")
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO prediction_history
        (electricity, fuel, water, production,
         machine_hours, fabric, carbon_emission)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (
        electricity,
        fuel,
        water,
        production,
        machine_hours,
        fabric,
        prediction
    ))

    conn.commit()
    conn.close()

    return render_template(
        "result.html",

        prediction=prediction,

        fabric=fabric,

        electricity=electricity,

        fuel=fuel,

        water=water,

        production=production,

        machine_hours=machine_hours,

        highest_factor=highest_factor,

        highest_percentage=highest_percentage
    )
# ---------- RUN ----------

if __name__ == "__main__":
    app.run(debug=True)