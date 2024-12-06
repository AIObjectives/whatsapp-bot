from firebase_admin import credentials, firestore, initialize_app
from decouple import config
import logging

# Initialize Firebase
cred = credentials.Certificate(config("FIREBASE_CREDENTIALS"))
initialize_app(cred)
db = firestore.client()

# Firestore interaction functions
def get_event_info(event_id):
    try:
        event_info_ref = db.collection(f'AOI_{event_id}').document('info')
        event_info_doc = event_info_ref.get()
        return event_info_doc.to_dict() if event_info_doc.exists else {}
    except Exception as e:
        logging.error(f"Error fetching event info: {e}")
        return {}

def validate_event_id(event_id):
    try:
        collections = db.collections()
        valid_event_ids = [
            collection.id.replace("AOI_", "") for collection in collections if collection.id.startswith("AOI_")
        ]
        return event_id in valid_event_ids
    except Exception as e:
        logging.error(f"Error validating event ID: {e}")
        return False
