import pandas as pd

# Load the dataset
df = pd.read_csv('balanced_dataset.csv')

# Initialize counters
label_counts = df['label'].value_counts()

# Print the results
print("Total number of benign samples:", label_counts.get( 1, 0))
print("Total number of adware samples:", label_counts.get(0, 0))
print("Total number of ransomware samples:", label_counts.get(2, 0))
print("Total number of smsware samples:", label_counts.get(4, 0))
print("Total number of scareware samples:", label_counts.get(3, 0))
