import os
import joblib
import pandas as pd
import numpy as np
import warnings
from flask import Flask, request, jsonify, render_template
from flask_cors import CORS

# Ignore sklearn unpickling warnings for different versions
warnings.filterwarnings("ignore", category=UserWarning)

app = Flask(__name__, template_folder="templates")
CORS(app)  # Enable Cross-Origin Resource Sharing for future integration

# Resolve file paths inside the Heart directory
HEART_DIR = os.path.dirname(os.path.abspath(__file__))
CSV_PATH = os.path.join(HEART_DIR, "heart.csv")
COLS_PATH = os.path.join(HEART_DIR, "columns.pkl")
MODEL_PATH = os.path.join(HEART_DIR, "logistic_heart.pkl")
SCALER_PATH = os.path.join(HEART_DIR, "scaler_heart.pkl")

# Load models and preprocessing assets
try:
    cols = joblib.load(COLS_PATH)
    scaler = joblib.load(SCALER_PATH)
    model = joblib.load(MODEL_PATH)
    print("Successfully loaded model, scaler, and columns.")
except Exception as e:
    print(f"Error loading models or scaler: {e}")
    cols, scaler, model = None, None, None

# Load dataset and precompute statistics for dashboard
try:
    df_raw = pd.read_csv(CSV_PATH)
    print(f"Successfully loaded dataset: {len(df_raw)} records.")
except Exception as e:
    print(f"Error loading dataset: {e}")
    df_raw = None

def compute_dataset_stats():
    if df_raw is None:
        return {}
    
    total = len(df_raw)
    hd_count = int(df_raw["HeartDisease"].sum())
    normal_count = total - hd_count
    
    # Summary stats
    stats = {
        "summary": {
            "total_patients": total,
            "heart_disease_count": hd_count,
            "normal_count": normal_count,
            "heart_disease_rate": round(float(df_raw["HeartDisease"].mean()) * 100, 2),
            "avg_age": round(float(df_raw["Age"].mean()), 1),
            "avg_cholesterol": round(float(df_raw["Cholesterol"].mean()), 1),
            "avg_resting_bp": round(float(df_raw["RestingBP"].mean()), 1),
            "avg_max_hr": round(float(df_raw["MaxHR"].mean()), 1)
        }
    }
    
    # Age vs Heart Disease
    # Bins: <40, 40-49, 50-59, 60-69, 70+
    age_bins = [0, 39, 49, 59, 69, 120]
    age_labels = ["<40", "40-49", "50-59", "60-69", "70+"]
    df_age = df_raw.copy()
    df_age["AgeGroup"] = pd.cut(df_age["Age"], bins=age_bins, labels=age_labels)
    age_hd = df_age[df_age["HeartDisease"] == 1].groupby("AgeGroup", observed=False).size().to_dict()
    age_normal = df_age[df_age["HeartDisease"] == 0].groupby("AgeGroup", observed=False).size().to_dict()
    
    stats["age_dist"] = {
        "labels": age_labels,
        "heart_disease": [int(age_hd.get(l, 0)) for l in age_labels],
        "normal": [int(age_normal.get(l, 0)) for l in age_labels]
    }
    
    # Sex vs Heart Disease
    sex_hd = df_raw[df_raw["HeartDisease"] == 1].groupby("Sex").size().to_dict()
    sex_normal = df_raw[df_raw["HeartDisease"] == 0].groupby("Sex").size().to_dict()
    stats["sex_dist"] = {
        "labels": ["Male", "Female"],
        "heart_disease": [int(sex_hd.get("M", 0)), int(sex_hd.get("F", 0))],
        "normal": [int(sex_normal.get("M", 0)), int(sex_normal.get("F", 0))]
    }
    
    # ChestPainType vs Heart Disease
    cp_types = ["ASY", "ATA", "NAP", "TA"]
    cp_hd = df_raw[df_raw["HeartDisease"] == 1].groupby("ChestPainType").size().to_dict()
    cp_normal = df_raw[df_raw["HeartDisease"] == 0].groupby("ChestPainType").size().to_dict()
    stats["cp_dist"] = {
        "labels": ["Asymptomatic (ASY)", "Atypical Angina (ATA)", "Non-Anginal (NAP)", "Typical Angina (TA)"],
        "heart_disease": [int(cp_hd.get(t, 0)) for t in cp_types],
        "normal": [int(cp_normal.get(t, 0)) for t in cp_types]
    }
    
    # ST_Slope vs Heart Disease
    slope_types = ["Up", "Flat", "Down"]
    slope_hd = df_raw[df_raw["HeartDisease"] == 1].groupby("ST_Slope").size().to_dict()
    slope_normal = df_raw[df_raw["HeartDisease"] == 0].groupby("ST_Slope").size().to_dict()
    stats["slope_dist"] = {
        "labels": ["Upsloping (Up)", "Flat", "Downsloping (Down)"],
        "heart_disease": [int(slope_hd.get(t, 0)) for t in slope_types],
        "normal": [int(slope_normal.get(t, 0)) for t in slope_types]
    }

    # Preprocess df for correlations (one-hot encode columns)
    df_encoded = pd.DataFrame()
    df_encoded["Age"] = df_raw["Age"]
    df_encoded["RestingBP"] = df_raw["RestingBP"]
    df_encoded["Cholesterol"] = df_raw["Cholesterol"]
    df_encoded["FastingBS"] = df_raw["FastingBS"]
    df_encoded["MaxHR"] = df_raw["MaxHR"]
    df_encoded["Oldpeak"] = df_raw["Oldpeak"]
    df_encoded["Sex_M"] = (df_raw["Sex"] == "M").astype(int)
    df_encoded["ChestPainType_ATA"] = (df_raw["ChestPainType"] == "ATA").astype(int)
    df_encoded["ChestPainType_NAP"] = (df_raw["ChestPainType"] == "NAP").astype(int)
    df_encoded["ChestPainType_TA"] = (df_raw["ChestPainType"] == "TA").astype(int)
    df_encoded["RestingECG_Normal"] = (df_raw["RestingECG"] == "Normal").astype(int)
    df_encoded["RestingECG_ST"] = (df_raw["RestingECG"] == "ST").astype(int)
    df_encoded["ExerciseAngina_Y"] = (df_raw["ExerciseAngina"] == "Y").astype(int)
    df_encoded["ST_Slope_Flat"] = (df_raw["ST_Slope"] == "Flat").astype(int)
    df_encoded["ST_Slope_Up"] = (df_raw["ST_Slope"] == "Up").astype(int)
    df_encoded["HeartDisease"] = df_raw["HeartDisease"]

    corrs = df_encoded.corr()["HeartDisease"].drop("HeartDisease")
    # Sort by absolute correlation
    corrs_sorted = corrs.abs().sort_values(ascending=False)
    corrs_original = corrs[corrs_sorted.index]
    
    friendly_names = {
        "ST_Slope_Up": "Up-sloping ST Slope",
        "ST_Slope_Flat": "Flat ST Slope",
        "ExerciseAngina_Y": "Exercise Induced Angina",
        "Oldpeak": "ST Depression (Oldpeak)",
        "ChestPainType_ATA": "Atypical Angina Chest Pain",
        "MaxHR": "Max Heart Rate",
        "Sex_M": "Male Gender",
        "Age": "Age",
        "ChestPainType_NAP": "Non-Anginal Chest Pain",
        "FastingBS": "Fasting Blood Sugar > 120",
        "Cholesterol": "Cholesterol Level",
        "ChestPainType_TA": "Typical Angina Chest Pain",
        "RestingBP": "Resting Blood Pressure",
        "RestingECG_ST": "ECG ST-T Abnormality",
        "RestingECG_Normal": "Normal ECG"
    }

    stats["correlations"] = {
        "features": [friendly_names.get(f, f) for f in corrs_original.index],
        "values": [round(float(v), 3) for v in corrs_original.values]
    }
    
    return stats

# Precompute stats
stats_cache = compute_dataset_stats()

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/api/stats", methods=["GET"])
def get_stats():
    return jsonify(stats_cache)

@app.route("/api/predict", methods=["POST"])
def predict():
    if model is None or scaler is None or cols is None:
        return jsonify({"error": "ML model or scaler is not loaded. Check server logs."}), 500
    
    try:
        data = request.json
        
        # Extract features
        age = float(data.get("Age", 50))
        sex = data.get("Sex", "M")
        chest_pain_type = data.get("ChestPainType", "ASY")
        resting_bp = float(data.get("RestingBP", 130))
        cholesterol = float(data.get("Cholesterol", 240))
        fasting_bs = int(data.get("FastingBS", 0))
        resting_ecg = data.get("RestingECG", "Normal")
        max_hr = float(data.get("MaxHR", 140))
        exercise_angina = data.get("ExerciseAngina", "N")
        oldpeak = float(data.get("Oldpeak", 0.0))
        st_slope = data.get("ST_Slope", "Flat")
        
        # Preprocess features matching one-hot encoding structure of training columns
        input_data = {}
        input_data["Age"] = age
        input_data["RestingBP"] = resting_bp
        input_data["Cholesterol"] = cholesterol
        input_data["FastingBS"] = fasting_bs
        input_data["MaxHR"] = max_hr
        input_data["Oldpeak"] = oldpeak
        input_data["Sex_M"] = 1 if sex == "M" else 0
        input_data["ChestPainType_ATA"] = 1 if chest_pain_type == "ATA" else 0
        input_data["ChestPainType_NAP"] = 1 if chest_pain_type == "NAP" else 0
        input_data["ChestPainType_TA"] = 1 if chest_pain_type == "TA" else 0
        input_data["RestingECG_Normal"] = 1 if resting_ecg == "Normal" else 0
        input_data["RestingECG_ST"] = 1 if resting_ecg == "ST" else 0
        input_data["ExerciseAngina_Y"] = 1 if exercise_angina == "Y" else 0
        input_data["ST_Slope_Flat"] = 1 if st_slope == "Flat" else 0
        input_data["ST_Slope_Up"] = 1 if st_slope == "Up" else 0
        
        # Build pandas DataFrame with correct columns order
        X_df = pd.DataFrame([input_data])[cols]
        
        # Standardize using the loaded scaler
        X_scaled = scaler.transform(X_df)
        
        # Compute predictions
        prob = float(model.predict_proba(X_scaled)[0][1])
        prediction = int(model.predict(X_scaled)[0])
        
        # Calculate feature contributions for Explainable AI (SHAP-like)
        # intercept (beta_0)
        intercept = float(model.intercept_[0])
        # coefficients (beta_i)
        coefs = model.coef_[0]
        # scaled input values (z_i)
        scaled_vals = X_scaled[0]
        
        # Contributions: beta_i * z_i
        contributions = coefs * scaled_vals
        
        friendly_names = {
            "Age": "Age",
            "RestingBP": "Resting Blood Pressure",
            "Cholesterol": "Cholesterol",
            "FastingBS": "Fasting Blood Sugar > 120",
            "MaxHR": "Max Heart Rate",
            "Oldpeak": "ST Depression (Oldpeak)",
            "Sex_M": "Male Gender",
            "ChestPainType_ATA": "Atypical Angina Chest Pain",
            "ChestPainType_NAP": "Non-Anginal Chest Pain",
            "ChestPainType_TA": "Typical Angina Chest Pain",
            "RestingECG_Normal": "Normal ECG",
            "RestingECG_ST": "ECG ST-T Wave Abnormality",
            "ExerciseAngina_Y": "Exercise Induced Angina",
            "ST_Slope_Flat": "Flat ST Slope",
            "ST_Slope_Up": "Up-sloping ST Slope"
        }
        
        impacts = []
        for i, col_name in enumerate(cols):
            cont = float(contributions[i])
            raw_val = float(X_df[col_name].iloc[0])
            coef = float(coefs[i])
            
            # Skip categorical features that are 0 (not active) to keep explanation clean
            if col_name in ["Sex_M", "ChestPainType_ATA", "ChestPainType_NAP", "ChestPainType_TA", 
                             "RestingECG_Normal", "RestingECG_ST", "ExerciseAngina_Y", 
                             "ST_Slope_Flat", "ST_Slope_Up"] and raw_val == 0:
                continue
                
            impacts.append({
                "feature": col_name,
                "friendly_name": friendly_names.get(col_name, col_name),
                "raw_value": raw_val,
                "contribution": cont,
                "coefficient": coef,
                "direction": "increase" if cont > 0 else "decrease",
                "importance": abs(cont)
            })
            
        # Sort impacts by importance (absolute contribution)
        impacts = sorted(impacts, key=lambda x: x["importance"], reverse=True)
        
        # Risk classification
        if prob < 0.35:
            risk_level = "Low"
            risk_color = "green"
            risk_desc = "Your parameters indicate a healthy heart profile. Keep maintaining a balanced diet and active lifestyle!"
        elif prob < 0.70:
            risk_level = "Moderate"
            risk_color = "orange"
            risk_desc = "Your parameters indicate a moderate cardiovascular risk. It is recommended to schedule a checkup and monitor your blood pressure and cholesterol levels."
        else:
            risk_level = "High"
            risk_color = "red"
            risk_desc = "Your parameters indicate a high probability of cardiovascular complications. Please consult a medical professional or cardiologist immediately."
            
        return jsonify({
            "probability": round(prob * 100, 1),
            "prediction": prediction,
            "risk_level": risk_level,
            "risk_color": risk_color,
            "risk_description": risk_desc,
            "intercept": intercept,
            "feature_impacts": impacts
        })
        
    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({"error": str(e)}), 400

@app.route("/api/sample", methods=["GET"])
def get_sample():
    # Return first 10 rows of heart.csv to populate the explorer table
    if df_raw is None:
        return jsonify([])
    
    # We will return the first 100 rows for the table explorer
    samples = df_raw.head(100).to_dict(orient="records")
    
    # Inject patient names (with "Syed Tahir Ahamed R" as the first one)
    import random
    first_names = ["John", "Emily", "Michael", "Sarah", "David", "Jessica", "James", "Sophia", "Robert", "Isabella", "William", "Mia", "Joseph", "Olivia", "Daniel", "Charlotte", "Matthew", "Amelia", "Andrew", "Harper"]
    last_names = ["Smith", "Johnson", "Williams", "Brown", "Jones", "Garcia", "Miller", "Davis", "Rodriguez", "Martinez", "Hernandez", "Lopez", "Gonzalez", "Wilson", "Anderson", "Thomas", "Taylor", "Moore", "Jackson", "Martin"]
    
    for i, s in enumerate(samples):
        random.seed(i)  # Deterministic naming
        s["Name"] = f"{random.choice(first_names)} {random.choice(last_names)}"
            
    return jsonify(samples)

if __name__ == "__main__":
    # Run server on port 5002 so it doesn't conflict with electron (port 3000) or express backend (port 5001)
    app.run(host="0.0.0.0", port=5002, debug=True)
