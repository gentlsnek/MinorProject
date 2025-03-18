import pandas as pd

# Load your merged dataset
df = pd.read_csv(".\processed_data\merged_cic_andmal2017.csv")

# Replace 'malware_2015_1016' with 'benign' in the label column
df['label'].replace('malware_2015_1016', 'benign', inplace=True)

# Save the updated dataframe
df.to_csv("updated_merged_cic_andmal2017.csv", index=False)

print("Replacement complete. Updated CSV saved as 'updated_merged_cic_andmal2017.csv'")
