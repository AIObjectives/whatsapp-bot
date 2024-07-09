

import firebase_admin
from firebase_admin import credentials, firestore
from fastapi import FastAPI, Form, Response
from openai import OpenAI
from decouple import config
import logging
import json
from twilio.rest import Client as TwilioClient


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


# OpenAI Configuration
OpenAI.api_key = config("OPENAI_API_KEY")
client = OpenAI(api_key=OpenAI.api_key)
#assistant_id = "##" ## EMRE
#assistant_id = "##" ## AOI for general whatsapp
assistant_id = "##" ## AOI for AI conference/ gpt-4o shoudl be much cheaper!


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
# Instructions for the bot

# instructions= """ 

# Bot Objective
# The AI bot is primarily designed to listen and record discussions at the AI Objectives Institute (AOI) conference with minimal interaction. Its responses are restricted to one or two sentences only, to maintain focus on the participants' discussions.

# Bot Personality
# The bot is programmed to be non-intrusive and neutral, offering no more than essential interaction required to acknowledge participants' inputs.

# Initial Interaction
# Welcome Message: The bot will initially greet participants only if prompted, with a simple, "Welcome to the AI Objectives Institute (AOI) conference."
# Listening Mode
# Data Retention: The bot is in a passive listening mode, capturing important discussion points without actively participating.
# Minimal Responses: The bot remains largely silent, offering brief acknowledgments if directly addressed.
# Interaction Guidelines
# Ultra-Brief Responses: If the bot needs to respond, it will use no more than one to two sentences, strictly adhering to this rule to prevent engaging beyond necessary acknowledgment.
# Acknowledgments: For instance, if a participant makes a point or asks if the bot is recording, it might say, "Acknowledged," or, "Yes, I'm recording."
# Conversation Management
# Directive Responses: On rare occasions where direction is required and appropriate, the bot will use concise prompts like "Please continue," or "Could you clarify?"
# Passive Engagement: The bot uses minimal phrases like "Understood" or "Noted" with professional emojis to confirm its presence and listening status without adding substance to the conversation.
# Closure of Interaction
# Concluding Interaction: When a dialogue concludes or a user ends the interaction, the bot responds succinctly with, "Thank you for the discussion."
# Overall Management
# The bot ensures it does not interfere with or distract from the human-centric discussions at the conference. Its primary role is to support by listening and only acknowledging when absolutely necessary, ensuring that all interactions remain brief and to the point.

# """


instructions= """ 

Bot Objective
The AI bot is primarily designed to listen and record discussions at the AI Objectives Institute (AOI) conference with minimal interaction. Its responses are restricted to one or two sentences only, to maintain focus on the participants' discussions.

Bot Personality
The bot is programmed to be non-intrusive and neutral, offering no more than essential interaction required to acknowledge participants' inputs.


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

from openai import OpenAI


import openai
import re

# Configuration
openai_api_key = config('OPENAI_API_KEY')
openai_engine = 'gpt-4o'

def generate_initial_message1(user_input):
    """Generate an initial response based on user input that either extracts the name or prompts for it, along with a welcoming message."""
    try:
        response = client.chat.completions.create(
            model="gpt-4o",
            
            messages=[
                {"role": "system", "content": """
                    This is the first interaction of the assistant with a user at the Talk to the City discussion on deliberative technology. The assistant's primary objectives are:
                    1. To warmly welcome the user to the conference.
                    2. Check the user's input for their name and extract it. If a name is provided, include it in the welcoming message, like 'Welcome [Name] to the Talk to the City discussion on deliberative technology. Please continue with the conversation.' However, if the user has entered 'Anonymous'or 'anonymous', the welcoming message should be 'Welcome to the Talk to the City discussion on deliberative technology! Please continue with the conversation.' without including a name.'
                    3. If the name is not clearly provided in the input, the assistant should politely ask for the name by saying 'Welcome to the Talk to the City discussion on deliberative technology. Please tell me your name.'
                    4. The assistant must also be prepared to respond succinctly (in one sentence) to any query or unrelated statement the user might initially make, maintaining a professional and neutral tone. After addressing the query or statement, if the name has not been provided, the assistant should proceed to ask for it.
                """},
                {"role": "user", "content": user_input}
            ],
            
            max_tokens=150,
            temperature=0.5
        )
        if response.choices:
            full_message = response.choices[0].message.content.strip()
            # Improved name extraction using regex to find capitalized words or sequences after 'Welcome'
            match = re.search(r"Welcome (\b[A-Z][a-z]*\b)", full_message)
            name_part = match.group(1) if match else None
            return full_message, name_part
        else:
            return "Welcome to the Talk to the City discussion on deliberative technology. Please tell me your name.", None
    except Exception as e:
        logger.error(f"Error in generating initial message response: {e}")
        return "Welcome to the Talk to the City discussion on deliberative technology. Please tell me your name.", None
    



def extract_name_with_llm(generated_message):
    """Extract the user's name from the generated message using LLM analysis."""
    try:
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": """
                    Analyze the generated message carefully. Analyze the generated welcome message carefully. Examine the message for a greeting that includes a participant's name immediately following 'Welcome' or 'Welcome to the,' as seen in phrases like 'Welcome [Name] to the Talk to the City discussion on deliberative technology.' Extract only the name itself, without any additional text. Return strictly the name itself without any additional text. If the message does not include a name, as in 'Welcome to the Talk to the City discussion on deliberative technology!' without any following name, return 'Anonymous' to indicate that no specific name was provided.  If the message prompts with 'Please tell me your name,' indicate that no name was provided by returning 'No name found'.
                """}, 
                {"role": "user", "content": generated_message}
            ],
            max_tokens=50,
            temperature=0.7
        )
        # Access the content of the response to extract the name
        if response.choices and response.choices[0].message.content.strip():
            name = response.choices[0].message.content.strip()
            if "Please tell me your name." in generated_message:
                return "No name found"  # Name request implies no name was provided
            return name
        else:
            return "No name found"
    except Exception as e:
        logger.error(f"Error in extracting name with LLM: {e}")
        return None

@app.post("/message/")
async def reply(Body: str = Form(default=None), From: str = Form(), MediaUrl0: str = Form(default=None)):
    logger.info(f"Received message from {From} with body '{Body}' and media URL {MediaUrl0}")
    normalized_phone = From.replace("+", "").replace("-", "").replace(" ", "")
    user_doc_ref = db.collection('whatsapp_conversations1').document(normalized_phone)
    doc = user_doc_ref.get()


    if MediaUrl0:
        response = requests.get(MediaUrl0, auth=HTTPBasicAuth(twilio_account_sid, twilio_auth_token))
        content_type = response.headers['Content-Type']
        if 'audio' in content_type:
            audio_stream = io.BytesIO(response.content)
            audio_stream.name = 'file.ogg'
            try:
                transcription_result = client.audio.transcriptions.create(
                    model="whisper-1", 
                    file=audio_stream
                )
                Body = transcription_result.text
            except Exception as e:
                return Response(status_code=500, content=str(e))
        else:
            return Response(status_code=400, content="Unsupported media type.")

    if not Body:
        return Response(status_code=400)

    if not doc.exists:
        user_doc_ref.set({'interactions': [], 'name': None, 'limit_reached_notified': False})
        generated_message, _ = generate_initial_message1(Body)  # Assuming this function returns the message and a dummy name part
        extracted_name = extract_name_with_llm(generated_message)
        # if extracted_name and extracted_name != "No name found":
        #     user_doc_ref.update({'name': extracted_name})
        #     send_message(From, f"Welcome {extracted_name} to the Talk to the City discussion on deliberative technology. You can now start sending text and audio messages to Talk to the City. To change your name, type 'change name' followed by your new name (all in one message)")
        # else:
        #     send_message(From, "Welcome to the Talk to the City discussion on deliberative technology. Please tell me your name.")
        # return Response(status_code=200)
        if extracted_name == "Anonymous":
            user_doc_ref.update({'name': extracted_name})
            send_message(From, "Welcome to the Talk to the City discussion on deliberative technology. You can now start sending text and audio messages to Talk to the City. To change your name, type 'change name' followed by your new name (all in one message)")
        elif extracted_name and extracted_name != "No name found":
            user_doc_ref.update({'name': extracted_name})
            send_message(From, f"Welcome {extracted_name} to the Talk to the City discussion on deliberative technology. You can now start sending text and audio messages to Talk to the City. To change your name, type 'change name' followed by your new name (all in one message)")
        else:
            send_message(From, "Welcome to the Talk to the City discussion on deliberative technology. Please tell me your name.")
        return Response(status_code=200)


    data = doc.to_dict()
    interactions = data.get('interactions', [])
    participant_name = data.get('name', None)

    if len(interactions) >= 450:
        send_message(From, "You have reached your interaction limit with AOI. Please contact AOI for further assistance.")
        return Response(status_code=200)

    if not participant_name:
        #extracted_name = extract_name_with_llm2(Body)
        # extracted_name = generate_initial_message1(Body)
        # extracted_name1 = extract_name_with_llm(extracted_name)

        generated_message, _ = generate_initial_message1(Body)  # Assuming this function returns the message and a dummy name part
        extracted_name = extract_name_with_llm(generated_message)
       



        # if extracted_name1 and extracted_name1 != "No name found":
        #     user_doc_ref.update({'name': extracted_name1})
        #     send_message(From, f"Welcome {extracted_name1}! Please continue with the conversation1.")
        # else:
        #     send_message(From, "Please tell me your name to continue.")
        
        # extracted_name = extract_name_with_llm2("my name is emre")
        # extracted_name1 = extract_name_with_llm2("i dont want to")

        
        print("this is body" ,Body)
        print("letsee",extracted_name)
        # print("letsee1",extracted_name1)
        # if extracted_name and extracted_name != "No name found":
        #     user_doc_ref.update({'name': extracted_name})
        #     send_message(From, f"Welcome {extracted_name}! You can now start sending text and audio messages to Talk to the City. To change your name, type 'change name' followed by your new name (all in one message)")
        # else:
        #     send_message(From, "I'm sorry, I couldn't find a name. Please tell me your name to continue.")
        # return Response(status_code=200)
    

        if extracted_name == "Anonymous":
            user_doc_ref.update({'name': extracted_name})
            send_message(From, "Welcome! You can now start sending text and audio messages to Talk to the City. To change your name, type 'change name' followed by your new name (all in one message)")
        elif extracted_name and extracted_name != "No name found":
            user_doc_ref.update({'name': extracted_name})
            send_message(From, f"Welcome {extracted_name}! You can now start sending text and audio messages to Talk to the City. To change your name, type 'change name' followed by your new name (all in one message)")
        else:
            send_message(From, "I'm sorry, I couldn't find a name. Please tell me your name to continue.")
        return Response(status_code=200)
    
    if Body.lower().startswith("change name "):
        new_name = Body[12:].strip()
        if new_name:
            user_doc_ref.update({'name': new_name})
            send_message(From, f"Your name has been updated to {new_name}. Please continue with the conversation.")
        else:
            send_message(From, "It seems there was an error updating your name. Please try again.")
        return Response(status_code=200)

    # if Body == "123456":
    #     send_message(From, "Your breakout group 1 has been assigned. Please continue the conversation.")
    #     # ACTUALLY create the spreadsheet and mak eit happen!!!
    #     return Response(status_code=200)
    
    # if Body == "123455":
    #     send_message(From, "Your breakout group 2 has been assigned. Please continue the conversation.")
    #     # ACTUALLY create the spreadsheet and mak eit happen!!!
    #     return Response(status_code=200)
    
    # if Body == "123454":
    #     send_message(From, "Your breakout group 3 has been assigned. Please continue the conversation.")
    #     # ACTUALLY create the spreadsheet and mak eit happen!!!
    #     return Response(status_code=200)
    
    # if Body == "123453":
    #     send_message(From, "Your breakout group 4 has been assigned. Please continue the conversation.")
    #     # ACTUALLY create the spreadsheet and mak eit happen!!!
    #     return Response(status_code=200)


    # if MediaUrl0:
    #     response = requests.get(MediaUrl0, auth=HTTPBasicAuth(twilio_account_sid, twilio_auth_token))
    #     content_type = response.headers['Content-Type']
    #     if 'audio' in content_type:
    #         audio_stream = io.BytesIO(response.content)
    #         audio_stream.name = 'file.ogg'
    #         try:
    #             transcription_result = client.audio.transcriptions.create(
    #                 model="whisper-1", 
    #                 file=audio_stream
    #             )
    #             Body = transcription_result.text
    #         except Exception as e:
    #             return Response(status_code=500, content=str(e))
    #     else:
    #         return Response(status_code=400, content="Unsupported media type.")

    # if not Body:
    #     return Response(status_code=400)

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
        send_message(From, "There was an issue processing your request.")

    return Response(status_code=200)


def confirm_name(response):
    try:
        follow_up = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": "The user's response is intended to confirm their name. Analyze the response below and simply reply 'yes' if it confirms the name positively or 'no' if it does not."},
                #{"role": "system", "content": "Determine if the user's response confirms their previous name, provides a new name, or is neither. Respond 'yes' for confirmation, 'extract' to indicate a new name should be extracted, or 'no' if the response is neither."},

                {"role": "user", "content": response}
            ],
            max_tokens=10,
            temperature=0.1
        )
        return follow_up.choices[0].message.content.strip()
    except Exception as e:
        logger.error(f"Error in processing name confirmation: {e}")
        return "error"


