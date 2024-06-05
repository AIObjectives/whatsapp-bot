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
firebase_credentials = json.loads(os.environ.get('FIREBASE_CREDENTIALS'))
cred = credentials.Certificate(firebase_credentials)
firebase_admin.initialize_app(cred)
db = firestore.client()

# FastAPI app initialization
app = FastAPI()

# # OpenAI Configuration
# OpenAI.api_key = config("OPENAI_API_KEY")
# client = OpenAI(api_key=OpenAI.api_key)
# #assistant_id = "asst_oxQinJe5sKixyRh1HHsy8yqo" ## EMRE
# assistant_id = "asst_XNN9S1LK9EvUG2533xkvKoZh" ## AOI


# # Twilio Configuration
# twilio_account_sid = config("TWILIO_ACCOUNT_SID")
# twilio_auth_token = config("TWILIO_AUTH_TOKEN")
# twilio_client = TwilioClient(twilio_account_sid, twilio_auth_token)
# twilio_number = config('TWILIO_NUMBER')


# Firebase Initialization
# cred = credentials.Certificate('/Users/emreturan/Desktop/firebase/aoiwhatsappbot-firebase-adminsdk-rki5n-9526831994.json')
# firebase_admin.initialize_app(cred)
# db = firestore.client()

# FastAPI app initialization
#app = FastAPI()

# OpenAI Configuration
OpenAI.api_key = config("OPENAI_API_KEY")
client = OpenAI(api_key=OpenAI.api_key)
#assistant_id = "asst_oxQinJe5sKixyRh1HHsy8yqo" ## EMRE
#assistant_id = "asst_XNN9S1LK9EvUG2533xkvKoZh" ## AOI for general whatsapp
assistant_id = "asst_Hd2y8q4VdTz9j07zA8m3vW85" ## AOI for AI conference/ gpt-4o shoudl be much cheaper!



# Twilio Configuration
twilio_account_sid = config("TWILIO_ACCOUNT_SID")
twilio_auth_token = config("TWILIO_AUTH_TOKEN")
twilio_client = TwilioClient(twilio_account_sid, twilio_auth_token)
twilio_number = config('TWILIO_NUMBER')
# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


#instructions = """ act like you are a dog"""






###  make some small changes: 
instructions= """ 

Bot Objective
The AI bot is primarily designed to listen and record discussions at the AI Objectives Institute (AOI) conference with minimal interaction. Its responses are restricted to one or two sentences only, to maintain focus on the participants' discussions.

Bot Personality
The bot is programmed to be non-intrusive and neutral, offering no more than essential interaction required to acknowledge participants' inputs.

Initial Interaction
Welcome Message: The bot will initially greet participants only if prompted, with a simple, "Welcome to the AI Objectives Institute (AOI) conference."
Listening Mode
Data Retention: The bot is in a passive listening mode, capturing important discussion points without actively participating.
Minimal Responses: The bot remains largely silent, offering brief acknowledgments if directly addressed.
Interaction Guidelines
Ultra-Brief Responses: If the bot needs to respond, it will use no more than one to two sentences, strictly adhering to this rule to prevent engaging beyond necessary acknowledgment.
Acknowledgments: For instance, if a participant makes a point or asks if the bot is recording, it might say, "Acknowledged," or, "Yes, I'm recording."
Conversation Management
Directive Responses: On rare occasions where direction is required and appropriate, the bot will use concise prompts like "Please continue," or "Could you clarify?"
Passive Engagement: The bot uses minimal phrases like "Understood" or "Noted" with professional emojis to confirm its presence and listening status without adding substance to the conversation.
Closure of Interaction
Concluding Interaction: When a dialogue concludes or a user ends the interaction, the bot responds succinctly with, "Thank you for the discussion."
Overall Management
The bot ensures it does not interfere with or distract from the human-centric discussions at the conference. Its primary role is to support by listening and only acknowledging when absolutely necessary, ensuring that all interactions remain brief and to the point.

"""


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


from fastapi import HTTPException, Response, Form, UploadFile, File
from uuid import uuid4
import os
import requests
import io
from pydub import AudioSegment
from requests.auth import HTTPBasicAuth



@app.post("/message/")
async def reply(Body: str = Form(default=None), From: str = Form(), MediaUrl0: str = Form(default=None)):
    logger.info(f"Received message from {From} with body {Body} and media URL {MediaUrl0}")
    normalized_phone = From.lstrip("+").replace("-", "").replace(" ", "")
    user_doc_ref = db.collection('whatsapp_conversations').document(normalized_phone)
    doc = user_doc_ref.get()

    if not doc.exists:
        user_doc_ref.set({'interactions': [], 'limit_reached_notified': False})
        interactions = []
    else:
        interactions = doc.to_dict().get('interactions', [])
        limit_reached_notified = doc.to_dict().get('limit_reached_notified', False)

    if len(interactions) >= 150 and not limit_reached_notified:
        send_message(From, "You have reached your interaction limit with AOI. Please contact AOI for further assistance.")
        user_doc_ref.update({'limit_reached_notified': True})
        return Response(status_code=200)

    if MediaUrl0:
        response = requests.get(MediaUrl0, auth=HTTPBasicAuth(twilio_account_sid, twilio_auth_token))
        content_type = response.headers['Content-Type']
        logger.info(f"Content-Type of received media: {content_type}")

        if 'audio' in content_type:
            audio_stream = io.BytesIO(response.content)
            audio_stream.name = 'file.ogg'  # Assume the file is in OGG format
            logger.info("Attempting to transcribe audio")
            try:
                transcription_result = client.audio.transcriptions.create(
                    model="whisper-1", 
                    file=audio_stream
                )
                Body = transcription_result.text
                logger.info(f"Transcription result: {Body}")
            except Exception as e:
                logger.error(f"Error in transcription: {str(e)}")
                return Response(status_code=500, content=str(e))
        else:
            logger.error("Received media is not an audio file. Response content: " + response.text)
            return Response(status_code=400, content="Unsupported media type.")

    if not Body:
        logger.error("No text to process after transcription.")
        return Response(status_code=400)

    thread = client.beta.threads.create()
    message = client.beta.threads.messages.create(
        thread_id=thread.id,
        role="user",
        content=Body
    )

    user_doc_ref.update({
        'interactions': firestore.ArrayUnion([{'message': Body}])
    })

    run = client.beta.threads.runs.create_and_poll(
        thread_id=thread.id,
        assistant_id=assistant_id,
        instructions=instructions
    )

    if run.status == 'completed':
        messages = client.beta.threads.messages.list(thread_id=thread.id)
        assistant_response = extract_text_from_messages(messages)
        send_message(From, assistant_response)
        user_doc_ref.update({
            'interactions': firestore.ArrayUnion([{'response': assistant_response}])
        })
    else:
        logger.error("Failed to complete processing: " + run.status)
        send_message(From, "There was an issue processing your request.")

    return Response(status_code=200)
