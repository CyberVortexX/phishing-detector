import pandas as pd

# Load cleaned dataset
df = pd.read_csv("training/clean_dataset.csv")

print("Original shape:", df.shape)

# Separate classes
df_legit = df[df["label"] == 0]
df_phish = df[df["label"] == 1]

# Downsample legitimate to match phishing
df_legit_sampled = df_legit.sample(n=len(df_phish), random_state=42)

# Combine
df_balanced = pd.concat([df_legit_sampled, df_phish])

# Shuffle
df_balanced = df_balanced.sample(frac=1, random_state=42).reset_index(drop=True)

print("Balanced shape:", df_balanced.shape)
print("\nBalanced distribution:")
print(df_balanced["label"].value_counts())

# Save
df_balanced.to_csv("training/balanced_dataset.csv", index=False)