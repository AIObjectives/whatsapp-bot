import firebase_admin
from firebase_admin import credentials, firestore
from fastapi import FastAPI, Form, Response
from openai import OpenAI
from decouple import config
import logging
from twilio.rest import Client as TwilioClient

# Firebase Initialization
cred = credentials.Certificate('/Users/emreturan/Desktop/firebase/aoiwhatsappbot-firebase-adminsdk-rki5n-9526831994.json')
firebase_admin.initialize_app(cred)
db = firestore.client()

# FastAPI app initialization
app = FastAPI()

# OpenAI Configuration
OpenAI.api_key = config("OPENAI_API_KEY")
client = OpenAI(api_key=OpenAI.api_key)
#assistant_id = "asst_oxQinJe5sKixyRh1HHsy8yqo" ## EMRE
assistant_id = "asst_XNN9S1LK9EvUG2533xkvKoZh" ## AOI


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

from openai import OpenAI


import openai

# Configuration
openai_api_key = config('OPENAI_API_KEY')
openai_engine = 'gpt-4o'


def extract_name_with_llm(message):
    try:
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": "Your task is to identify and return only the first name mentioned in the user's input, without any additional text or formatting."},
                {"role": "user", "content": message}
            ],
            max_tokens=150,
            temperature=0.7
        )
        # Correctly access the content of the response using the appropriate method or property
        if response.choices:
            return response.choices[0].message.content.strip()  # Updated access to use properties
        else:
            return "No name found"
    except Exception as e:
        logger.error(f"Error in generating response from OpenAI: {e}")
        return None
    


def handle_group_assignment(Body, From, doc, group_assignments, service, spreadsheet_id):
    if Body in group_assignments:
        round_number, group_number = group_assignments[Body]
        if doc.exists:
            data = doc.to_dict()
            participant_name = data.get('name', 'Unknown Name')
            phone_number = From  # Assuming 'From' contains the normalized phone number

            try:
                # Pass all required parameters, including service and spreadsheet_id
                update_google_sheets(participant_name, phone_number, str(round_number), str(group_number), service, spreadsheet_id)
                send_message(From, f"Your breakout group {group_number} in round {round_number} has been assigned. Please continue the conversation.")
            except Exception as e:
                logging.error(f"Error updating Google Sheets: {e}")
                send_message(From, "Failed to update Google Sheets. Please try again.")
        else:
            send_message(From, "Please register your name first.")





@app.post("/message/")
async def reply(Body: str = Form(default=None), From: str = Form(), MediaUrl0: str = Form(default=None)):
    logger.info(f"Received message from {From} with body '{Body}' and media URL {MediaUrl0}")
    normalized_phone = From.replace("+", "").replace("-", "").replace(" ", "")
    user_doc_ref = db.collection('whatsapp_conversations').document(normalized_phone)
    doc = user_doc_ref.get()

    if not doc.exists:
        user_doc_ref.set({'interactions': [], 'name': None, 'limit_reached_notified': False, 'awaiting_name_confirmation': False})
        send_message(From, "Welcome to the AI Objectives Institute (AOI) conference. Please tell me your name.")
        return Response(status_code=200)

    data = doc.to_dict()
    interactions = data.get('interactions', [])
    participant_name = data.get('name', None)
    awaiting_confirmation = data.get('awaiting_name_confirmation', False)

    if len(interactions) >= 450:
        send_message(From, "You have reached your interaction limit with AOI. Please contact AOI for further assistance.")
        return Response(status_code=200)

    
        
    if not participant_name:
        if awaiting_confirmation:
            confirmation_response = confirm_name(Body)
            if confirmation_response == "yes":
                user_doc_ref.update({'name': data.get('last_provided_name'), 'awaiting_name_confirmation': False})
                send_message(From, f"Thank you, {data.get('last_provided_name')}. Please continue with the conversation. To change your name, type 'change name' followed by your new name.")
                return Response(status_code=200)
            else:
                corrected_name = extract_name_with_llm(Body)
                if corrected_name and corrected_name != "No name found":
                    user_doc_ref.update({'name': corrected_name, 'awaiting_name_confirmation': False})
                    send_message(From, f"Your name has been updated to {corrected_name}. Please continue with the conversation. To change your name, type 'change name' followed by your new name.")
                else:
                    send_message(From, "I'm still having trouble finding a valid name. To change your name, type 'change name' followed by your new name.")
                return Response(status_code=200)

        name_extracted = extract_name_with_llm(Body)
        if name_extracted and name_extracted != "No name found":
            user_doc_ref.update({'last_provided_name': name_extracted, 'awaiting_name_confirmation': True})
            #send_message(From, f"Please provide a sentence with your name or type 'change name' followed by your new name.")
            send_message(From, f"Thank you, {name_extracted}. Please continue with the conversation. To change your name, type 'change name' followed by your new name.")

            return Response(status_code=200)
        else:
            send_message(From, "I'm sorry, I couldn't find a name. To change your name, type 'change name' followed by your new name.")
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


    group_assignments = {
    "1111": (0, 0),
    "2222": (0, 1),
    "3333": (0, 2),
    # Add more mappings as needed
    "4444": (1, 0),
    "5555": (1, 1),
    "6666": (1, 2),
    "7777": (2, 0),
    "8888": (2, 1),
    "9999": (2, 2),
    "1234": (3, 0)
        }
    
    # if Body in group_assignments:
    #     round_number, group_number = group_assignments[Body]
    #     if doc.exists:
    #         data = doc.to_dict()
    #         participant_name = data.get('name', 'Unknown Name')
    #         phone_number = normalized_phone
    #         try:
    #             update_google_sheets(participant_name, phone_number, round_number, group_number)
    #             send_message(From, f"Your breakout group {group_number} in round {round_number} has been assigned. Please continue the conversation.")
    #         except Exception as e:
    #             logger.error(f"Error updating Google Sheets: {e}")
    #             send_message(From, "Failed to update Google Sheets. Please try again.")
    #         return Response(status_code=200)
    #     else:
    #         send_message(From, "Please register your name first.")
    #         return Response(status_code=200)

    service = build_google_sheets_service()  # Ensure you have a function to build the Google Sheets service
    spreadsheet_id = 'your_spreadsheet_id_here'

    # Check if the message relates to group assignment
    if Body in group_assignments:
        handle_group_assignment(Body, From, doc, group_assignments, service, spreadsheet_id)

    



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





import json
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from firebase_admin import credentials, firestore, initialize_app

# Firebase and Google API setup would be similar to your existing setup

def find_header_indexes(headers, target_headers):
    """ Find indexes of the target headers in the headers list. """
    indexes = {}
    for i, header in enumerate(headers):
        if header in target_headers:
            indexes[header] = i
    return indexes

def update_google_sheets(name, phone_number, breakout_round, group_number, service, spreadsheet_id):
    try:
        # Fetch the current data from the sheet to locate the header row
        range_name = 'Breakout groups!A1:Z100'  # Adjust as necessary
        result = service.spreadsheets().values().get(spreadsheetId=spreadsheet_id, range=range_name).execute()
        values = result.get('values', [])

        if not values:
            print("No data found in the spreadsheet.")
            return

        # Locate the header row and column indexes
        target_headers = ['Breakout round', 'Group number', 'Name', 'Phone number']
        header_row = None
        header_indexes = {}
        for row in values:
            header_indexes = find_header_indexes(row, target_headers)
            if len(header_indexes) == len(target_headers):
                header_row = row
                break

        if not header_row:
            print("Header row with necessary columns not found.")
            return

        # Prepare data for insertion
        data_row = [''] * len(header_row)  # create an empty row with the same length as the header row
        data_row[header_indexes['Breakout round']] = breakout_round
        data_row[header_indexes['Group number']] = group_number
        data_row[header_indexes['Name']] = name
        data_row[header_indexes['Phone number']] = phone_number

        # Append the new row to the sheet
        body = {'values': [data_row]}
        range_to_write = f"Breakout groups!A{len(values) + 1}"  # Assumes appending after the last row
        request = service.spreadsheets().values().append(
            spreadsheetId=spreadsheet_id, range=range_to_write,
            valueInputOption='USER_ENTERED', body=body)
        request.execute()

    except HttpError as err:
        print(err)

# Usage of update_google_sheets would be similar to your existing usage




from google.oauth2 import service_account
from googleapiclient.discovery import build

def build_google_sheets_service():
    # Path to your service account key file
    service_account_file = '/path/to/service/account.json'
    
    # Define the scopes of access
    scopes = ["https://www.googleapis.com/auth/spreadsheets"]

    # Authenticate using the service account file
    credentials = service_account.Credentials.from_service_account_file(
        service_account_file, scopes=scopes)

    # Build the service object for the Google Sheets API
    service = build('sheets', 'v4', credentials=credentials)
    
    return service

# Usage of the function in your application logic
service = build_google_sheets_service()
# Now, you can use `service` to interact with Google Sheets
