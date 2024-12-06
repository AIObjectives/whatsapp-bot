from shared.firebase_setup import db
from shared.logger import logger
from openended_mode.config import OPENENDED_MODE_CONFIG


def initialize_event_collection(event_id, event_name, event_location, event_background, event_date, main_question):
    """Initializes the Firestore collection and stores event info for Open-Ended Mode."""
    collection_ref = db.collection(f"{OPENENDED_MODE_CONFIG['default_event_prefix']}_{event_id}")
    info_doc_ref = collection_ref.document('info')
    
    # Set the main event info in the 'info' document
    info_doc_ref.set({
        'event_initialized': True,
        'event_name': event_name,
        'event_location': event_location,
        'event_background': event_background,
        'event_date': event_date,
        'welcome_message': f"Welcome to the {event_name} at {event_location}. You can now start sending text and audio messages. To change your name, type 'change name [new name]'. To change your event, type 'change event [event name]'.",
        'initial_message': OPENENDED_MODE_CONFIG['initial_message'],
        'completion_message': OPENENDED_MODE_CONFIG['completion_message'],
        'extraction_settings': OPENENDED_MODE_CONFIG['extraction_settings'],
        'bot_topic': OPENENDED_MODE_CONFIG['bot_topic'],
        'main_question': main_question,
        'bot_aim': OPENENDED_MODE_CONFIG['bot_aim'],
        'bot_principles': OPENENDED_MODE_CONFIG['bot_principles'],
        'bot_personality': OPENENDED_MODE_CONFIG['bot_personality'],
        'bot_additional_prompts': OPENENDED_MODE_CONFIG['bot_additional_prompts'],
        'languages': OPENENDED_MODE_CONFIG['languages']
    })
    
    logger.info(f"Event '{event_name}' initialized with main question: {main_question}.")
