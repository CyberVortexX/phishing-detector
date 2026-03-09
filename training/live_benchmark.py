import pandas as pd
import numpy as np
import joblib
import requests

from scipy.sparse import hstack
from sklearn.metrics import classification_report, confusion_matrix

# -----------------------------
# Import feature extractor
# -----------------------------
from app.feature_extractor import extract_features


# -----------------------------
# Load model + preprocessing
# -----------------------------
print("Loading model...")

model = joblib.load("model/xgb_model.pkl")
vectorizer = joblib.load("model/tfidf_vectorizer.pkl")
scaler = joblib.load("model/struct_scaler.pkl")

print("Model loaded.")


# -----------------------------
# Download OpenPhish feed
# -----------------------------
print("Downloading OpenPhish feed...")

url = "https://openphish.com/feed.txt"

response = requests.get(url)
phishing_urls = response.text.split("\n")

phishing_urls = [u for u in phishing_urls if len(u) > 5]

phishing_urls = phishing_urls[:300]

print("Phishing URLs collected:", len(phishing_urls))


# -----------------------------
# Load legitimate URLs
# -----------------------------
legit_df = pd.read_csv("training/clean_dataset.csv")

legit_urls = legit_df["url"].sample(300).tolist()


# -----------------------------
# Build evaluation dataset
# -----------------------------
urls = phishing_urls + legit_urls
labels = [1]*len(phishing_urls) + [0]*len(legit_urls)

df_eval = pd.DataFrame({
    "url": urls,
    "label": labels
})

print("Total evaluation URLs:", len(df_eval))


# -----------------------------
# Structural feature extraction
# -----------------------------
print("Extracting structural features...")

X_struct = df_eval["url"].apply(extract_features)

X_struct = pd.DataFrame(X_struct.tolist())

X_struct_scaled = scaler.transform(X_struct)


# -----------------------------
# TF-IDF features
# -----------------------------
print("Generating TF-IDF features...")

X_text = vectorizer.transform(df_eval["url"])


# -----------------------------
# Combine features
# -----------------------------
X = hstack([X_struct_scaled, X_text])


# -----------------------------
# Model prediction
# -----------------------------
probs = model.predict_proba(X)[:,1]

threshold = 0.8

y_pred = (probs >= threshold).astype(int)


# -----------------------------
# Evaluation
# -----------------------------
print("\nLive Benchmark Results:\n")

print(classification_report(df_eval["label"], y_pred))

print("\nConfusion Matrix:\n")

print(confusion_matrix(df_eval["label"], y_pred))


# -----------------------------
# Probability stats
# -----------------------------
print("\nMean predicted probability:", np.mean(probs))
print("Max probability:", np.max(probs))
print("Min probability:", np.min(probs))