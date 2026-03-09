import joblib
import pandas as pd
import numpy as np
from scipy.sparse import hstack
from sklearn.metrics import classification_report, confusion_matrix

from app.feature_extractor import extract_features

print("Loading model...")

model = joblib.load("model/phishing_model.pkl")
vectorizer = joblib.load("model/tfidf_vectorizer.pkl")
scaler = joblib.load("model/struct_scaler.pkl")

print("Model loaded.")

# -----------------------------------
# LOAD EXTERNAL DATASET
# -----------------------------------
# CHANGE THIS PATH
external_df = pd.read_csv("training/external_dataset.csv")
print(external_df.columns)
# Make sure columns are:
# url, label
# label: 1 = phishing, 0 = legitimate

print("External dataset shape:", external_df.shape)

urls = external_df["url"].astype(str).tolist()
# Convert multi-class to binary
# 2 = phishing → 1
# others → 0
y_true = (external_df["label"] == 2).astype(int)

# -----------------------------------
# Feature Extraction
# -----------------------------------
print("Extracting features...")

X_struct = [extract_features(url) for url in urls]
X_struct_df = pd.DataFrame(X_struct)
X_struct_scaled = scaler.transform(X_struct_df)

X_text = vectorizer.transform(urls)

X_combined = hstack([X_struct_scaled, X_text])

# -----------------------------------
# Prediction
# -----------------------------------
probs = model.predict_proba(X_combined)[:, 1]

threshold = 0.5
y_pred = (probs >= threshold).astype(int)

# -----------------------------------
# Evaluation
# -----------------------------------
print("\nExternal Classification Report:\n")
print(classification_report(y_true, y_pred))

print("\nConfusion Matrix:\n")
print(confusion_matrix(y_true, y_pred))
print("Mean predicted probability:", probs.mean())
print("Max probability:", probs.max())
print("Min probability:", probs.min())