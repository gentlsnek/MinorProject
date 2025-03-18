import pandas as pd
import numpy as np
from sklearn.preprocessing import StandardScaler

# -------------------------------
# 1. Load the Merged Dataset
# -------------------------------
df = pd.read_csv("updated_merged_cic_andmal2017.csv")
print("Initial shape:", df.shape)
print(df.info())

# -------------------------------
# 2. Remove Duplicate Rows
# -------------------------------
df.drop_duplicates(inplace=True)
print("Shape after dropping duplicates:", df.shape)

# -------------------------------
# 3. Drop Columns with Excessive Missing Values
#    (For example, drop any column with >50% missing values)
# -------------------------------
threshold = 0.5  # 50%
cols_to_drop = [col for col in df.columns if df[col].isnull().mean() > threshold]
if cols_to_drop:
    print("Dropping columns due to high missing values:", cols_to_drop)
    df.drop(columns=cols_to_drop, inplace=True)
print("Shape after dropping high-missing columns:", df.shape)

# -------------------------------
# 4. Fill Missing Values
#    - For numeric columns, fill missing values with the median.
#    - For categorical columns, fill missing values with the mode.
# -------------------------------
numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
categorical_cols = df.select_dtypes(include=['object']).columns.tolist()

# Optionally, you can exclude the target variable "label" from encoding
if 'label' in categorical_cols:
    categorical_cols.remove('label')

# Fill missing numeric values
for col in numeric_cols:
    median_val = df[col].median()
    df[col].fillna(median_val, inplace=True)

# Fill missing categorical values
for col in categorical_cols:
    mode_val = df[col].mode()[0] if not df[col].mode().empty else "Unknown"
    df[col].fillna(mode_val, inplace=True)

# -------------------------------
# 5. Preprocess Timestamp Column (if present)
#    - Convert to datetime.
#    - Optionally, you can engineer new time-based features.p 
# -------------------------------
if 'timestamp' in df.columns:
    df['timestamp'] = pd.to_datetime(df['timestamp'], errors='coerce')
    # Replace any conversion failures with a default timestamp, e.g., the Unix epoch.
    df['timestamp'].fillna(pd.Timestamp("1970-01-01"), inplace=True)
    # (Optional) Create a new feature for "hour" or "day" if useful:
    df['hour'] = df['timestamp'].dt.hour

# -------------------------------
# 6. Normalize Numerical Features
#    - Standardize numeric columns to have zero mean and unit variance.
# -------------------------------
scaler = StandardScaler()
df[numeric_cols] = scaler.fit_transform(df[numeric_cols])

# -------------------------------
# 7. Encode Categorical Variables
#    - One-hot encode categorical features using pandas get_dummies.
# -------------------------------
df = pd.get_dummies(df, columns=categorical_cols, drop_first=True)

# -------------------------------
# 8. Save the Cleaned Dataset
# -------------------------------
cleaned_file = "cleaned_dataset.csv"
df.to_csv(cleaned_file, index=False)
print("Cleaned dataset saved to", cleaned_file)
print("Final shape:", df.shape)
