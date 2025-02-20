# # always check 2 things - collection name and db credentials

# import csv
# from io import StringIO
# import firebase_admin
# from firebase_admin import credentials, firestore
# import pandas as pd  # Added for merging CSVs

# def get_all_user_inputs(db, collection_name):
#     """
#     Fetch all user messages (excluding bot responses) across documents in the collection.
#     """
#     try:
#         collection_data = db.collection(collection_name).stream()
#         all_messages = {}

#         for doc in collection_data:
#             # Skip the 'info' document if you want to exclude it
#             if doc.id == 'info':
#                 continue
            
#             doc_data = doc.to_dict()
#             phone_number = doc.id  # The document ID is the phone number

#             # Extract the user messages, skipping bot responses
#             user_messages = [
#                 interaction.get('message', '') for interaction in doc_data.get('interactions', []) 
#                 if isinstance(interaction, dict) and 'message' in interaction and 'response' not in interaction
#             ]

#             # Clean the messages by joining them without brackets/quotes
#             cleaned_messages = " ".join(user_messages).replace('[', '').replace(']', '').replace("'", "")
            
#             # Fetch the name (if available) and any additional fields, excluding unwanted fields
#             name = doc_data.get('name', '')  # The 'name' field
#             other_fields = {key: value for key, value in doc_data.items() 
#                             if key not in ['interactions', 'name', 'limit_reached_notified', 'event_id']}

#             # Store all fields dynamically, including 'name', 'comment-body', and any other fields
#             all_messages[phone_number] = {
#                 'name': name,
#                 'comment-body': cleaned_messages,
#                 'collection': collection_name,  # Track which collection the data came from
#                 **other_fields  # Merge any additional fields dynamically
#             }
#         return all_messages
#     except Exception as e:
#         print(f"An error occurred: {e}")
#         return {}

# def generate_dynamic_csv(all_messages, output_filename):
#     """
#     Generate and save CSV dynamically from all fields in user messages.
#     """
#     if not all_messages:
#         print(f"No data found for {output_filename}, skipping CSV generation.")
#         return None

#     all_keys = set()

#     # Collect all unique keys across documents
#     for doc_data in all_messages.values():
#         all_keys.update(doc_data.keys())

#     # Write headers (sorted for consistency)
#     headers = ['comment-id'] + sorted(all_keys)
    
#     # Write CSV content
#     csv_data = []
#     index = 1
#     for phone_number, doc_data in all_messages.items():
#         row = [index]  # Start with comment-id
#         row += [doc_data.get(key, '') for key in sorted(all_keys)]
#         csv_data.append(row)
#         index += 1

#     # Save CSV locally
#     df = pd.DataFrame(csv_data, columns=headers)
#     df.to_csv(output_filename, index=False, encoding="utf-8")
    
#     print(f"CSV saved as: {output_filename}")
#     return df  # Return DataFrame for merging later

# def main():
#     """
#     Main function to:
#     1. Initialize Firebase Admin SDK with local credentials.
#     2. Retrieve documents from specified collections.
#     3. Generate individual CSVs & merge them into one big CSV.
#     """
#     # === 1. Initialize Firebase with your credentials ===
#     cred = credentials.Certificate('xxx.json')
#     firebase_admin.initialize_app(cred)
#     db = firestore.client()

#     # === 2. Specify collections to download ===
#     collection_names = [
#         #"Week1_TAICA_COPY",
#         #"Week2_TAICA_COPY",
#         "AOI_3_TAICA_3",
#         #"Week4_TAICA_COPY",
#         "AOI_5_TAICA_5"
#     ]

#     # Store all dataframes for merging
#     all_dfs = []

#     # === 3. Fetch data & save CSVs ===
#     for collection_name in collection_names:
#         print(f"Fetching data from collection: {collection_name}")
#         all_messages = get_all_user_inputs(db, collection_name)
        
#         # Generate CSV & collect for merging
#         csv_filename = f"{collection_name}.csv"
#         df = generate_dynamic_csv(all_messages, csv_filename)
#         if df is not None:
#             all_dfs.append(df)

#     # === 4. Merge all CSVs into one final file ===
#     if all_dfs:
#         merged_df = pd.concat(all_dfs, ignore_index=True)
#         merged_filename = "Merged_All_Collections.csv"
#         merged_df.to_csv(merged_filename, index=False, encoding="utf-8")
#         print(f"✅ Merged CSV saved as: {merged_filename}")

# if __name__ == "__main__":
#     main()




#####


# Always check 2 things - collection name and db credentials

import csv
from io import StringIO
import firebase_admin
from firebase_admin import credentials, firestore
import pandas as pd  # Pandas for merging CSVs

def get_all_user_inputs(db, collection_name):
    """
    Fetch all user messages (excluding bot responses) across documents in the collection.
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
                'collection': collection_name,  # Track which collection the data came from
                **other_fields  # Merge any additional fields dynamically
            }
        return all_messages
    except Exception as e:
        print(f"An error occurred: {e}")
        return {}

def generate_dynamic_csv(all_messages, output_filename, start_id):
    """
    Generate and save CSV dynamically from all fields in user messages.
    """
    if not all_messages:
        print(f"No data found for {output_filename}, skipping CSV generation.")
        return None, start_id

    all_keys = set()

    # Collect all unique keys across documents
    for doc_data in all_messages.values():
        all_keys.update(doc_data.keys())

    # Write headers (sorted for consistency)
    headers = ['comment-id'] + sorted(all_keys)
    
    # Write CSV content
    csv_data = []
    comment_id = start_id  # Start from the last highest ID
    for phone_number, doc_data in all_messages.items():
        row = [comment_id]  # Set comment-id
        row += [doc_data.get(key, '') for key in sorted(all_keys)]
        csv_data.append(row)
        comment_id += 1  # Increment ID for next row

    # Save CSV locally
    df = pd.DataFrame(csv_data, columns=headers)
    df.to_csv(output_filename, index=False, encoding="utf-8")
    
    print(f"CSV saved as: {output_filename}")
    return df, comment_id  # Return DataFrame for merging later and new starting comment-id

def main():
    """
    Main function to:
    1. Initialize Firebase Admin SDK with local credentials.
    2. Retrieve documents from specified collections.
    3. Generate individual CSVs & merge them into one big CSV.
    """
    # === 1. Initialize Firebase with your credentials ===
    cred = credentials.Certificate('xx.json')
    firebase_admin.initialize_app(cred)
    db = firestore.client()

    # === 2. Specify collections to download ===
    collection_names = [
        "AOI_1_TAICA_1",
        "AOI_2_TAICA_2",
        "AOI_3_TAICA_3",
        "AOI_4_TAICA_4",
        "AOI_5_TAICA_5"
    ]

    # Store all dataframes for merging
    all_dfs = []
    start_id = 1  # Initial ID for the first row

    # === 3. Fetch data & save CSVs ===
    for collection_name in collection_names:
        print(f"Fetching data from collection: {collection_name}")
        all_messages = get_all_user_inputs(db, collection_name)
        
        # Generate CSV & collect for merging
        csv_filename = f"{collection_name}.csv"
        df, start_id = generate_dynamic_csv(all_messages, csv_filename, start_id)  # Pass start_id to maintain sequence
        if df is not None:
            all_dfs.append(df)

    # === 4. Merge all CSVs into one final file ===
    if all_dfs:
        merged_df = pd.concat(all_dfs, ignore_index=True)
        merged_filename = "Merged_All_Collections_incrementweek1.csv"
        merged_df.to_csv(merged_filename, index=False, encoding="utf-8")
        print(f"✅ Merged CSV saved as: {merged_filename}")

if __name__ == "__main__":
    main()
