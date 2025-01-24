# Firestore CSV Downloader

This repository contains a **single Python script** (`download_firestore_csv.py`) that connects to a **Firestore database**, retrieves documents from specified collections, and saves them as **CSV** files locally.

---

## Features

1. **Firestore Integration**  
   Uses the Firebase Admin SDK to authenticate and access Firestore.

2. **Dynamic CSV Export**  
   Automatically detects and includes all fields from your Firestore documents, ensuring **no data is lost**.

3. **Easy Setup**  
   Simply point the script at your Firebase credentials JSON file, list the collections you want to export, and run.

---

## Prerequisites

1. **Python 3.6+**  
   Ensure you have Python 3.6 or higher installed on your system.

2. **Firebase Admin SDK Credentials**  
   You must have a Firebase service account JSON file.  
   - Go to [Firebase Console](https://console.firebase.google.com/)  
   - Navigate to **Project Settings**  
   - In the **Service Accounts** tab, click **Generate New Private Key**  
   - Store the downloaded JSON file somewhere secure.

3. **Dependencies**  
   Install required packages:
   ```bash
   pip install firebase-admin
   ```

---

## Usage

1. **Clone or Download** this repository.  
   ```bash
   git clone https://github.com/YourUsername/Firestore-CSV-Downloader.git
   cd Firestore-CSV-Downloader
   ```

2. **Update the Script**  
   - **Path to Credentials**: In the `download_firestore_csv.py` file, locate the line:  
     ```python
     cred = credentials.Certificate("path/to/your_firebase_credentials.json")
     ```  
     Replace `"path/to/your_firebase_credentials.json"` with the actual path to your service account JSON file.
   - **Collection Names**: In the `main()` function, edit:
     ```python
     collection_names = [
         "YourCollectionName1",
         # "YourCollectionName2",
         ...
     ]
     ```  
     Specify the collections you want to download.

3. **Run the Script**  
   ```bash
   python download_firestore_csv.py
   ```  
   This will:
   - Authenticate to Firestore using your credentials.
   - Retrieve all documents in the specified collections (skipping an `info` document if found).
   - Generate CSV files named `<CollectionName>.csv` in the same directory.

4. **Inspect CSV Files**  
   After successful execution, you should see CSV files in your project folder. Open them with any CSV viewer (Excel, Google Sheets, etc.) or parse them programmatically for your needs.

---

## Script Overview

- **`get_all_user_inputs(db, collection_name)`**  
  Fetches all documents from the given Firestore collection, skipping the `info` document. Extracts user messages from the `interactions` field, **excluding bot responses**, and captures all other fields.

- **`generate_dynamic_csv(all_messages)`**  
  Takes a dictionary of messages and dynamically generates CSV content. Automatically detects all unique fields and adds them as columns.

- **`main()`**  
  The entry point of the script, which initializes Firebase, specifies collections, and writes CSV files.

---

## Troubleshooting

- **Authentication Failure**  
  Ensure your service account JSON file is valid and that you've provided the correct path.
- **Module Not Found**  
  Make sure you have installed `firebase-admin`:
  ```bash
  pip install firebase-admin
  ```
- **Insufficient Permissions**  
  Your service account must have **FireStore Admin** permissions to read the database.

---

## Contributing

Feel free to submit a Pull Request or open an Issue if you have suggestions or find a bug.

---
