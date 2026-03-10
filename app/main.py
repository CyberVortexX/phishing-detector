from fastapi import FastAPI
import joblib
import pandas as pd
from scipy.sparse import hstack

from app.feature_extractor import extract_features, TRUSTED_DOMAINS
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Load models
from pathlib import Path
import joblib

BASE_DIR = Path(__file__).resolve().parent.parent

model = joblib.load(BASE_DIR / "model/xgb_model.pkl")
vectorizer = joblib.load(BASE_DIR / "model/tfidf_vectorizer.pkl")
scaler = joblib.load(BASE_DIR / "model/struct_scaler.pkl")

@app.get("/")
def home():
    return {"message": "Phishing Detector API running"}


from pydantic import BaseModel

class URLRequest(BaseModel):
    url: str

@app.post("/predict")
def predict(data: URLRequest):

    url = data.url

    from urllib.parse import urlparse

    domain = urlparse(url).netloc.replace("www.", "")

    if any(trusted in domain for trusted in TRUSTED_DOMAINS):
        return {
        "url": url,
        "prediction": "legitimate",
        "probability": 0.0
        }

    # STEP 2: Extract structural features
    features = extract_features(url)

    X_struct = pd.DataFrame([features])
    X_struct_scaled = scaler.transform(X_struct)

    # STEP 3: TF-IDF
    X_text = vectorizer.transform([url])

    # STEP 4: Combine
    from scipy.sparse import hstack
    X = hstack([X_struct_scaled, X_text])

    # STEP 5: Model prediction
    probs = model.predict_proba(X)[0]
    prob_phishing = probs[1]

    prediction = "phishing" if prob_phishing >= 0.8 else "legitimate"

    return {
        "url": url,
        "prediction": prediction,
        "probability": float(prob_phishing)
    }