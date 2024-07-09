from firebase_admin import credentials, initialize_app, get_app

def initialize_firebase(firebase_credentials):
    try:
        app = get_app()
    except ValueError:
        cred = credentials.Certificate(firebase_credentials)
        app = initialize_app(cred)
    return app

def get_all_user_inputs(db):
    """ Retrieve all user messages from Firestore across all documents in the 'whatsapp_conversations' collection """
    try:
        conversations = db.collection('whatsapp_conversations').stream()
        all_messages = {}
        for conversation in conversations:
            doc_data = conversation.to_dict()
            phone_number = conversation.id  # The document ID is the phone number
            user_messages = [interaction['message'] for interaction in doc_data.get('interactions', []) if 'message' in interaction]
            all_messages[phone_number] = user_messages
        return all_messages
    except Exception as e:
        print(f"An error occurred: {e}")
        return {}
