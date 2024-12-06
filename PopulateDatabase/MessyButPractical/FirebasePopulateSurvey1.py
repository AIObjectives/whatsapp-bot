
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

# def initialize_event_collection(event_id, event_name, event_location, event_background, event_date, extraction_settings, bot_topic, bot_aim, bot_principles, bot_personality, bot_additional_prompts, questions, languages):
#     """Initializes the Firestore collection and stores event info, bot settings, and survey questions within the 'info' document."""
#     collection_ref = db.collection(f'AOI_{event_id}')
#     info_doc_ref = collection_ref.document('info')
    
#     # Assign unique IDs to each question and format them into a dictionary
#     formatted_questions = []
#     for idx, question in enumerate(questions):
#         formatted_questions.append({
#             "id": idx,  # Assign a unique ID (index) to each question
#             "text": question,
#             "asked_count": 0
#         })
    
#     # Set the main event info in the 'info' document along with extraction settings, bot configuration, and languages
#     info_doc_ref.set({
#         'event_initialized': True,
#         'event_name': event_name,
#         'event_location': event_location,
#         'event_background': event_background,
#         'event_date': event_date,
#         'welcome_message': f"Welcome to the {event_name} at {event_location}. You can now start sending text and audio messages. To change your name, type 'change name [new name]'. To change your event, type 'change event [event name]'.",
#         'extraction_settings': extraction_settings,
#         'bot_topic': bot_topic,
#         'bot_aim': bot_aim,
#         'bot_principles': bot_principles,
#         'bot_personality': bot_personality,
#         'bot_additional_prompts': bot_additional_prompts,
#         'languages': languages,
#         'questions': formatted_questions  # Each question has "id", "text", and "asked_count"
#     })
    
#     logger.info(f"Event '{event_name}' initialized with {len(questions)} questions.")


def initialize_event_collection(event_id, event_name, event_location, event_background, event_date, extraction_settings, bot_topic, bot_aim, bot_principles, bot_personality, bot_additional_prompts, questions, languages, initial_message, completion_message):
    """Initializes the Firestore collection and stores event info, bot settings, and survey questions within the 'info' document."""
    collection_ref = db.collection(f'AOI_{event_id}')
    info_doc_ref = collection_ref.document('info')
    
    # Assign unique IDs to each question and format them into a dictionary
    formatted_questions = []
    for idx, question in enumerate(questions):
        formatted_questions.append({
            "id": idx,  # Assign a unique ID (index) to each question
            "text": question,
            "asked_count": 0
        })
    
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
        'bot_topic': bot_topic,
        'bot_aim': bot_aim,
        'bot_principles': bot_principles,
        'bot_personality': bot_personality,
        'bot_additional_prompts': bot_additional_prompts,
        'languages': languages,
        'questions': formatted_questions  # Each question has "id", "text", and "asked_count"
    })
    
    logger.info(f"Event '{event_name}' initialized with {len(questions)} questions.")




# Define event details and survey questions
event_id = "Dec3FullDynamicSurvey"
event_name = "Dec3FullDynamicSurvey"
event_location = "Global"
event_background = "A survey exploring the experiences and challenges of LBQ+ women in various sectors."
event_date = "2024-12-01"
extraction_settings = {
    "name_extraction": True,
    "age_extraction": False,
    "gender_extraction": False,
    "region_extraction": False
}
bot_topic = "Experiences and challenges of LBQ+ women in the workplace and community"
bot_aim = "To gather insights on the unique challenges and opportunities of LBQ+ women globally."
bot_principles = [
    "Maintain an open and non-judgmental tone",
    "Respect privacy and confidentiality",
    "Encourage honest and thoughtful responses"
]
bot_personality = "Empathetic, supportive, and respectful"
bot_additional_prompts = [
    "What are some unique challenges you face?",
    "How can your workplace better support LBQ+ individuals?"
]
languages = ["English", "French", "Swahili"]  # Specify the main languages for this event

# Define the list of questions (English versions)
questions = [
    #"How do you identify in terms of your (a) gender and (b) sexuality? Do you present as feminine, masculine, or non-binary?",
    # "Who have you shared your identity with, and how do you decide who to tell?",
    # "How well-known is your identity at your workplace? What factors influenced this?",
    # "Can you describe your current job situation? What type of work do you do, how did you find the job, what is your level of seniority, how long have you been in this position, and how satisfied are you with your career?",
    # "What have been the biggest challenges or barriers you’ve faced in your career journey so far?",
    # "In what ways has being a woman, trans, or non-binary influenced your opportunities and challenges in the workplace or business?",
    # "As an LBQ+ woman, what specific challenges do you encounter when trying to live your life fully and safely while also making a living?",
    # "How do societal attitudes towards LGBQ+ individuals affect your ability to earn money or advance in your career?",
    # "Can you describe instances of discrimination you have faced as an LBQ+ woman at work or in business? How did you respond to these situations?",
    # "Share a time when you felt truly supported as an LBQ+ woman in your workplace or business. What made that experience stand out?",
    # "What changes do you wish to see in your community or workplace to create more opportunities for LBQ+ women to thrive?",
    # "What role do you believe LGBTQI organizations or allies should play in improving the financial well-being of LBQ+ women?",
    # "How do you think your identity has shaped your career choices or business decisions?",
    # "What types of support do you think would be most beneficial for LBQ+ women in your community to succeed in their careers or businesses?",
    # "Is there anything else you’d like to share regarding your experiences as an LBQ+ woman that you think is important for us to know?"


    "How widely do you share your LBQ identity with people, and how do you decide who to discuss it with?",
    "How widely known is your identity in your workplace? Did you tell people, or did they find out in another way?",
    "Please tell us about how you earn an income. For example: what type of work do you do: how did you find this work, is it in the formal or informal sector; what is your level of seniority, how long have you been in this position and how satisfied are you with your current work situation?",
    "What have been the biggest barriers or challenges you’ve faced in earning an income?",
    "In what ways does being a woman (or non-binary or trans) impacted your choices, opportunities, and challenges in finding work, earning an income, or advancing in your career?",
    "As an LBQ+ woman, what are the biggest challenges you face in living your life fully and safely while earning an income?",
    "How do people’s attitudes in your community or place of work about LGBQ+ people affect your ability to earn money or grow in your career?",
    "What experiences of discrimination have you had as an LBQ+ woman in your workplace or business? How did you handle it?",
    "Can you share a time when you felt supported as an LBQ+ woman at work or in business? What made the experience special?",
    "What changes would you like to see in your community or workplace to create more opportunities for LBQ+ women to succeed?",
    "What do you think LGBTQI organizations or allies could do to improve the financial well- being of LBQ+ women?",
    "What types of support do you think would be most beneficial for LBQ+ women in your community to succeed in their careers or business?",
    "How do you think your identity as an LBQ woman has influenced the decisions you have made about how to earn a living?",
    "Is there anything else you'd like to share about this topic?",



]

# # Initialize the event with questions
# initialize_event_collection(
#     event_id,
#     event_name,
#     event_location,
#     event_background,
#     event_date,
#     extraction_settings,
#     bot_topic,
#     bot_aim,
#     bot_principles,
#     bot_personality,
#     bot_additional_prompts,
#     questions,
#     languages
# )

# Define the initial and completion messages
initial_message = """Thank you for agreeing to participate. We want to assure you that none of the data you provide will be directly linked back to you. Your identity is protected through secure and encrypted links. How would you like to be addressed during this session? (Please feel free to use your own name, or another name.)"""

completion_message = """Congratulations, you’ve completed the survey! Thank you so much for taking the time to share your experiences. Your input will help Utopia Network Kenya create programs and advocate for meaningful change. If you have any questions, concerns, or feedback, please don’t hesitate to contact us. Your voice matters, and we deeply appreciate your participation."""

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
    questions,
    languages,
    initial_message,      # Add this line
    completion_message    # Add this line
)
