import firebase_admin
from firebase_admin import credentials, firestore
import logging

# 1) Initialize Firebase
#    Change the path below to the location of your Firebase service account JSON
cred = credentials.Certificate('...')
firebase_admin.initialize_app(cred)
db = firestore.client()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def initialize_event_collection(event_id, event_name, event_location, event_background, event_date, languages, initial_message, completion_message):
    """
    Creates (or overwrites) the Firestore document for this event_id under 'info'.
    This sets the entire 'extra_questions' block at once.
    
    WARNING: This will overwrite existing extra_questions and other fields in 'info'.
    """
    collection_ref = db.collection(f'AOI_{event_id}')
    info_doc_ref = collection_ref.document('info')
    
    # Example extra questions dict
    extra_questions = {
        "ExtraQuestion1": {
            "enabled": True,
            "id": "extract_name_with_llm",   # function ID if needed
            "text": "現在請您於對話框輸入希望在呈現意見時的暱稱，中英文皆可",
            "order": 1
        },
        "ExtraQuestion2": {
            "enabled": True,
            "text": "現在請您於對話框輸入學號",
            "order": 2
        },
        "ExtraQuestion3": {
            "enabled": True,
            "text": "現在請您於對話框輸入所屬學校",
            "order": 3
        },
        "ExtraQuestion4": {
            "enabled": False,   # This one won't be asked
            "text": "Any special requests for the organizers?",
            "order": 4
        }
    }

    info_doc_ref.set({
        'event_initialized': True,
        'event_name': event_name,
        'event_location': event_location,
        'event_background': event_background,
        'event_date': event_date,
        'welcome_message': f"歡迎來到 TAICA 課程，現在機器人已開始聆聽您的發言",
        'initial_message': initial_message,
        'completion_message': completion_message,
        'languages': languages,
        'extra_questions': extra_questions
    })
    
    logger.info(f"[initialize_event_collection] Event '{event_name}' initialized/overwritten with extra questions.")


def add_extra_question(event_id, question_key, text, enabled=True, order=1, function_id=None):
    """
    Adds or updates a single extra question to the existing 'extra_questions' map
    inside the 'info' document for the given event_id.
    """
    info_doc_ref = db.collection(f'AOI_{event_id}').document('info')
    doc_snapshot = info_doc_ref.get()

    if not doc_snapshot.exists:
        logger.warning(f"Event '{event_id}' does not exist or has no 'info' doc. Please initialize it first.")
        return

    data = doc_snapshot.to_dict() or {}
    extra_questions = data.get('extra_questions', {})

    # Build a new question dictionary
    new_question = {
        "enabled": enabled,
        "text": text,
        "order": order
    }
    if function_id:
        new_question["id"] = function_id

    # Insert or update
    extra_questions[question_key] = new_question

    # Update Firestore
    info_doc_ref.update({
        "extra_questions": extra_questions
    })
    logger.info(f"[add_extra_question] Added/updated question '{question_key}' in event '{event_id}'.")


if __name__ == "__main__":
    # ---------------------------------------------------------------------
    #  EXAMPLE USAGE 1: Initialize a brand new event (OVERWRITES everything)
    # ---------------------------------------------------------------------
    event_id = "xxx"
    event_name = "xxx"
    event_location = "Taiwan"
    event_background = "You should already know this and you can ask your professor!"
    event_date = "2025"
    languages = ["Mandarin", "English"]
    initial_message = "歡迎您使用本課程指定的 Talk to the City 線上公共討論系統。為了確認您的課堂參與，系統將請您依序提供所屬學校與學號，並以加密方式傳輸。這些資料僅用於記錄您的參與狀況，並於每週記錄完成後刪除。本課程僅依據您是否參與來評分，討論內容則不列入評分。"
    completion_message = "Thank you for participating in this event. Your responses have been recorded."

    initialize_event_collection(
        event_id,
        event_name,
        event_location,
        event_background,
        event_date,
        languages,
        initial_message,
        completion_message
    )

    # ---------------------------------------------------------------------
    #  EXAMPLE USAGE 2: Add or update a single question
    #  (Does NOT overwrite other existing questions)
    # ---------------------------------------------------------------------
    # add_extra_question(
    #     event_id="DemoEvent2025",
    #     question_key="ExtraQuestion5",
    #     text="What is your favorite color?",
    #     enabled=True,
    #     order=5,
    #     function_id=None
    # )

    # add_extra_question(
    #     event_id="DemoEvent2025",
    #     question_key="ExtraQuestion6",
    #     text="Please tell me more about your background.",
    #     enabled=True,
    #     order=6,
    #     function_id=None
    # )

    # You can comment out one or the other example usage block as needed.
    # Just run this file to update your Firestore accordingly.
