import os
import zipfile
import re
import pandas as pd
from androguard.core.bytecodes import apk, dvm
from androguard.core.analysis import analysis
from sklearn.feature_extraction.text import CountVectorizer

def extract_apk_features(apk_path):
    """Extract comprehensive features from an APK file"""
    apk_info = {}
    
    # Get category from path (Adware, Benign, Ransomware, etc.)
    if 'Adware' in apk_path:
        apk_info['category'] = 'Adware'
    elif 'Benign' in apk_path:
        apk_info['category'] = 'Benign'
    elif 'Ransomware' in apk_path:
        apk_info['category'] = 'Ransomware'
    elif 'Scareware' in apk_path:
        apk_info['category'] = 'Scareware'
    elif 'SMSmalware' in apk_path:
        apk_info['category'] = 'SMSmalware'
    else:
        apk_info['category'] = 'Unknown'
    
    try:
        # Parse APK
        a = apk.APK(apk_path)
        d = dvm.DalvikVMFormat(a.get_dex())
        dx = analysis.Analysis(d)
        
        # Extract permissions
        permissions = a.get_permissions()
        apk_info['permissions'] = list(permissions)
        
        # Extract intents
        intents = []
        for intent in a.get_intent_filters():
            for action in intent.get_action():
                intents.append(action)
        apk_info['intents'] = intents
        
        # Extract API calls
        api_calls = []
        for method in dx.get_methods():
            for _, call, _ in method.get_xref_to():
                api_calls.append(call.get_class_name() + "->" + call.get_name())
        apk_info['api_calls'] = api_calls[:1000]  # Limit to prevent excessive data
        
        # Extract opcode sequence
        opcodes = []
        for method in d.get_methods():
            if method.get_code():
                for ins in method.get_code().get_instructions():
                    opcodes.append(ins.get_name())
        apk_info['opcodes'] = opcodes[:2000]  # Limit to prevent excessive data
        
        # Extract and tokenize strings
        string_list = []
        for string in d.get_strings():
            string_val = string.get_value()
            if len(string_val) > 3 and not string_val.isdigit():  # Filter out very short strings and pure numbers
                string_list.append(string_val)
        
        # Tokenize strings
        if string_list:
            vectorizer = CountVectorizer(analyzer='word', token_pattern=r'\b\w+\b')
            vectorizer.fit_transform([' '.join(string_list)])
            apk_info['string_tokens'] = vectorizer.get_feature_names_out().tolist()
        else:
            apk_info['string_tokens'] = []
        
        apk_info['path'] = apk_path
        apk_info['package_name'] = a.get_package()
        apk_info['success'] = True
        
    except Exception as e:
        apk_info['error'] = str(e)
        apk_info['path'] = apk_path
        apk_info['success'] = False
        
    return apk_info

def preprocess_apks(base_dir):
    """Process all APK files in the given directory and subdirectories"""
    apk_data = []
    total_apks = 0
    processed_apks = 0
    
    # First count total APKs
    for root, dirs, files in os.walk(base_dir):
        for file in files:
            if file.endswith('.apk'):
                total_apks += 1
    
    # Now process each APK
    for root, dirs, files in os.walk(base_dir):
        for file in files:
            if file.endswith('.apk'):
                apk_path = os.path.join(root, file)
                processed_apks += 1
                print(f"Processing APK {processed_apks}/{total_apks}: {apk_path}")
                
                apk_info = extract_apk_features(apk_path)
                apk_data.append(apk_info)
                
                # Save intermediate results every 50 APKs
                if processed_apks % 50 == 0:
                    save_results(apk_data, f"apk_features_partial_{processed_apks}.csv")
    
    return apk_data

def save_results(apk_data, filename):
    """Save the extracted features to a CSV file"""
    # Convert to pandas DataFrame for easier handling
    df = pd.DataFrame(apk_data)
    
    # Save to CSV
    df.to_csv(filename, index=False)
    print(f"Saved results to {filename}")
    
    # Also save specific feature sets for easier analysis
    if len(apk_data) > 0 and 'permissions' in apk_data[0]:
        # Create a one-hot encoded permissions dataframe
        all_permissions = set()
        for item in apk_data:
            if 'permissions' in item and item['permissions']:
                all_permissions.update(item['permissions'])
        
        perm_dict = {apk['path']: {perm: 1 if perm in apk.get('permissions', []) else 0 
                                for perm in all_permissions} 
                    for apk in apk_data if 'path' in apk}
        
        perm_df = pd.DataFrame.from_dict(perm_dict, orient='index')
        perm_df.to_csv("permissions_features.csv")

if __name__ == "__main__":
    base_dir = '/home/gentlesnek/projects/MinorProject/CICApks'
    apk_data = preprocess_apks(base_dir)
    
    # Save final results
    save_results(apk_data, "apk_features_complete.csv")
    
    # Print summary
    print("\nPreprocessing Complete!")
    print(f"Processed {len(apk_data)} APK files")
    successful = sum(1 for apk in apk_data if apk.get('success', False))
    print(f"Successfully analyzed: {successful}")
    print(f"Failed: {len(apk_data) - successful}")