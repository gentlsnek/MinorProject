import os
import pandas as pd
import logging
import tkinter as tk
from tkinter import ttk
from androguard.misc import AnalyzeAPK

# Setup logging
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class APKPreprocessor:
    def __init__(self, dataset_paths, output_path):
        self.dataset_paths = dataset_paths
        self.output_path = output_path
        os.makedirs(output_path, exist_ok=True)

        # Setup Tkinter progress bar
        self.root = tk.Tk()
        self.root.title("APK Processing Progress")
        self.root.geometry("300x100")
        self.progress_label = tk.Label(self.root, text="Initializing...")
        self.progress_label.pack(pady=10)
        self.progress_bar = ttk.Progressbar(self.root, orient="horizontal", length=250, mode="determinate")
        self.progress_bar.pack(pady=10)
        self.root.update()

    def extract_apk_features(self, apk_path):
        try:
            a, d, dx = AnalyzeAPK(apk_path)
            features = {
                "package_name": a.get_package(),
                "app_name": a.get_app_name(),
                "version_code": a.get_androidversion_code(),
                "num_permissions": len(a.get_permissions()),
                "num_activities": len(a.get_activities()),
                "num_services": len(a.get_services()),
                "num_receivers": len(a.get_receivers()),
                "num_providers": len(a.get_providers()),
                "num_intents": sum(len(a.get_intent_filters("activity", act)) for act in a.get_activities()),
                "total_methods": len(list(dx.get_methods())),  # Convert generator to list
                "has_native_code": int(any(".so" in file for file in a.get_files())),
                "file_size_kb": os.path.getsize(apk_path) / 1024,
                "num_files": len(a.get_files())
            }
            return features
        except Exception as e:
            logger.error(f"Error processing {apk_path}: {e}")
            return None

    def process_dataset(self):
        total_files = sum(len(os.listdir(dataset_path)) for dataset_path in self.dataset_paths)
        processed_files = 0
        self.progress_bar['maximum'] = total_files

        output_csv = os.path.join(self.output_path, "apk_features.csv")
        # Initialize the CSV file with headers
        if not os.path.exists(output_csv):
            df = pd.DataFrame(columns=[
                "filename", "package_name", "app_name", "version_code", "version_name",
                "num_permissions", "num_activities", "num_services", "num_receivers",
                "num_providers", "num_intents", "total_methods", "has_native_code",
                "file_size_kb", "num_files"
            ])
            df.to_csv(output_csv, index=False)
            logger.info(f"Initialized CSV file with headers at {output_csv}")

        for dataset_path in self.dataset_paths:
            apk_files = [f for f in os.listdir(dataset_path) if f.endswith('.apk')]
            logger.info(f"Found {len(apk_files)} APK files in {dataset_path} to process")

            for apk_file in apk_files:
                apk_path = os.path.join(dataset_path, apk_file)
                features = self.extract_apk_features(apk_path)

                if features is not None:
                    combined_features = {
                        "filename": apk_file,
                        "package_name": features["package_name"],
                        "app_name": features["app_name"],
                        "version_code": features["version_code"],
                        "version_name": features.get("version_name", "Unknown"),
                        "num_permissions": features["num_permissions"],
                        "num_activities": features["num_activities"],
                        "num_services": features["num_services"],
                        "num_receivers": features["num_receivers"],
                        "num_providers": features["num_providers"],
                        "num_intents": features["num_intents"],
                        "total_methods": features["total_methods"],
                        "has_native_code": int(features["has_native_code"]),
                        "file_size_kb": features["file_size_kb"],
                        "num_files": features["num_files"],
                    }
                    # Append the features to the CSV file
                    df = pd.DataFrame([combined_features])
                    df.to_csv(output_csv, mode='a', header=False, index=False)
                    logger.debug(f"Added features for {apk_file}: {combined_features}")

                processed_files += 1
                self.progress_bar['value'] = processed_files
                self.progress_label.config(text=f"Processed {processed_files}/{total_files} APKs")
                self.root.update()

        self.progress_label.config(text="Processing Complete!")
        self.root.update()
        self.root.after(3000, self.root.destroy)
        self.root.mainloop()

if __name__ == "__main__":
    # List of dataset paths
    dataset_paths = [
        r".\datasets\Ransomware-APKs\Ransomware\Charger",
        r".\datasets\Ransomware-APKs\Ransomware\Jisut",
        r".\datasets\Ransomware-APKs\Ransomware\Koler",\
        r".\datasets\Ransomware-APKs\Ransomware\LockerPin",
        r".\datasets\Ransomware-APKs\Ransomware\Simplocker",
        r".\datasets\Ransomware-APKs\Ransomware\Wannalocker",
        r".\datasets\Ransomware-APKs\Ransomware\Pletor",
        r".\datasets\Ransomware-APKs\Ransomware\PornDroid",
        r".\datasets\Ransomware-APKs\Ransomware\RansomBO",
        r".\datasets\Ransomware-APKs\Ransomware\Svpeng",
    ]

    # Output directory for processed data
    output_path = "processed_data"
    os.makedirs(output_path, exist_ok=True)

    processor = APKPreprocessor(dataset_paths, output_path)
    processor.process_dataset()
#"""
#        r".\datasets\Ransomware-APKs\Ransomware\Charger",
#        r".\datasets\Ransomware-APKs\Ransomware\Jisut",
#        r".\datasets\Ransomware-APKs\Ransomware\Koler",\
#        r".\datasets\Ransomware-APKs\Ransomware\LockerPin",
#        r".\datasets\Ransomware-APKs\Ransomware\Simplocker",
#        r".\datasets\Ransomware-APKs\Ransomware\Wannalocker",
#        r".\datasets\Ransomware-APKs\Ransomware\Pletor",
#        r".\datasets\Ransomware-APKs\Ransomware\PornDroid",
#        r".\datasets\Ransomware-APKs\Ransomware\RansomBO",
#        r".\datasets\Ransomware-APKs\Ransomware\Svpeng",
#        r".\datasets\Scareware-APKs\Scareware\Android.spy.277",
#        r".\datasets\Scareware-APKs\Scareware\AndroidDefender",
#        r".\datasets\Scareware-APKs\Scareware\AvForAndroid",
#        #r".\dataset\Scareware-APKs\Scareware\AvPass",
#        r".\datasets\Scareware-APKs\Scareware\FakeApp",
#        r".\datasets\Scareware-APKs\Scareware\FakeApp_AL",
#        r".\datasets\Scareware-APKs\Scareware\FakeAV",
#        r".\datasets\Scareware-APKs\Scareware\FakeJobOffer",
#        r".\datasets\Scareware-APKs\Scareware\FaketaoBao",
#        r".\datasets\Scareware-APKs\Scareware\penetho",
#        r".\datasets\Scareware-APKs\Scareware\VirusShield",
#        r".\datasets\SMSmalware-APKs\SMSmalware\BeanBot",
#        r".\datasets\SMSmalware-APKs\SMSmalware\Biige",
#        r".\datasets\SMSmalware-APKs\SMSmalware\FakeInst",
#        r".\datasets\SMSmalware-APKs\SMSmalware\FakeMart",
#        r".\datasets\SMSmalware-APKs\SMSmalware\FakeNotify",
#        r".\datasets\SMSmalware-APKs\SMSmalware\Jifake",
#        r".\datasets\SMSmalware-APKs\SMSmalware\MazarBot",
#        r".\datasets\SMSmalware-APKs\SMSmalware\Nandrobox",
#        r".\datasets\SMSmalware-APKs\SMSmalware\Plankton",
#        r".\datasets\SMSmalware-APKs\SMSmalware\SMSsniffer",
#        r".\datasets\SMSmalware-APKs\SMSmalware\Zsone",
#        r".\datasets\Benign-APKs-2015\Benign_2015",
#        r".\datasets\Benign-APKs-2016\Benign_2016",
#        r".\datasets\Benign-APKs-2017\Benign_2017"
#"""