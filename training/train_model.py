import pandas as pd
import numpy as np
import joblib

from scipy.sparse import hstack
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report, confusion_matrix
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import LogisticRegression

from xgboost import XGBClassifier

# -----------------------------
# Load Dataset
# -----------------------------
df = pd.read_csv("training/balanced_dataset.csv")

print("Dataset loaded:", df.shape)

# -----------------------------
# Fix Labels (convert to binary)
# -----------------------------
df["label"] = df["label"].replace({
    2: 1,
    3: 1
})

print("\nLabel distribution:")
print(df["label"].value_counts())

# -----------------------------
# Remove NaN
# -----------------------------
df = df.dropna(subset=["url", "label"])

# -----------------------------
# Import Feature Extractor
# -----------------------------
from app.feature_extractor import extract_features

print("\nExtracting structural features...")

X_struct = df["url"].apply(extract_features)
X_struct = pd.DataFrame(X_struct.tolist())

# -----------------------------
# Scale Structural Features
# -----------------------------
scaler = StandardScaler()
X_struct_scaled = scaler.fit_transform(X_struct)

# -----------------------------
# TF-IDF Features
# -----------------------------
print("Generating TF-IDF features...")

vectorizer = TfidfVectorizer(
    analyzer="char",
    ngram_range=(3,5),
    max_features=5000
)

X_text = vectorizer.fit_transform(df["url"])

# -----------------------------
# Combine Features
# -----------------------------
X = hstack([X_struct_scaled, X_text])

y = df["label"]

# -----------------------------
# Train Test Split
# -----------------------------
X_train, X_test, y_train, y_test = train_test_split(
    X,
    y,
    test_size=0.2,
    stratify=y,
    random_state=42
)

print("\nTraining size:", X_train.shape)
print("Testing size:", X_test.shape)

# -----------------------------
# Handle Class Imbalance
# -----------------------------
positive = sum(y_train == 1)
negative = sum(y_train == 0)

scale_pos_weight = negative / positive

print("Positive samples:", positive)
print("Negative samples:", negative)
print("scale_pos_weight:", scale_pos_weight)

# -----------------------------
# Train XGBoost
# -----------------------------
print("\nTraining XGBoost...")

xgb_model = XGBClassifier(
    n_estimators=500,
    max_depth=6,
    learning_rate=0.05,
    subsample=0.8,
    colsample_bytree=0.8,
    scale_pos_weight=scale_pos_weight,
    objective="binary:logistic",
    eval_metric="logloss",
    tree_method="hist",
    n_jobs=-1,
    random_state=42
)

xgb_model.fit(X_train, y_train)

# -----------------------------
# Train Logistic Regression
# -----------------------------
print("Training Logistic Regression...")

lr_model = LogisticRegression(
    max_iter=1000,
    class_weight="balanced"
)

lr_model.fit(X_train, y_train)

# -----------------------------
# Ensemble Prediction
# -----------------------------
print("\nEvaluating Ensemble...")

xgb_probs = xgb_model.predict_proba(X_test)[:,1]
lr_probs = lr_model.predict_proba(X_test)[:,1]

ensemble_probs = (xgb_probs + lr_probs) / 2

threshold = 0.7

y_pred = (ensemble_probs >= threshold).astype(int)

# -----------------------------
# Evaluation
# -----------------------------
print("\nTEST Classification Report:\n")

print(classification_report(y_test, y_pred))

print("\nConfusion Matrix:\n")

print(confusion_matrix(y_test, y_pred))

# -----------------------------
# Save Models
# -----------------------------
joblib.dump(xgb_model, "model/xgb_model.pkl")
joblib.dump(lr_model, "model/lr_model.pkl")
joblib.dump(vectorizer, "model/tfidf_vectorizer.pkl")
joblib.dump(scaler, "model/struct_scaler.pkl")

print("\nModels saved successfully.")