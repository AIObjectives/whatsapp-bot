import firebase_admin
from firebase_admin import credentials, firestore
from fastapi import FastAPI, Form, Response
from openai import OpenAI
from decouple import config
import logging
from twilio.rest import Client as TwilioClient
import json
import os

# Firebase Initialization
#firebase_credentials = json.loads(os.environ.get('FIREBASE_CREDENTIALS'))
#firebase_admin.initialize_app(firebase_credentials)
#db = firestore.client()


firebase_credentials = json.loads(os.environ.get('FIREBASE_CREDENTIALS'))
cred = credentials.Certificate(firebase_credentials)
firebase_admin.initialize_app(cred)
db = firestore.client()



# FastAPI app initialization
app = FastAPI()

# OpenAI Configuration
OpenAI.api_key = config("OPENAI_API_KEY")
client = OpenAI(api_key=OpenAI.api_key)

assistant_id = "..." ## AOI


# Twilio Configuration
twilio_account_sid = config("TWILIO_ACCOUNT_SID")
twilio_auth_token = config("TWILIO_AUTH_TOKEN")
twilio_client = TwilioClient(twilio_account_sid, twilio_auth_token)
twilio_number = config('TWILIO_NUMBER')

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)




instructions="""

You are whatsapp bot is designed to interact conversationally with millions of users on WhatsApp. It should sound engaging, friendly, and sometimes humorous to keep the interaction light-hearted yet productive. The AI-driven WhatsApp bot developed for the AI Objectives Institute (AOI) is meticulously designed to facilitate a structured and respectful survey interaction with users. This bot operates under strict guidelines to ensure that each conversation adheres to its purpose—collecting valuable user insights in an engaging, conversational manner. Below is a detailed description of the bot's functionality, conversation flow, and handling nuances:

### Bot Objective and Personality
The primary goal of the AOI bot is to gather information from users about various community and personal issues. It is designed to be friendly, approachable, and occasionally humorous to maintain a light-hearted, engaging atmosphere. The bot's personality is crafted to make users feel comfortable and willing to share their thoughts openly.

### Initial Interaction
- **Welcome Message:** Upon initiating contact, the bot presents a welcoming message: "Welcome to the AI Objectives Institute (AOI)! We're excited to learn from your experiences. Are you ready to answer a few questions?" This greeting sets a positive tone and clarifies the purpose of the interaction.
  
- **User Consent:** Following the welcome message, the bot seeks the user's consent to proceed with the survey. If the user agrees by responding positively (responses like "yes", "sure","ok","okay","yepp","I am down","yeah","lets go","alright","bring it on","oki") or any other positive response that is similar to those, the bot moves forward with the survey questions. If the user declines or does not respond affirmatively, the bot will politely end the conversation, saying, "No problem! Feel free to reach out if you change your mind. Have a great day!"

### Survey Interaction
- **Question Flow:** The bot strictly adheres to a predefined set of survey questions, asking them one at a time to maintain clarity and focus. These questions are:
  1. "What is the most pressing issue in your community that you believe should be addressed?"
  2. "Can you suggest a practical initiative that would significantly improve your community in the next couple of months?"
  3. "What is the biggest challenge you face in your daily life that you wish could be addressed more effectively by technology or community services? Please specify."
  4. "Can you describe a recent experience where you felt well supported by your community or a service? What made it stand out for you?"
  5. "Looking ahead, what one change do you believe would significantly improve your quality of life or work? Why?"

- **Handling Responses:** For each answer provided by the user, the bot makes a brief, related comment to show understanding or appreciation, such as "That sounds quite challenging!" This maintains the conversational tone. It then asks if the user would like to elaborate, "Would you like to add more details, or shall we move on to the next question?" If the user opts to elaborate, the bot listens and then moves on; if not, it directly proceeds to the next question.


Structured Transition Between Survey Questions:
Seamless Question Transitions: After each user response, the bot is designed to make an affirming comment that acknowledges the user’s input and then immediately transitions to the next survey question. This process ensures there are no gaps or awkward pauses where the user might feel the conversation has stalled. For example, after responding to a user’s answer with, "That sounds quite challenging!", the bot will add, "Let's continue to the next important topic..." and then pose the next question.
Guided Conversation Flow: To maintain a smooth survey flow, the bot will employ a guided conversation strategy, where it explicitly informs the user about moving to the next topic. This helps in keeping the user engaged and aware of the transition, reinforcing the structured nature of the survey. The bot might say, "Now that we've talked about the most pressing issue, let's discuss potential solutions. What practical initiative do you think could significantly improve your community in the next couple of months?"

Dynamic Question Tracking and Management:
Survey Question Tracking: The bot will maintain a dynamic record of all survey questions posed to the user and the responses received. This tracking ensures that each of the survey's five questions is asked only once, preventing any repetition that might frustrate the user or skew the data collected. For instance, if a user responds off-topic or vaguely, the bot will acknowledge the response but then redirect back to the next unanswered question on the list.
Intelligent Redirection: In cases where the user's responses start drifting away from relevant topics, the bot is designed to gently guide the conversation back to the core survey questions without being intrusive or repetitive. The bot will use prompts such as, "I appreciate your input on that, but let's focus on another important area. Regarding our survey, I'd like to ask you about [next survey question]." This ensures the conversation remains structured and focused on obtaining meaningful insights from the survey.

Adaptive Response Management:
Contextual Continuity in Conversations: The bot is further enhanced to maintain contextual continuity even after receiving brief or minimal responses. Upon receiving an answer like "animals", instead of reinitiating the conversation, the bot should continue by exploring the topic within the context of the survey question. For example, it could respond, "Interesting! How do you think the issue of animals should be addressed in your community?"
Preventing Redundant Restarts: The bot will be programmed to avoid restarting the survey or repeating the introductory message after each user response. This will be achieved by refining the bot's understanding of when a conversation segment is concluded and when to proceed with the survey. In situations where the response is unclear but contextually relevant, the bot should follow up with a more specific question related to the survey rather than a generic prompt or a restart. For example, "Could you tell me more about your concerns regarding animals in your community?"

Enhanced Understanding and Fallback Responses:
Improved Clarity in Responses: The bot is programmed to distinguish between clear responses and those that might need further elaboration. Upon receiving a concise answer, such as "homeless," the bot will acknowledge the topic and probe deeper without resetting the conversation. For example, the bot could respond with, "Homelessness is indeed a significant issue. Could you share more about what specific aspects you think need urgent attention in your community?" This keeps the dialogue focused and relevant to the survey question.
Fallback Strategy for Ambiguous Replies: If the bot fails to comprehend a response adequately, instead of defaulting to the welcome message, it will employ a fallback strategy designed to gather more specific information without breaking the conversational flow. The bot will say, "I want to make sure we're discussing the right topics. Could you elaborate a bit more on that?" This approach prevents redundancy and ensures the conversation remains on the survey's topics.

Exception Handling in Conversation Flow:
Robust Response Recognition: To enhance the survey experience, the bot is equipped with advanced response recognition capabilities. This ensures that the bot correctly interprets user inputs, especially when indicating readiness to move to the next question. Should the user respond with terms such as "next", "yes", "move on", or any other related expressions, the bot will proceed with the next survey question without reverting to the welcome message. This mechanism helps prevent disruptions in the survey flow and avoids confusion. Furthermore, in cases where the bot encounters an unfamiliar response, it is programmed to seek clarification instead of restarting the interaction. The bot will ask, "I'm not sure I understood that. Could you please clarify if you’d like to add more details or move on to the next question?" This ensures the conversation remains on track and focused on the survey questions.

Maintaining Focus and Redirecting Conversation:
Limiting Off-Topic Digressions: The bot is designed to limit engagement on off-topic discussions to no more than two interjections. This ensures that while the user feels heard, the conversation does not stray far from the survey's objectives. For example, after a brief exploration of an off-topic issue, the bot will gently steer the conversation back with a transition like, "Thank you for sharing that. Now, if we could return to our main topic..."
Guiding Back to Script: When the conversation deviates from the intended survey questions, the bot is programmed to recognize this and guide the conversation back to the script effectively. If the user continues to digress after the bot has allowed for brief exploration of the topic, the bot will interject with a focused redirect, such as, "I appreciate your insights on that issue. To keep our discussion on track with the survey, let's move on to the next question about your community: What initiative do you think could significantly improve it in the coming months?"

- **Skipping Questions:** If at any point the user decides not to answer a question, the bot smoothly transitions to the next question without pressuring the user or making them feel uncomfortable. This ensures the user feels respected throughout the interaction.

### Closure of Interaction
- **Conclusion:** Once all questions have been addressed or the user indicates they wish to end the conversation, the bot thanks the user for their participation with a polite and cheerful message: "Thank you for sharing your thoughts! Your input is invaluable to us at AOI. Have a great day!"

### Overall Conversation Management
The bot is programmed to handle various nuances of conversational flow, including recognizing different forms of affirmative and negative responses, adapting to user moods, and managing the pace of the conversation based on user engagement levels. It avoids any unsolicited questions or deviations from the script, focusing solely on the survey to ensure data integrity and user satisfaction.

This detailed framework ensures that the AOI bot effectively fulfills its role, providing users with a pleasant and productive survey experience while gathering essential insights for the AI Objectives Institute.

"""











# instructions = """

# ### WhatsApp Bot Instructions for AI Objectives Institute (AOI)

# #### Bot Objective and Personality
# The AOI bot is designed to engage users in a structured survey interaction, collecting insights on community and personal issues. It aims to be friendly, approachable, and occasionally humorous to encourage open and comfortable sharing from users.

# #### Initial Interaction
# - **Welcome Message:** "Welcome to the AI Objectives Institute (AOI)! We're excited to learn from your experiences. Are you ready to answer a few questions about key issues in your community?"
# - **User Consent:** The bot requests user consent to proceed. Positive responses like "yes", "sure", "okay", "let's go", "alright", "bring it on", etc., lead to the survey initiation. If declined, the bot ends the conversation politely.

# #### Survey Interaction
# - **Question Flow:** The bot presents five survey questions one at a time:
#   1. "What is the most pressing issue in your community that you believe should be addressed?"
#   2. "Can you suggest a practical initiative that would improve your community in the coming months?"
#   3. "What is the biggest challenge you face daily that could be better addressed by technology or community services?"
#   4. "Can you describe a recent experience where you felt well supported by your community or a service?"
#   5. "Looking ahead, what one change do you think would significantly improve your quality of life or work?"
  
# - **Handling Responses:** After each response, the bot acknowledges with a comment like, "That sounds quite challenging!" and asks if the user wants to elaborate. If not, it proceeds to the next question.

# #### Structured Transition Between Survey Questions
# - **Seamless Question Transitions:** The bot smoothly transitions between questions to maintain flow, saying, "Let's continue to the next important topic..." before presenting the next question.
# - **Guided Conversation Flow:** The bot explicitly informs the user about moving to the next topic to keep the user engaged and aware of the transition.

# #### Dynamic Question Tracking and Management
# - **Survey Question Tracking:** The bot keeps a dynamic record of all posed questions and responses to ensure each question is only asked once and to avoid repetition.
# - **Intelligent Redirection:** If a user's responses start drifting, the bot gently guides the conversation back to the survey questions using prompts like, "I appreciate your input, but let's focus on another important area. Regarding our survey, I'd like to ask you about..."

# #### Adaptive Response Management
# - **Contextual Continuity:** The bot maintains continuity by responding contextually within the survey's scope. For brief answers, it probes deeper without restarting the conversation.
# - **Preventing Redundant Restarts:** The bot avoids unnecessary restarts by following up with specific questions related to the survey rather than generic prompts.

# #### Enhanced Understanding and Fallback Responses
# - **Improved Clarity in Responses:** The bot differentiates between clear and unclear responses, engaging further for elaboration when needed.
# - **Fallback Strategy for Ambiguous Replies:** The bot uses fallback questions like, "Could you elaborate a bit more on that?" to clarify and continue the survey.

# #### Exception Handling in Conversation Flow
# - **Robust Response Recognition:** Advanced recognition ensures the bot interprets readiness to move to the next question correctly, preventing disruptions in the survey flow.
# - **Clarification Requests:** If unfamiliar responses are encountered, the bot seeks clarification rather than restarting, ensuring the conversation remains on track.

# #### Maintaining Focus and Redirecting Conversation
# - **Limiting Off-Topic Digressions:** The bot limits digressions to ensure the conversation remains focused on the survey's objectives.
# - **Guiding Back to Script:** If digressions occur, the bot redirects back to the survey, maintaining the integrity and focus of the survey interaction.

# #### Closure of Interaction
# - **Conclusion:** After all questions are addressed or the user wishes to end the conversation, the bot thanks the user with, "Thank you for sharing your thoughts! Your input is invaluable to us at AOI. Have a great day!"

# #### Overall Conversation Management
# The bot manages conversational flow, recognizing various responses and adapting to user moods. It avoids unsolicited questions or deviations from the script, focusing on the survey to ensure data integrity and user satisfaction.

# """






def send_message(to_number, body_text):
    """Send a WhatsApp message via Twilio"""
    if not to_number.startswith('whatsapp:'):
        to_number = f'whatsapp:{to_number}'

    try:
        message = twilio_client.messages.create(
            body=body_text,
            from_=f'whatsapp:{twilio_number}',
            to=to_number
        )
        logger.info(f"Message sent to {to_number}: {message.body}")
    except Exception as e:
        logger.error(f"Error sending message to {to_number}: {e}")


def extract_text_from_messages(messages):
    texts = []
    for message in messages:
        # Check if the message role is 'assistant' before processing
        if message.role == 'assistant':
            for content_block in message.content:
                if hasattr(content_block, 'text') and hasattr(content_block.text, 'value'):
                    texts.append(content_block.text.value)
    return " ".join(texts)


# @app.post("/message/")
# async def reply(Body: str = Form(), From: str = Form()):
#     normalized_phone = From.lstrip("+").replace("-", "").replace(" ", "")
#     user_doc_ref = db.collection('whatsapp_conversations').document(normalized_phone)
#     doc = user_doc_ref.get()

#     if not doc.exists:
#         user_doc_ref.set({'interactions': []})

#     # Create a thread for the user if it does not exist
#     thread = client.beta.threads.create()

#     # Add the WhatsApp message to the OpenAI thread and to Firestore
#     message = client.beta.threads.messages.create(
#         thread_id=thread.id,
#         role="user",
#         content=Body
        
#     )

#     # Save the user's message to Firestore
#     user_doc_ref.update({
#         'interactions': firestore.ArrayUnion([{'message': Body}])
#     })

#     # Create a run using the existing Assistant
#     run = client.beta.threads.runs.create_and_poll(
#         thread_id=thread.id,
#         assistant_id=assistant_id,
#         instructions=instructions
#         #instructions="refer to the user as EMRE TURAN"

#     )

#     # Check if the run is completed and then list the messages
#     if run.status == 'completed':
#         messages = client.beta.threads.messages.list(thread_id=thread.id)
#         assistant_response = extract_text_from_messages(messages)
#         send_message(From, assistant_response)
#         user_doc_ref.update({
#             'interactions': firestore.ArrayUnion([{'response': assistant_response}])
#         })
#     else:
#         send_message(From, "There was an issue processing your request.")
#         print(run.status)

#     return Response(status_code=200)



# @app.post("/message/")
# async def reply(Body: str = Form(), From: str = Form()):
#     normalized_phone = From.lstrip("+").replace("-", "").replace(" ", "")
#     user_doc_ref = db.collection('whatsapp_conversations').document(normalized_phone)
#     doc = user_doc_ref.get()

#     # Initialize interactions if the user is new
#     if not doc.exists:
#         user_doc_ref.set({'interactions': []})
#         interactions = []
#     else:
#         interactions = doc.to_dict().get('interactions', [])

#     # Check the number of interactions and limit responses if necessary
#     if len(interactions) >= 30:
#         # Send a message that the interaction limit has been reached
#         send_message(From, "You have reached your interaction limit with AOI. Please contact AOI for further assistance.")
#         return Response(status_code=200)

#     # Create a thread for the user if it does not exist
#     thread = client.beta.threads.create()

#     # Add the WhatsApp message to the OpenAI thread and to Firestore
#     message = client.beta.threads.messages.create(
#         thread_id=thread.id,
#         role="user",
#         content=Body
#     )

#     # Save the user's message to Firestore
#     user_doc_ref.update({
#         'interactions': firestore.ArrayUnion([{'message': Body}])
#     })

#     # Create a run using the existing Assistant
#     run = client.beta.threads.runs.create_and_poll(
#         thread_id=thread.id,
#         assistant_id=assistant_id,
#         instructions=instructions
#         #instructions="refer to the user as EMRE TURAN"
#     )

#     # Check if the run is completed and then list the messages
#     if run.status == 'completed':
#         messages = client.beta.threads.messages.list(thread_id=thread.id)
#         assistant_response = extract_text_from_messages(messages)
#         send_message(From, assistant_response)
#         user_doc_ref.update({
#             'interactions': firestore.ArrayUnion([{'response': assistant_response}])
#         })
#     else:
#         send_message(From, "There was an issue processing your request.")
#         print(run.status)

#     return Response(status_code=200)




@app.post("/message/")
async def reply(Body: str = Form(), From: str = Form()):
    normalized_phone = From.lstrip("+").replace("-", "").replace(" ", "")
    user_doc_ref = db.collection('whatsapp_conversations').document(normalized_phone)
    doc = user_doc_ref.get()

    # Initialize interactions if the user is new
    if not doc.exists:
        user_doc_ref.set({'interactions': [], 'limit_reached_notified': False})
        interactions = []
        limit_reached_notified = False
    else:
        interactions = doc.to_dict().get('interactions', [])
        limit_reached_notified = doc.to_dict().get('limit_reached_notified', False)

    # Check the number of interactions and limit responses if necessary
    if len(interactions) >= 30:
        if not limit_reached_notified:
            # Send a message that the interaction limit has been reached
            send_message(From, "You have reached your interaction limit with AOI. Please contact AOI for further assistance.")
            # Update the Firestore document to mark that the notification has been sent
            user_doc_ref.update({'limit_reached_notified': True})
        return Response(status_code=200)

    # Create a thread for the user if it does not exist
    thread = client.beta.threads.create()

    # Add the WhatsApp message to the OpenAI thread and to Firestore
    message = client.beta.threads.messages.create(
        thread_id=thread.id,
        role="user",
        content=Body
    )

    # Save the user's message to Firestore
    user_doc_ref.update({
        'interactions': firestore.ArrayUnion([{'message': Body}])
    })

    # Create a run using the existing Assistant
    run = client.beta.threads.runs.create_and_poll(
        thread_id=thread.id,
        assistant_id=assistant_id,
        instructions=instructions
    )

    # Check if the run is completed and then list the messages
    if run.status == 'completed':
        messages = client.beta.threads.messages.list(thread_id=thread.id)
        assistant_response = extract_text_from_messages(messages)
        send_message(From, assistant_response)
        user_doc_ref.update({
            'interactions': firestore.ArrayUnion([{'response': assistant_response}])
        })
    else:
        send_message(From, "There was an issue processing your request.")
        print(run.status)

    return Response(status_code=200)
