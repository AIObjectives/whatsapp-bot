
## add a seperate fillow up question per question as lel 9 asking to eloberate 0 tracking that too!



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


def initialize_event_collection(event_id, event_name, event_location, event_background, event_date, extraction_settings, languages, initial_message, completion_message):
    """Initializes the Firestore collection and stores event info, bot settings, and survey questions within the 'info' document."""
    collection_ref = db.collection(f'AOI_{event_id}')
    info_doc_ref = collection_ref.document('info')
    
    
    # Set the main event info in the 'info' document along with extraction settings, bot configuration, and languages
    info_doc_ref.set({
        'event_initialized': True,
        'event_name': event_name,
        'event_location': event_location,
        'event_background': event_background,
        'event_date': event_date,
        'welcome_message': f"Welcome to the {event_name} at {event_location}. You can now start sending text and audio messages. To change your name, type 'change name [new name]'. To change your event, type 'change event [event name]'.",
        'initial_message': initial_message,
        'completion_message': completion_message,
        'extraction_settings': extraction_settings,
        'languages': languages,
    })
    
    logger.info(f"Event '{event_name}' initialized .")




# Define event details and survey questions
event_id = "Dec3FullDynamicListenerMode"
event_name = "Dec3FullDynamicListenerMode"
event_location = "Global"
event_background = "A survey exploring the experiences and challenges of LBQ+ women in various sectors."
event_date = "2024-12-01"
extraction_settings = {
    "name_extraction": True,
    "age_extraction": False,
    "gender_extraction": False,
    "region_extraction": False
}

languages = ["English", "French", "Swahili"]  # Specify the main languages for this event



# Define the initial and completion messages
initial_message = """Thank you for agreeing to participate. We want to assure you that none of the data you provide will be directly linked back to you. Your identity is protected through secure and encrypted links. How would you like to be addressed during this session? (Please feel free to use your own name, or another name.)"""

completion_message = """Congratulations, you’ve completed the survey! Thank you so much for taking the time to share your experiences. Your input will help Utopia Network Kenya create programs and advocate for meaningful change. If you have any questions, concerns, or feedback, please don’t hesitate to contact us. Your voice matters, and we deeply appreciate your participation."""

# Initialize the event with questions and messages
initialize_event_collection(
    event_id,
    event_name,
    event_location,  # Fix: event_location is in the correct place
    event_background,
    event_date,
    extraction_settings,
    languages,
    initial_message,
    completion_message
)
