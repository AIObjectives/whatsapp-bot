import firebase_admin
from firebase_admin import credentials, firestore
import json
import os
class Database:
    def __init__(self):
        # Replace 'path_to_your_service_account_json' with your Firebase project credentials
        # cred = credentials.Certificate('/Users/emreturan/Desktop/firebase/aoiwhatsappbot-firebase-adminsdk-rki5n-9526831994.json')
        # firebase_admin.initialize_app(cred)
        firebase_credentials = json.loads(os.environ.get('FIREBASE_CREDENTIALS'))

# Initialize Firebase using the credentials from environment variable
        cred = credentials.Certificate(firebase_credentials)
        firebase_admin.initialize_app(cred)
        self.client = firestore.client()

    def get_document(self, collection, document_id):
        doc_ref = self.client.collection(collection).document(document_id)
        doc = doc_ref.get()
        return doc.to_dict() if doc.exists else None

    def update_document(self, collection, document_id, data):
        doc_ref = self.client.collection(collection).document(document_id)
        doc_ref.update(data)

    def create_document(self, collection, document_id, data):
        doc_ref = self.client.collection(collection).document(document_id)
        doc_ref.set(data)
