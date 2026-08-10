import pandas as pd
import pickle

from sklearn.ensemble import RandomForestRegressor
from sklearn.preprocessing import LabelEncoder


# ==============================
# LOAD DATASET
# ==============================

data = pd.read_csv("dataset.csv")


# ==============================
# ENCODE FABRIC TYPE
# ==============================

encoder = LabelEncoder()

data["fabric"] = encoder.fit_transform(data["fabric"])


# ==============================
# INPUT FEATURES
# ==============================

X = data[
    [
        "electricity",
        "fuel",
        "water",
        "production",
        "machine_hours",
        "fabric"
    ]
]


# ==============================
# TARGET
# ==============================

y = data["carbon_emission"]


# ==============================
# RANDOM FOREST MODEL
# ==============================

model = RandomForestRegressor(
    n_estimators=200,
    random_state=42
)

model.fit(X, y)


# ==============================
# SAVE MODEL
# ==============================

with open("model.pkl", "wb") as file:
    pickle.dump(model, file)


# ==============================
# SAVE ENCODER
# ==============================

with open("encoder.pkl", "wb") as file:
    pickle.dump(encoder, file)


# ==============================
# FEATURE IMPORTANCE
# ==============================

print("\nFeature Importance:")

features = [
    "Electricity",
    "Fuel",
    "Water",
    "Production",
    "Machine Hours",
    "Fabric"
]

for feature, importance in zip(features, model.feature_importances_):
    print(f"{feature}: {importance:.4f}")


# ==============================
# SUCCESS MESSAGE
# ==============================

print("\nModel Created Successfully!")
print("model.pkl and encoder.pkl updated successfully.")