

import firebase_admin
from firebase_admin import credentials, firestore
from fastapi import FastAPI, Form, Response
import logging
from uuid import uuid4

cred = credentials.Certificate('xxx.json')
firebase_admin.initialize_app(cred)
db = firestore.client()

# FastAPI app initialization
#app = FastAPI()


# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
def add_question_to_event(event_id, new_question):
    """Adds a new question to the 'questions' array in the 'info' document for the specified event."""
    collection_ref = db.collection(f'AOI_{event_id}')
    info_doc_ref = collection_ref.document('info')
    
    # Retrieve the current questions from Firestore
    info_data = info_doc_ref.get().to_dict()
    if not info_data or 'questions' not in info_data:
        raise ValueError("The 'info' document or 'questions' field does not exist.")
    
    # Get the current questions and calculate the new ID
    current_questions = info_data['questions']
    new_id = len(current_questions)  # Assign the next ID
    
    # Append the new question
    new_question_entry = {
        "id": new_id,
        "text": new_question,
        "asked_count": 0
    }
    current_questions.append(new_question_entry)
    
    # Update the document with the modified questions
    info_doc_ref.update({"questions": current_questions})
    logger.info(f"Added new question to event '{event_id}': {new_question}")

# Define the new question
new_question_text = "Q15.Reflecting on your experiences, is there anything else you’d like to share about the challenges, successes, or support systems that have shaped your journey?"

# Call the function to add the question
add_question_to_event("Utopia_Network", new_question_text)
