import os
import pandas as pd

# Define the directory where the CSV files are stored using a raw string to avoid escape issues.
data_dir = r".\processed_data"

# Define the file names along with their corresponding labels.
# Here, the keys are only the file names (without any directory path) because data_dir handles the location.
files_labels = {
    "apk_features_2015_1016.csv": "malware_2015_1016",
    "apk_features_adware.csv": "adware",
    "apk_features_ransomware.csv": "ransomware",
    "apk_features_scareware.csv": "scareware",
    "apk_features_smsmalware.csv": "smsmalware",
    "benign 2017.csv": "benign"
}

# Dictionary to store each DataFrame.
dataframes = {}

# Loop over each file, construct the full file path, load the CSV, add a label column, and store the DataFrame.
for file_name, label in files_labels.items():
    file_path = os.path.join(data_dir, file_name)
    if not os.path.exists(file_path):
        print(f"Error: File not found - {file_path}")
        continue  # Skip files that are not found.
    try:
        df = pd.read_csv(file_path, low_memory=False)
        df['label'] = label  # Add a column indicating the malware type or benign status.
        dataframes[file_name] = df
        print(f"Loaded {file_name} from {file_path} with shape {df.shape}")
    except Exception as e:
        print(f"Error loading {file_name} from {file_path}: {e}")

# Check if any files were loaded.
if not dataframes:
    raise ValueError("No files were loaded. Please check your file paths and names.")

# Compute the union of all column names across the loaded DataFrames.
all_columns = set()
for df in dataframes.values():
    all_columns.update(df.columns)
all_columns = list(all_columns)
print(f"Total unique columns across all files: {len(all_columns)}")

# Reindex each DataFrame so that all have the same columns (filling missing ones with NaN).
standardized_dfs = []
for file_name, df in dataframes.items():
    standardized_df = df.reindex(columns=all_columns)
    standardized_dfs.append(standardized_df)
    print(f"{file_name} reindexed to shape {standardized_df.shape}")

# Check if there are any DataFrames to concatenate.
if not standardized_dfs:
    raise ValueError("No DataFrames available for concatenation.")

# Concatenate all standardized DataFrames into one merged DataFrame.
merged_df = pd.concat(standardized_dfs, axis=0, ignore_index=True)
print(f"Merged dataset shape: {merged_df.shape}")

# Save the merged DataFrame to a new CSV file in the same directory.
output_file = os.path.join(data_dir, "merged_cic_andmal2017.csv")
merged_df.to_csv(output_file, index=False)
print(f"Merged dataset saved to {output_file}")
