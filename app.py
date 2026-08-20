from flask import Flask, render_template, request, redirect, url_for, flash, session
import sqlite3
import pickle
import hashlib
import json
from datetime import datetime

app = Flask(__name__)
app.secret_key = "carboniq_secret_key"


# ============================================================
# ML MODEL
# ============================================================

model = pickle.load(open("model.pkl", "rb"))
encoder = pickle.load(open("encoder.pkl", "rb"))


# ============================================================
# DATABASE
# ============================================================

def get_db():

    conn = sqlite3.connect("database.db")
    conn.row_factory = sqlite3.Row

    return conn


def init_db():

    conn = get_db()
    cursor = conn.cursor()

    # USERS
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT,
            email TEXT UNIQUE,
            password TEXT
        )
    """)

    # PREDICTIONS
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

    # BLOCKCHAIN
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS blockchain_blocks(

            id INTEGER PRIMARY KEY AUTOINCREMENT,

            block_index INTEGER UNIQUE,

            prediction_id INTEGER UNIQUE,

            timestamp TEXT,

            data TEXT,

            previous_hash TEXT,

            hash TEXT
        )
    """)

    conn.commit()
    conn.close()


init_db()


# ============================================================
# BLOCKCHAIN CLASS
# ============================================================

class Blockchain:

    # --------------------------------------------------------
    # HASH
    # --------------------------------------------------------

    def calculate_hash(self, block_data):

        block_string = json.dumps(
            block_data,
            sort_keys=True
        ).encode()

        return hashlib.sha256(
            block_string
        ).hexdigest()


    # --------------------------------------------------------
    # GENESIS BLOCK
    # --------------------------------------------------------

    def create_genesis_block(self):

        conn = get_db()
        cursor = conn.cursor()

        cursor.execute("""
            SELECT *
            FROM blockchain_blocks
            WHERE block_index = 0
        """)

        existing = cursor.fetchone()

        if existing:

            conn.close()
            return


        timestamp = datetime.now().isoformat()

        data = {
            "message": "CarbonIQ Blockchain Genesis Block"
        }


        block_data = {

            "block_index": 0,

            "prediction_id": None,

            "timestamp": timestamp,

            "data": data,

            "previous_hash": "0"
        }


        block_hash = self.calculate_hash(
            block_data
        )


        cursor.execute("""
            INSERT INTO blockchain_blocks
            (
                block_index,
                prediction_id,
                timestamp,
                data,
                previous_hash,
                hash
            )
            VALUES (?, ?, ?, ?, ?, ?)
        """, (

            0,

            None,

            timestamp,

            json.dumps(data),

            "0",

            block_hash

        ))


        conn.commit()
        conn.close()


    # --------------------------------------------------------
    # ADD PREDICTION BLOCK
    # --------------------------------------------------------

    def add_prediction_block(
        self,
        prediction_id,
        prediction_data
    ):

        conn = get_db()
        cursor = conn.cursor()


        # Check duplicate
        cursor.execute("""
            SELECT *
            FROM blockchain_blocks
            WHERE prediction_id = ?
        """, (prediction_id,))

        existing = cursor.fetchone()


        if existing:

            conn.close()

            return existing["hash"]


        # Previous block
        cursor.execute("""
            SELECT *
            FROM blockchain_blocks
            ORDER BY block_index DESC
            LIMIT 1
        """)

        previous_block = cursor.fetchone()


        if previous_block:

            previous_hash = previous_block["hash"]

            next_index = (
                previous_block["block_index"] + 1
            )

        else:

            previous_hash = "0"

            next_index = 0


        timestamp = datetime.now().isoformat()


        block_data = {

            "block_index": next_index,

            "prediction_id": prediction_id,

            "timestamp": timestamp,

            "data": prediction_data,

            "previous_hash": previous_hash

        }


        block_hash = self.calculate_hash(
            block_data
        )


        cursor.execute("""
            INSERT INTO blockchain_blocks
            (
                block_index,
                prediction_id,
                timestamp,
                data,
                previous_hash,
                hash
            )
            VALUES (?, ?, ?, ?, ?, ?)
        """, (

            next_index,

            prediction_id,

            timestamp,

            json.dumps(prediction_data),

            previous_hash,

            block_hash

        ))


        conn.commit()
        conn.close()


        return block_hash


    # --------------------------------------------------------
    # VERIFY BLOCKCHAIN
    # --------------------------------------------------------

    def verify_chain(self):

        conn = get_db()
        cursor = conn.cursor()

        cursor.execute("""
            SELECT *
            FROM blockchain_blocks
            ORDER BY block_index ASC
        """)

        blocks = cursor.fetchall()

        conn.close()


        if not blocks:

            return False


        for i, block in enumerate(blocks):

            data = json.loads(
                block["data"]
            )


            block_data = {

                "block_index":
                    block["block_index"],

                "prediction_id":
                    block["prediction_id"],

                "timestamp":
                    block["timestamp"],

                "data":
                    data,

                "previous_hash":
                    block["previous_hash"]
            }


            calculated_hash = self.calculate_hash(
                block_data
            )


            # Check hash
            if calculated_hash != block["hash"]:

                return False


            # Check previous hash
            if i > 0:

                previous_block = blocks[i - 1]

                if (
                    block["previous_hash"]
                    != previous_block["hash"]
                ):

                    return False


        return True


    # --------------------------------------------------------
    # BLOCK COUNT
    # --------------------------------------------------------

    def get_block_count(self):

        conn = get_db()
        cursor = conn.cursor()

        cursor.execute("""
            SELECT COUNT(*)
            FROM blockchain_blocks
            WHERE block_index > 0
        """)

        count = cursor.fetchone()[0]

        conn.close()

        return count


    # --------------------------------------------------------
    # LATEST BLOCK
    # --------------------------------------------------------

    def get_latest_block(self):

        conn = get_db()
        cursor = conn.cursor()

        cursor.execute("""
            SELECT *
            FROM blockchain_blocks
            ORDER BY block_index DESC
            LIMIT 1
        """)

        block = cursor.fetchone()

        conn.close()

        return block


# ============================================================
# CREATE BLOCKCHAIN
# ============================================================

blockchain = Blockchain()

blockchain.create_genesis_block()


# ============================================================
# SYNC OLD PREDICTIONS
# ============================================================

def sync_existing_predictions():

    conn = get_db()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT *
        FROM prediction_history
        ORDER BY id ASC
    """)

    predictions = cursor.fetchall()

    conn.close()


    for prediction in predictions:

        prediction_data = {

            "electricity":
                prediction["electricity"],

            "fuel":
                prediction["fuel"],

            "water":
                prediction["water"],

            "production":
                prediction["production"],

            "machine_hours":
                prediction["machine_hours"],

            "fabric":
                prediction["fabric"],

            "carbon_emission":
                prediction["carbon_emission"]
        }


        blockchain.add_prediction_block(

            prediction["id"],

            prediction_data

        )


sync_existing_predictions()


# ============================================================
# HOME
# ============================================================

@app.route("/")
def home():

    return render_template(
        "index.html"
    )


# ============================================================
# FEATURES
# ============================================================

@app.route("/features")
def features():

    return render_template(
        "features.html"
    )


# ============================================================
# HOW IT WORKS
# ============================================================

@app.route("/how-it-works")
def how_it_works():

    return render_template(
        "how_it_works.html"
    )


# ============================================================
# ABOUT
# ============================================================

@app.route("/about")
def about():

    return render_template(
        "about.html"
    )


# ============================================================
# CONTACT
# ============================================================

@app.route("/contact")
def contact():

    return render_template(
        "contact.html"
    )


# ============================================================
# SIGNUP
# ============================================================

@app.route(
    "/signup",
    methods=["GET", "POST"]
)
def signup():

    if request.method == "POST":

        name = request.form["name"]

        email = request.form["email"]

        password = request.form["password"]


        conn = get_db()
        cursor = conn.cursor()


        cursor.execute("""
            SELECT *
            FROM users
            WHERE email = ?
        """, (email,))


        user = cursor.fetchone()


        if user:

            flash(
                "Email already exists"
            )

            conn.close()

            return redirect(
                url_for("signup")
            )


        cursor.execute("""
            INSERT INTO users
            (name, email, password)
            VALUES (?, ?, ?)
        """, (

            name,
            email,
            password

        ))


        conn.commit()
        conn.close()


        flash(
            "Registration Successful"
        )


        return redirect(
            url_for("login")
        )


    return render_template(
        "signup.html"
    )


# ============================================================
# LOGIN
# ============================================================

@app.route(
    "/login",
    methods=["GET", "POST"]
)
def login():

    if request.method == "POST":

        email = request.form["email"]

        password = request.form["password"]


        conn = get_db()
        cursor = conn.cursor()


        cursor.execute("""
            SELECT *
            FROM users
            WHERE email = ?
            AND password = ?
        """, (

            email,
            password

        ))


        user = cursor.fetchone()

        conn.close()


        if user:

            session["user"] = user["name"]

            return redirect(
                url_for("dashboard")
            )


        flash(
            "Invalid Email or Password"
        )


        return redirect(
            url_for("login")
        )


    return render_template(
        "login.html"
    )


# ============================================================
# DASHBOARD
# ============================================================

@app.route("/dashboard")
def dashboard():

    if "user" not in session:

        return redirect(
            url_for("login")
        )


    conn = get_db()
    cursor = conn.cursor()


    # --------------------------------------------------------
    # TOTAL PREDICTIONS
    # --------------------------------------------------------

    cursor.execute("""
        SELECT COUNT(*)
        FROM prediction_history
    """)

    total_predictions = cursor.fetchone()[0]


    # --------------------------------------------------------
    # TOTAL EMISSION
    # --------------------------------------------------------

    cursor.execute("""
        SELECT COALESCE(
            SUM(carbon_emission), 0
        )
        FROM prediction_history
    """)

    total_emission = cursor.fetchone()[0]


    # --------------------------------------------------------
    # AVERAGE EMISSION
    # --------------------------------------------------------

    cursor.execute("""
        SELECT COALESCE(
            AVG(carbon_emission), 0
        )
        FROM prediction_history
    """)

    average_emission = cursor.fetchone()[0]


    # --------------------------------------------------------
    # HIGH EMISSION ALERTS
    # --------------------------------------------------------

    cursor.execute("""
        SELECT COUNT(*)
        FROM prediction_history
        WHERE carbon_emission > 500
    """)

    alert_count = cursor.fetchone()[0]


    # --------------------------------------------------------
    # CARBON SCORE
    # --------------------------------------------------------

    if average_emission <= 100:

        carbon_score = 95

    elif average_emission <= 200:

        carbon_score = 90

    elif average_emission <= 300:

        carbon_score = 80

    elif average_emission <= 500:

        carbon_score = 70

    else:

        carbon_score = 60


    # --------------------------------------------------------
    # FABRIC DATA
    # --------------------------------------------------------

    cursor.execute("""
        SELECT
            fabric,
            AVG(carbon_emission) AS avg_emission
        FROM prediction_history
        GROUP BY fabric
    """)

    fabric_data = cursor.fetchall()


    fabrics = [
        row["fabric"]
        for row in fabric_data
    ]


    fabric_emissions = [
        round(
            float(row["avg_emission"]),
            2
        )
        for row in fabric_data
    ]


    # --------------------------------------------------------
    # EMISSION TREND
    # --------------------------------------------------------

    cursor.execute("""
        SELECT
            id,
            carbon_emission
        FROM prediction_history
        ORDER BY id ASC
    """)

    trend_data = cursor.fetchall()


    prediction_labels = [

        "Prediction " + str(row["id"])

        for row in trend_data

    ]


    emission_values = [

        float(row["carbon_emission"])

        for row in trend_data

    ]


    # --------------------------------------------------------
    # RESOURCE CONSUMPTION
    # --------------------------------------------------------

    cursor.execute("""
        SELECT

            COALESCE(SUM(electricity), 0),

            COALESCE(SUM(fuel), 0),

            COALESCE(SUM(water), 0)

        FROM prediction_history
    """)


    resource_data = cursor.fetchone()


    electricity_total = float(
        resource_data[0]
    )

    fuel_total = float(
        resource_data[1]
    )

    water_total = float(
        resource_data[2]
    )


    resource_total = (
        electricity_total
        + fuel_total
        + water_total
    )


    if resource_total > 0:

        electricity_percent = round(
            electricity_total
            / resource_total
            * 100,
            1
        )

        fuel_percent = round(
            fuel_total
            / resource_total
            * 100,
            1
        )

        water_percent = round(
            water_total
            / resource_total
            * 100,
            1
        )

    else:

        electricity_percent = 0
        fuel_percent = 0
        water_percent = 0


    # --------------------------------------------------------
    # BLOCKCHAIN DATA
    # --------------------------------------------------------

    cursor.execute("""
        SELECT *
        FROM blockchain_blocks
        ORDER BY block_index DESC
    """)


    blockchain_records = cursor.fetchall()


    conn.close()


    blockchain_blocks = (
        blockchain.get_block_count()
    )


    blockchain_verified = (
        blockchain.verify_chain()
    )


    latest_block = (
        blockchain.get_latest_block()
    )


    if latest_block:

        latest_hash = latest_block["hash"]

    else:

        latest_hash = "N/A"


    if blockchain_verified:

        blockchain_status = (
            "Blockchain Verified"
        )

    else:

        blockchain_status = (
            "Verification Failed"
        )


    # --------------------------------------------------------
    # DASHBOARD
    # --------------------------------------------------------

    return render_template(

        "dashboard.html",

        username=session["user"],

        total_predictions=total_predictions,

        total_emission=round(
            float(total_emission),
            2
        ),

        average_emission=round(
            float(average_emission),
            2
        ),

        carbon_score=carbon_score,

        energy_optimized=15.6,

        alert_count=alert_count,


        fabrics=fabrics,

        fabric_emissions=fabric_emissions,


        prediction_labels=prediction_labels,

        emission_values=emission_values,


        electricity_total=round(
            electricity_total,
            2
        ),

        fuel_total=round(
            fuel_total,
            2
        ),

        water_total=round(
            water_total,
            2
        ),


        electricity_percent=
            electricity_percent,

        fuel_percent=
            fuel_percent,

        water_percent=
            water_percent,


        blockchain_records=
            blockchain_records,

        blockchain_blocks=
            blockchain_blocks,

        blockchain_verified=
            blockchain_verified,

        blockchain_status=
            blockchain_status,

        latest_hash=
            latest_hash

    )


# ============================================================
# SETTINGS
# ============================================================

@app.route('/settings')
def settings():

    if "user" not in session:
        return redirect(url_for("login"))

    conn = get_db()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT *
        FROM users
        WHERE name = ?
    """, (session["user"],))

    user = cursor.fetchone()
    conn.close()

    return render_template(
        "settings.html",
        user_name=user["name"],
        user_email=user["email"]
    )


@app.route('/settings/profile', methods=['POST'])
def update_profile():

    if "user" not in session:
        return redirect(url_for("login"))

    full_name = request.form.get("full_name")
    email = request.form.get("email")

    conn = get_db()
    cursor = conn.cursor()

    cursor.execute("""
        UPDATE users
        SET name = ?, email = ?
        WHERE name = ?
    """, (full_name, email, session["user"]))

    conn.commit()
    conn.close()

    session["user"] = full_name

    flash("Profile updated successfully")

    return redirect(url_for("settings"))

# ============================================================
# LOGOUT
# ============================================================

@app.route("/logout")
def logout():

    session.clear()

    return redirect(
        url_for("login")
    )


# ============================================================
# PREDICTION PAGE
# ============================================================

@app.route("/predict")
def predict():

    if "user" not in session:

        return redirect(
            url_for("login")
        )

    return render_template(
        "predict.html"
    )


# ============================================================
# HISTORY
# ============================================================

@app.route("/history")
def history():

    if "user" not in session:

        return redirect(
            url_for("login")
        )


    conn = get_db()
    cursor = conn.cursor()


    cursor.execute("""
        SELECT *
        FROM prediction_history
        ORDER BY id DESC
    """)


    records = cursor.fetchall()


    cursor.execute("""
        SELECT COUNT(*) AS total
        FROM prediction_history
    """)


    total = cursor.fetchone()["total"]


    cursor.execute("""
        SELECT AVG(carbon_emission) AS average
        FROM prediction_history
    """)


    average = cursor.fetchone()["average"]


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

        average=round(
            average or 0,
            1
        ),

        high=high

    )


# ============================================================
# HISTORY VIEW
# ============================================================

@app.route(
    "/history/<int:prediction_id>"
)
def history_view(prediction_id):

    if "user" not in session:

        return redirect(
            url_for("login")
        )


    conn = get_db()
    cursor = conn.cursor()


    cursor.execute("""
        SELECT *
        FROM prediction_history
        WHERE id = ?
    """, (prediction_id,))


    record = cursor.fetchone()

    conn.close()


    if record is None:

        return (
            "Prediction record not found",
            404
        )


    return render_template(

        "history_view.html",

        record=record

    )


# ============================================================
# REPORTS
# ============================================================

@app.route("/reports")
def reports():

    if "user" not in session:

        return redirect(
            url_for("login")
        )


    conn = get_db()
    cursor = conn.cursor()


    cursor.execute("""
        SELECT COUNT(*)
        FROM prediction_history
    """)

    total_predictions = (
        cursor.fetchone()[0]
    )


    cursor.execute("""
        SELECT COALESCE(
            SUM(carbon_emission), 0
        )
        FROM prediction_history
    """)

    total_emission = (
        cursor.fetchone()[0]
    )


    cursor.execute("""
        SELECT COALESCE(
            AVG(carbon_emission), 0
        )
        FROM prediction_history
    """)

    average_emission = (
        cursor.fetchone()[0]
    )


    cursor.execute("""
        SELECT
            fabric,
            AVG(carbon_emission) AS avg_emission
        FROM prediction_history
        GROUP BY fabric
    """)


    fabric_data = cursor.fetchall()


    fabrics = [
        row["fabric"]
        for row in fabric_data
    ]


    fabric_emissions = [

        round(
            float(row["avg_emission"]),
            2
        )

        for row in fabric_data

    ]


    cursor.execute("""
        SELECT

            COALESCE(SUM(electricity), 0),

            COALESCE(SUM(fuel), 0),

            COALESCE(SUM(water), 0)

        FROM prediction_history
    """)


    resource_data = cursor.fetchone()


    conn.close()


    return render_template(

        "reports.html",

        username=session["user"],

        total_predictions=
            total_predictions,

        total_emission=
            round(
                float(total_emission),
                2
            ),

        average_emission=
            round(
                float(average_emission),
                2
            ),

        fabrics=fabrics,

        fabric_emissions=
            fabric_emissions,

        electricity_total=
            round(
                float(resource_data[0]),
                2
            ),

        fuel_total=
            round(
                float(resource_data[1]),
                2
            ),

        water_total=
            round(
                float(resource_data[2]),
                2
            )

    )


# ============================================================
# RESULT / ML PREDICTION
# ============================================================

@app.route(
    "/result",
    methods=["POST"]
)
def result():

    if "user" not in session:

        return redirect(
            url_for("login")
        )


    electricity = float(
        request.form["electricity"]
    )

    fuel = float(
        request.form["fuel"]
    )

    water = float(
        request.form["water"]
    )

    production = float(
        request.form["production"]
    )

    machine_hours = float(
        request.form["machine_hours"]
    )

    fabric = request.form["fabric"]


    # --------------------------------------------------------
    # ML
    # --------------------------------------------------------

    fabric_number = encoder.transform(
        [fabric]
    )[0]


    prediction = model.predict([

        [

            electricity,

            fuel,

            water,

            production,

            machine_hours,

            fabric_number

        ]

    ])[0]


    prediction = round(
        float(prediction),
        2
    )


    # --------------------------------------------------------
    # FEATURE IMPORTANCE
    # --------------------------------------------------------

    feature_names = [

        "Electricity",

        "Fuel",

        "Water",

        "Production",

        "Machine Hours",

        "Fabric"

    ]


    if hasattr(
        model,
        "feature_importances_"
    ):

        importance = (
            model.feature_importances_
        )

        feature_importance = dict(
            zip(
                feature_names,
                importance
            )
        )

        highest_factor = max(
            feature_importance,
            key=feature_importance.get
        )

        highest_percentage = round(

            feature_importance[
                highest_factor
            ] * 100,

            2

        )

    else:

        highest_factor = (
            "Electricity"
        )

        highest_percentage = 0


    # --------------------------------------------------------
    # SAVE PREDICTION
    # --------------------------------------------------------

    conn = get_db()
    cursor = conn.cursor()


    cursor.execute("""
        INSERT INTO prediction_history
        (
            electricity,
            fuel,
            water,
            production,
            machine_hours,
            fabric,
            carbon_emission
        )
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


    prediction_id = cursor.lastrowid


    conn.commit()
    conn.close()


    # --------------------------------------------------------
    # BLOCKCHAIN
    # --------------------------------------------------------

    prediction_data = {

        "electricity":
            electricity,

        "fuel":
            fuel,

        "water":
            water,

        "production":
            production,

        "machine_hours":
            machine_hours,

        "fabric":
            fabric,

        "carbon_emission":
            prediction
    }


    blockchain_hash = (
        blockchain.add_prediction_block(

            prediction_id,

            prediction_data

        )
    )


    # --------------------------------------------------------
    # RESULT
    # --------------------------------------------------------

    return render_template(

        "result.html",

        prediction=prediction,

        fabric=fabric,

        electricity=electricity,

        fuel=fuel,

        water=water,

        production=production,

        machine_hours=machine_hours,

        highest_factor=
            highest_factor,

        highest_percentage=
            highest_percentage,

        prediction_id=
            prediction_id,

        blockchain_hash=
            blockchain_hash,

        blockchain_status=
            "Verified"

    )


# ============================================================
# RUN
# ============================================================

if __name__ == "__main__":

    app.run(
        debug=True
    )