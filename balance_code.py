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

# Print original class distribution
print("Original class distribution:\n", df['label'].value_counts())

# Define correct class distribution for undersampling (matching numeric labels)
target_count = {
    1: 1200,  # benign
    4: 84,   # smsmalware
    3: 84,   # scareware
    2: 84,   # ransomware
    0: 84    # adware
}

# Apply Random Undersampling
rus = RandomUnderSampler(sampling_strategy=target_count, random_state=42)
X_resampled, y_resampled = rus.fit_resample(df.drop(columns=['label']), df['label'])


# Apply Borderline-SMOTE (boost minority classes)
# Apply Borderline-SMOTE with correct numeric labels
smote = BorderlineSMOTE(sampling_strategy={
    3: 300,  # scareware
    4: 300,  # smsmalware
    2: 300,  # ransomware
    0: 300   # adware
}, random_state=42)

X_smote, y_smote = smote.fit_resample(X_resampled, y_resampled)

# Apply ADASYN for further balancing
adasyn = ADASYN(sampling_strategy={
    3: max(300, y_smote.value_counts()[3]),  
    4: max(300, y_smote.value_counts()[4]),  
    2: max(300, y_smote.value_counts()[2]),  
    0: max(300, y_smote.value_counts()[0])   
}, random_state=42)

X_balanced, y_balanced = adasyn.fit_resample(X_smote, y_smote)

# Convert back to DataFrame
df_balanced = pd.DataFrame(X_balanced, columns=df.drop(columns=['label']).columns)
df_balanced['label'] = y_balanced

# Print final class distribution
print("\nFinal class distribution after oversampling:\n", df_balanced['label'].value_counts())

# Save the balanced dataset
df_balanced.to_csv('balanced_dataset.csv', index=False)
