import firebase_admin
from firebase_admin import credentials, firestore
from survey_management.add_question_to_survey.add_question import add_question_to_event
from survey_management.utils.logging_helpers import logger

# Initialize Firebase
cred = credentials.Certificate('xxx.json')
firebase_admin.initialize_app(cred)
db = firestore.client()

# Define the new question and event
event_id = "Utopia_Network"
new_question_text = "Q15.Reflecting on your experiences, is there anything else you’d like to share about the challenges, successes, or support systems that have shaped your journey?"

# Add the question to the event
try:
    add_question_to_event(db, event_id, new_question_text)
    logger.info("Question added successfully!")
except ValueError as e:
    logger.error(f"Error: {e}")
