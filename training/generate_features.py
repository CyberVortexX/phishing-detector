import pandas as pd
from app.feature_extractor import extract_features

# Load balanced dataset
df = pd.read_csv("training/balanced_dataset.csv")

print("Generating features...")

X = df["url"].apply(extract_features)
X = pd.DataFrame(X.tolist())

y = df["label"]

# Save processed dataset
X["label"] = y

X.to_csv("training/final_dataset.csv", index=False)

print("Feature dataset shape:", X.shape)