
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


def initialize_event_collection(event_id, event_name, event_location, event_background, event_date, extraction_settings, bot_topic, bot_aim, bot_principles, bot_personality, bot_additional_prompts, main_question, languages, initial_message, completion_message):
    """Initializes the Firestore collection and stores event info, bot settings, and survey questions within the 'info' document."""
    collection_ref = db.collection(f'AOI_{event_id}')
    info_doc_ref = collection_ref.document('info')
    
    # Define the follow-up questions
    follow_up_questions = [
        "Can you elaborate on what stood out to you the most about X?",
        "How did X make you feel, and why do you think that is?",
        "What aspects of X do you think work well, and what could be improved?",
        "Can you share an example or experience that relates to your impression of X?",
        "What specific elements of X influenced your thoughts the most?",
        "Did anything about X surprise you or challenge your expectations?",
        "If you were to explain X to someone else, how would you describe it?",
        "What additional context or information do you think would be helpful when discussing X?",
        "Are there any aspects of X that you think are being overlooked or under-discussed?",
        "What would you recommend as the next step or action based on your impressions of X?",
        "Do you think X aligns with your initial expectations? Why or why not?",
        "What do you think could be added to X to make it more engaging or effective?",
        "How does X compare to similar experiences or ideas you've encountered before?",
        "What questions or concerns come to mind when you think about X?",
        "If you had to summarize your overall impression of X in one sentence, what would it be?"
    ]

    # Add a toggle for the follow-up questions
    follow_up_toggle = {
        "enabled": True,  # Set to False to turn off follow-up questions
        "questions": follow_up_questions
    }

    # Set the main event info in the 'info' document along with extraction settings, bot configuration, and languages
    info_doc_ref.set({
        'event_initialized': True,
        'event_name': event_name,
        'event_location': event_location,
        'event_background': event_background,
        'event_date': event_date,
        'welcome_message': f"Welcome to the {event_name} at {event_location}. You can now start sending text and audio messages. To change your name, type 'change name [new name]'. To change your event, type 'change event [event name]'. Here is the first question:",
        'initial_message': initial_message,
        'completion_message': completion_message,
        'extraction_settings': extraction_settings,
        'bot_topic': bot_topic,
        'main_question': main_question,
        'bot_aim': bot_aim,
        'bot_principles': bot_principles,
        'bot_personality': bot_personality,
        'bot_additional_prompts': bot_additional_prompts,
        'languages': languages,
        'follow_up_questions': follow_up_toggle  # Add follow-up questions and toggle
    })
    
    logger.info(f"Event '{event_name}' initialized .")

# Define event details and survey questions
event_id = "xxx"
event_name = "xxx"
main_question = "What could make you change your mind about who you would vote for?"
event_location = "Global"
event_background = "A nationwide discussion on what could influence voters' decisions in upcoming elections."
event_date = "2025-15-01"
extraction_settings = {
    "name_extraction": True,
    "age_extraction": False,
    "gender_extraction": False,
    "region_extraction": False
}
bot_topic = "Experiences and challenges of LBQ+ women in the workplace and community"
bot_aim = "Encourage users to reflect on factors that could influence their voting decisions."
bot_principles = [
    "Avoid repeating user responses verbatim. Instead, acknowledge their input with concise and meaningful replies, such as 'Thank you for your input' or similar",
    "Respect privacy and confidentiality",
    "Encourage honest and thoughtful responses"
]
bot_personality = "Empathetic, supportive, and respectful"
bot_additional_prompts = [
    "What are some unique challenges you face?",
    "xxx"
]
languages = ["English", "French", "Swahili"]  # Specify the main languages for this event

# Define the initial and completion messages
initial_message = """Thank you for agreeing to participate. We want to assure you that none of the data you provide will be directly linked back to you. Your identity is protected through secure and encrypted links. How would you like to be addressed during this session? (Please feel free to use your own name, or another name.)"""

completion_message = """Thank you for sharing your thoughts; it's been insightful exploring what influences your voting decisions. If there's anything else you'd like to discuss or reflect on, feel free to ask, or we can end the session here."""

# Initialize the event with questions and messages
initialize_event_collection(
    event_id,
    event_name,
    event_location,
    event_background,
    event_date,
    extraction_settings,
    bot_topic,
    bot_aim,
    bot_principles,
    bot_personality,
    bot_additional_prompts,
    main_question,
    languages,
    initial_message,
    completion_message
)
