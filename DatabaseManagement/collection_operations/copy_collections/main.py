import firebase_admin
from firebase_admin import credentials, firestore
from collection_operations.copy_collections.copy_collection import copy_collection

# Firebase Initialization
cred = credentials.Certificate('xxx.json')
firebase_admin.initialize_app(cred)
db = firestore.client()

# Define source and target collection names
source_collection_name = 'whatsapp_conversations1'
target_collection_name = 'SearchForCommonGroundsDemo'

# Get references to the source and target collections
source_collection_ref = db.collection(source_collection_name)
target_collection_ref = db.collection(target_collection_name)

# Copy the collection
print(f"Copying collection '{source_collection_name}' to '{target_collection_name}'")
copy_collection(source_collection_ref, target_collection_ref)
print(f"Collection '{source_collection_name}' successfully copied to '{target_collection_name}'")
