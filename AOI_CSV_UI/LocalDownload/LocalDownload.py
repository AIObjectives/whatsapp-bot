#!/usr/bin/env python3

import csv
from io import StringIO
import firebase_admin
from firebase_admin import credentials, firestore

def get_all_user_inputs(db, collection_name):
    """
    Fetch all user messages (excluding bot responses) across documents in the collection,
    and any additional fields. This is based on your original code.
    """
    try:
        collection_data = db.collection(collection_name).stream()
        all_messages = {}

        for doc in collection_data:
            # Skip the 'info' document if you want to exclude it
            if doc.id == 'info':
                continue
            
            doc_data = doc.to_dict()
            phone_number = doc.id  # The document ID is the phone number

            # Extract the user messages, skipping bot responses
            user_messages = [
                interaction.get('message', '') for interaction in doc_data.get('interactions', []) 
                if isinstance(interaction, dict) and 'message' in interaction and 'response' not in interaction
            ]

            # Clean the messages by joining them without brackets/quotes
            cleaned_messages = " ".join(user_messages).replace('[', '').replace(']', '').replace("'", "")
            
            # Fetch the name (if available) and any additional fields, excluding unwanted fields
            name = doc_data.get('name', '')  # The 'name' field
            other_fields = {key: value for key, value in doc_data.items() 
                            if key not in ['interactions', 'name', 'limit_reached_notified', 'event_id']}

            # Store all fields dynamically, including 'name', 'comment-body', and any other fields
            all_messages[phone_number] = {
                'name': name,
                'comment-body': cleaned_messages,
                **other_fields  # Merge any additional fields dynamically
            }
        return all_messages
    except Exception as e:
        print(f"An error occurred: {e}")
        return {}

def generate_dynamic_csv(all_messages):
    """
    Generate CSV content dynamically from all fields in user messages.
    Returns the CSV content as a string.
    """
    output = StringIO()
    all_keys = set()

    # Collect all unique keys across documents
    for phone_number, doc_data in all_messages.items():
        all_keys.update(doc_data.keys())

    # Write headers (sorted for consistency)
    writer = csv.writer(output)
    headers = ['comment-id'] + sorted(all_keys)
    writer.writerow(headers)

    # Write each row
    index = 1
    for phone_number, doc_data in all_messages.items():
        row = [index]  # Start with comment-id
        row += [doc_data.get(key, '') for key in sorted(all_keys)]
        writer.writerow(row)
        index += 1

    return output.getvalue()

def main():
    """
    Main function to:
    1. Initialize Firebase Admin SDK with local credentials.
    2. Retrieve documents from specified collections.
    3. Generate and save CSV files locally.
    """
    # === 1. Initialize Firebase with your credentials ===
    # Replace with the path to your actual credentials JSON file
    cred = credentials.Certificate("path/to/your_firebase_credentials.json")

    firebase_admin.initialize_app(cred)
    
    db = firestore.client()

    # === 2. Specify which collections to download ===
    collection_names = [
        "enteryourcollectionnamehere",
        # "YourCollectionName2",
        # Add more as needed...
    ]

    # === 3. For each collection, generate CSV and save locally ===
    for collection_name in collection_names:
        print(f"Fetching data from collection: {collection_name}")
        all_messages = get_all_user_inputs(db, collection_name)
        
        # Generate CSV content
        csv_content = generate_dynamic_csv(all_messages)
        
        # Save to local file
        output_filename = f"{collection_name}.csv"
        with open(output_filename, "w", encoding="utf-8", newline="") as f:
            f.write(csv_content)
        
        print(f"CSV saved as: {output_filename}")

if __name__ == "__main__":
    main()
