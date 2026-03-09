import joblib
import pandas as pd
import shap
import numpy as np
import matplotlib.pyplot as plt

from scipy.sparse import hstack
from app.feature_extractor import extract_features

print("Loading model...")
model = joblib.load("model/phishing_model.pkl")
vectorizer = joblib.load("model/tfidf_vectorizer.pkl")
scaler = joblib.load("model/struct_scaler.pkl")
print("Loaded successfully.")

# ---------------------------------
# Load dataset sample (SMALL)
# ---------------------------------
df = pd.read_csv("training/balanced_dataset.csv")
sample_df = df.sample(100, random_state=42)

urls = sample_df["url"].tolist()

# ---------------------------------
# Build FULL feature matrix
# ---------------------------------
X_struct = [extract_features(url) for url in urls]
X_struct_df = pd.DataFrame(X_struct)
X_struct_scaled = scaler.transform(X_struct_df)

X_text = vectorizer.transform(urls)

X_combined = hstack([X_struct_scaled, X_text])

print("Generating SHAP values (full feature space)...")

# Use TreeExplainer
explainer = shap.TreeExplainer(model)

shap_values = explainer.shap_values(X_combined)

# Convert to dense for plotting
X_dense = X_combined.toarray()

# ---------------------------------
# Save summary plot
# ---------------------------------
# Create feature names list
struct_names = list(X_struct_df.columns)
tfidf_names = vectorizer.get_feature_names_out().tolist()

all_feature_names = struct_names + tfidf_names

shap.summary_plot(
    shap_values,
    X_dense,
    feature_names=all_feature_names,
    show=False,
    max_display=20
)

plt.tight_layout()
plt.savefig("model/shap_full_summary.png", dpi=300)

print("SHAP summary saved to model/shap_full_summary.png")