import pandas as pd
from imblearn.over_sampling import BorderlineSMOTE, ADASYN
from imblearn.under_sampling import RandomUnderSampler

# Load dataset
df = pd.read_csv('updated_merged_cic_andmal2017.csv')

# Drop duplicates and handle missing values
df = df.drop_duplicates().dropna()

# Drop non-numeric columns (like file names)
if 'filename' in df.columns:  # Adjust based on your actual column names
    df = df.drop(columns=['filename'])

# Convert categorical features to numerical if needed (use label encoding)
categorical_cols = df.select_dtypes(include=['object']).columns.tolist()
df[categorical_cols] = df[categorical_cols].astype('category').apply(lambda x: x.cat.codes)

# Print updated data types (for debugging)
print(df.dtypes)

# Save the processed dataset to CSV
df.to_csv('prepared_cic_malanal2017.csv', index=False)
print(f"Processed dataset saved to 'prepared_malanal2017.csv' ({len(df)} rows)")
