# CardioInsight AI - Heart Disease Risk Predictor & Analytics Dashboard

CardioInsight AI is a premium, web-based clinical assessment companion and dataset dashboard. It is powered by a Logistic Regression model trained on the combined UCI Heart Disease Dataset (918 patient records), achieving **86.27% accuracy** under 5-fold cross-validation.

This directory contains the standalone deployment package.

---

## ⚠️ CLINICAL SAFETY & LIABILITY DISCLAIMER

**IMPORTANT: READ BEFORE DEPLOYMENT OR INTEGRATION**

1. **NOT A DIAGNOSTIC DEVICE:** CardioInsight AI is an educational predictive utility based on historical statistical correlations. It is **not** a diagnostic device, clinical decision support system, or medical software under FDA Title 21 CFR or European Union Medical Device Regulation (MDR 2017/745).
2. **NO REGULATORY APPROVALS:** This application has not received CE Mark clearance, FDA 510(k) clearance, or approval from any medical regulatory authority globally.
3. **DO NOT USE FOR MEDICAL DIAGNOSIS:** This tool should **never** be used to replace professional medical advice, clinical diagnosis, or a cardiologist's direct evaluation.
4. **LIMITATIONS OF DATASET:** The underlying model is trained on a demographic cohort aged **28 to 77 years**. Predictions outside this range, or on patients with complex congenital heart defects, pacemakers, or active drug regimens not accounted for in the UCI repository, may yield skewed or highly inaccurate results.
5. **USER CONSENT MANDATORY:** A liability and disclaimer consent modal is built into the application's portal. It blocks user interaction until they explicitly accept these clinical boundaries.

---

## 🛠️ Architecture & Technology Stack

- **Backend:** Flask (Python 3.8+) serving sample tables, dataset statistics, and prediction fallbacks.
- **Frontend:** Single Page Application (HTML5 / Vanilla JS / Tailwind CSS / Chart.js / Lucide Icons).
- **ML Engine:** Dual-Execution:
  - **Primary:** Client-side zero-latency local prediction engine in pure JS (mathematically identical to scikit-learn Logistic Regression).
  - **Fallback:** Python Flask `/api/predict` route leveraging serialized `logistic_heart.pkl` and `scaler_heart.pkl`.

---

## 🚀 Running Locally

1. Install the required dependencies:
   ```bash
   pip install -r requirements.txt
   ```
2. Start the Flask server:
   ```bash
   python app.py
   ```
3. Open `http://127.0.0.1:5002` in your web browser.

---

## 🌐 Deploying to Production (e.g. Render, Heroku)

This app is production-ready. We use **Gunicorn** as a production WSGI server.

### Deploying to Render
1. Create a new **Web Service** on Render linked to your repository.
2. Set the **Root Directory** to `Heart`.
3. Set the **Build Command** to:
   ```bash
   pip install -r requirements.txt
   ```
4. Set the **Start Command** to:
   ```bash
   gunicorn app:app --bind 0.0.0.0:$PORT
   ```
5. Add the environment variables if needed (e.g., `PORT=5002` or let Render assign dynamically).

---

## 📊 Model Training Metadata

- **Intercept:** `0.27836358261363614`
- **Features & Coefficients (Log-Odds Impact):**
  - Age: `0.17037801` (older age = higher risk)
  - Resting BP: `0.0123106` (higher systolic pressure = higher risk)
  - Cholesterol: `0.0295025` (elevated cholesterol = higher risk)
  - Fasting BS > 120: `0.50528763` (hyperglycemic = higher risk)
  - Max HR: `-0.18873965` (lower max heart rate = higher risk)
  - Oldpeak: `0.4488342` (higher ST depression = higher risk)
  - Male Sex: `0.60360469` (male = higher risk)
  - Atypical Chest Pain (ATA): `-0.63170654` (atypical angina = lower risk relative to asymptomatic)
  - Non-Anginal Chest Pain (NAP): `-0.58007532` (non-anginal pain = lower risk relative to asymptomatic)
  - Typical Chest Pain (TA): `-0.24637359` (typical angina = slightly lower risk relative to asymptomatic)
  - Normal ECG: `-0.00728146` (normal resting ECG = slightly lower risk relative to hypertrophy)
  - ST-T ECG Abnormality: `-0.07072744` (ST wave abnormality = slightly lower risk relative to hypertrophy)
  - Exercise Angina (Yes): `0.49836494` (angina under strain = higher risk)
  - Flat ST Slope: `0.55885472` (flat ST recovery slope = higher risk)
  - Upsloping ST Slope: `-0.60450283` (upsloping ST recovery = lower risk)
