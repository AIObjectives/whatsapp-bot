

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


from fastapi import HTTPException, Response, Form, UploadFile, File
from uuid import uuid4
import os

import requests
import io
from pydub import AudioSegment

from requests.auth import HTTPBasicAuth

from openai import OpenAI

from config1 import db, logger, OpenAI, client, twilio_client, twilio_number, assistant_id , twilio_account_sid, twilio_auth_token, cred, app 

import openai
import re



def is_valid_name(name):
    if not name:
        return False
    name = name.strip().strip('"').strip("'")
    if not name or name.lower() == "anonymous":
        return False
    # Check if name contains at least one alphabetic character
    if any(char.isalpha() for char in name):
        return True
    return False









def send_message(to_number, body_text):
    """Send a WhatsApp message via Twilio"""
    #from multiconf3_3 import twilio_client, twilio_number, logger
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




def generate_initial_message1(user_input, event_id):
    """Generate an initial response based on user input with dynamic event-specific instructions."""
    # Fetch dynamic event-specific instructions and event details from Firestore
    #from multiconf3_3 import db, client, logger
    event_info_ref = db.collection(f'AOI_{event_id}').document('info')
    event_info_doc = event_info_ref.get()

    if event_info_doc.exists:
        event_info = event_info_doc.to_dict()
        event_name = event_info.get('event_name', 'the event')
        event_location = event_info.get('event_location', 'the location')
        welcome_message = event_info.get('welcome_message', f"Welcome to the {event_name} in {event_location}.")
    else:
        event_name = 'the event'
        event_location = 'the location'
        welcome_message = f"Welcome to the {event_name} in {event_location}."

    # Dynamic system message with event-specific details
    system_message = f"""
        This is the first interaction of the assistant with a user at the {event_name} in {event_location}. 
        The assistant's primary objectives are:
        1. To warmly welcome the user to the {event_name}.
        2. Check the user's input for their name and extract it. If a name is provided, include it in the welcoming message, like 'Welcome [Name] to the {event_name} in {event_location}. Please continue with the conversation.'
        3. If the user has entered 'Anonymous' or 'anonymous', the welcoming message should be 'Welcome to the {event_name} in {event_location}! Please continue with the conversation.' without including a name.
        4. If the name is not clearly provided in the input, the assistant should politely ask for the name by saying 'Welcome to the {event_name} in {event_location}. Please tell me your name.'
        5. The assistant must also be prepared to respond succinctly (in one sentence) to any query or unrelated statement the user might initially make, maintaining a professional and neutral tone. After addressing the query or statement, if the name has not been provided, the assistant should proceed to ask for it.
    """

    try:
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": system_message},
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
            return f"{welcome_message}. Please tell me your name.", None

    except Exception as e:
        logger.error(f"Error in generating initial message response: {e}")
        return f"{welcome_message}. Please tell me your name.", None







def extract_name_with_llm(user_input, event_id):
    """Extract the user's name from the user's input using LLM analysis."""
    # Fetch dynamic event-specific details from Firestore
    event_info_ref = db.collection(f'AOI_{event_id}').document('info')
    event_info_doc = event_info_ref.get()

    event_name = 'the event'
    event_location = 'the location'
    if event_info_doc.exists:
        event_info = event_info_doc.to_dict()
        event_name = event_info.get('event_name', event_name)
        event_location = event_info.get('event_location', event_location)

    # Adjusted system message to instruct the LLM not to return "None"
    # system_message = f"""
    # You are to extract the participant's name from the user's input. The user is participating in {event_name} in {event_location}.

    # Instructions:
    # - The user's input may contain their name or a statement that they prefer to remain anonymous.
    # - If the user provides their name, extract only the name.
    # - If the user indicates they prefer to remain anonymous, return "Anonymous".
    # - If you cannot find a name in the user's input, return an empty string.

    # Examples:
    # - User Input: "My name is John." => Output: "John"
    # - User Input: "I prefer not to share my name." => Output: "Anonymous"
    # - User Input: "Anonymous" => Output: "Anonymous"
    # - User Input: "Just call me Jane Doe." => Output: "Jane Doe"
    # - User Input: "Hello!" => Output: ""
    # """
    system_message = f"""
    You are to extract the participant's name from the user's input. The user is participating in {event_name} in {event_location}.

    Instructions:
    - The user's input may contain their name or a statement that they prefer to remain anonymous.
    - If the user provides their name, extract only the name.
    - If the user indicates they prefer to remain anonymous, return "Anonymous".
    - If you cannot find a name in the user's input, return an empty string.

    Examples:
    - User Input: "My name is John." => Output: "John"
    - User Input: "I prefer not to share my name." => Output: "Anonymous"
    - User Input: "Anonymous" => Output: "Anonymous"
    - User Input: "Just call me Jane Doe." => Output: "Jane Doe"
    - User Input: "Hello!" => Output: ""
    """

    try:
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": system_message},
                {"role": "user", "content": user_input}
            ],
            max_tokens=50,
            temperature=0.6
        )

    #     if response.choices and response.choices[0].message.content.strip():
    #         name = response.choices[0].message.content.strip()
    #         if not name or name.lower() in ["", "none"]:
    #             return None  # Return None if name is empty or "none"
    #         else:
    #             return name
    #     else:
    #         return None  # Return None if no response
    # except Exception as e:
    #     logger.error(f"Error in extracting name with LLM: {e}")
    #     return None  

        if response.choices and response.choices[0].message.content.strip():
            name = response.choices[0].message.content.strip()
            # Remove surrounding quotes and whitespace
            name = name.strip().strip('"').strip("'")
            if not name or name.lower() in ["", "none"]:
                return None  # Return None if the name is empty or "none"
            else:
                return name
        else:
            return None  # Return None if no response
    except Exception as e:
        logger.error(f"Error in extracting name with LLM: {e}")
        return None




###
def extract_event_id_with_llm(user_input):
    """Extract the event ID from the user's input using LLM analysis."""
    #from multiconf3_3 import db, client, logger
    # Fetch all valid event IDs from Firestore
    try:
        collections = db.collections()
        valid_event_ids = [collection.id.replace('AOI_', '') for collection in collections if collection.id.startswith('AOI_')]
    except Exception as e:
        logger.error(f"Error fetching event IDs: {e}")
        return None

    # Prepare the system message for LLM
    system_message = f"""
    You are to extract the event ID from the user's input. The event ID is one of the following IDs:
    {', '.join(valid_event_ids)}.

    The user's input may contain additional text. Your task is to identify and extract the event ID from the input.

    Return only the event ID. If you cannot find an event ID in the user's input, return 'No event ID found'.
    """

    try:
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": system_message},
                {"role": "user", "content": user_input}
            ],
            max_tokens=20,
            temperature=0.2
        )
        if response.choices and response.choices[0].message.content.strip():
            event_id = response.choices[0].message.content.strip()
            print("this is the extracted",event_id)
            if event_id == "No event ID found":
                return None
            else:
                return event_id
        else:
            return None
    except Exception as e:
        logger.error(f"Error extracting event ID with LLM: {e}")
        return None


    

def event_id_valid(event_id):
    """ Validate event ID by checking if it exists in Firestore """
    #from multiconf3_3 import db, logger
    try:
        # Query Firestore for all collections starting with 'AOI_'
        collections = db.collections()
        valid_event_ids = [collection.id.replace('AOI_', '') for collection in collections if collection.id.startswith('AOI_')]

        # Check if the provided event_id exists in the list
        return event_id in valid_event_ids
    except Exception as e:
        logger.error(f"Error validating event ID: {e}")
        return False





def create_welcome_message(event_id, participant_name=None, prompt_for_name=False):
    """Construct the welcome message using the event's welcome_message from the database."""
    # Fetch event details
    event_info_ref = db.collection(f'AOI_{event_id}').document('info')
    event_info_doc = event_info_ref.get()
    welcome_message = "Hello! You can now start sending text and audio messages."

    if event_info_doc.exists:
        event_info = event_info_doc.to_dict()
        welcome_message = event_info.get('welcome_message', welcome_message)

    # If participant_name is provided and not 'Anonymous', insert it into the welcome message
    #if participant_name and participant_name != "Anonymous":
    if is_valid_name(participant_name):

        # Attempt to insert the name into the welcome message
        if "Welcome" in welcome_message:
            #there was a welcome. and i deleted the fullstop booom--
            personalized_welcome = welcome_message.replace("Welcome", f"Welcome {participant_name}")
        else:
            # If "Welcome to" is not in the welcome message, prepend "Welcome {name}, " to the message
            personalized_welcome = f"Welcome {participant_name}, {welcome_message}"
    else:
        # Use the welcome message as is
        personalized_welcome = welcome_message

    # If we need to prompt for the name
    # if prompt_for_name:
    #     # Append "Please tell me your name." to the message
    #     personalized_welcome += " Please tell me your name."

    return personalized_welcome






def confirm_name(response):
    #from multiconf3_3 import client, logger
    try:
        follow_up = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": "The user's response is intended to confirm their name. Analyze the response below and simply reply 'yes' if it confirms the name positively or 'no' if it does not."},
                #{"role": "system", "content": "Determine if the user's response confirms their previous name, provides a new name, or is neither. Respond 'yes' for confirmation, 'extract' to indicate a new name should be extracted, or 'no' if the response is neither."},

                {"role": "user", "content": response}
            ],
            max_tokens=10,
            temperature=0.4
        )
        return follow_up.choices[0].message.content.strip()
    except Exception as e:
        logger.error(f"Error in processing name confirmation: {e}")
        return "error"
    






# addititons:

def extract_age_with_llm(user_input, current_event_id):
    """Extract the participant's age from the user's input using LLM analysis."""
    # Prepare the system message for LLM
    system_message = """
    You are to extract the participant's age from the user's input. The age should be an integer representing the person's age in years.

    The user's input may contain additional text. Your task is to identify and extract the age from the input.

    Return only the age as a number. If you cannot find an age in the user's input, return 'No age found'.
    """

    try:
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": system_message},
                {"role": "user", "content": user_input}
            ],
            max_tokens=50,
            temperature=0.3
        )
        if response.choices and response.choices[0].message.content.strip():
            age = response.choices[0].message.content.strip()
            if age == "No age found":
                return "No age found"
            else:
                return age
        else:
            return "No age found"
    except Exception as e:
        logger.error(f"Error extracting age with LLM: {e}")
        return "No age found"





def extract_gender_with_llm(user_input, current_event_id):
    """Extract the participant's gender from the user's input using LLM analysis."""
    # Prepare the system message for LLM
    system_message = """
    You are to extract the participant's gender from the user's input.

    The user's input may contain additional text. Your task is to identify and extract the gender from the input.

    Return only the gender. Acceptable responses are 'Male', 'Female', 'Non-binary', or 'Other'. If you cannot find a gender in the user's input, return 'No gender found'.
    """

    try:
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": system_message},
                {"role": "user", "content": user_input}
            ],
            max_tokens=60,
            temperature=0.4
        )
        if response.choices and response.choices[0].message.content.strip():
            gender = response.choices[0].message.content.strip()
            if gender == "No gender found":
                return "No gender found"
            else:
                return gender
        else:
            return "No gender found"
    except Exception as e:
        logger.error(f"Error extracting gender with LLM: {e}")
        return "No gender found"




def extract_region_with_llm(user_input, current_event_id):
    """Extract the participant's region from the user's input using LLM analysis."""
    # Prepare the system message for LLM
    system_message = """
    You are to extract the participant's region or location from the user's input.

    The user's input may contain additional text. Your task is to identify and extract the region from the input.

    Return only the region or location. If you cannot find a region in the user's input, return 'No region found'.
    """

    try:
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": system_message},
                {"role": "user", "content": user_input}
            ],
            max_tokens=60,
            temperature=0.4
        )
        if response.choices and response.choices[0].message.content.strip():
            region = response.choices[0].message.content.strip()
            if region == "No region found":
                return "No region found"
            else:
                return region
        else:
            return "No region found"
    except Exception as e:
        logger.error(f"Error extracting region with LLM: {e}")
        return "No region found"




def generate_name_prompt_with_llm(participant_data, event_id):
    """
    Generate a dynamic and varied prompt to ask the participant for their name, using LLM.
    """
    # Fetch event details
    #participant_name = participant_data.get('name', None)

    event_info_ref = db.collection(f'AOI_{event_id}').document('info')
    event_info_doc = event_info_ref.get()

    event_name = 'the event'
    event_location = 'the location'

    if event_info_doc.exists:
        event_info = event_info_doc.to_dict()
        event_name = event_info.get('event_name', event_name)
        event_location = event_info.get('event_location', event_location)

    # Construct the system message with diverse examples
    system_message = f"""
You are a friendly and engaging assistant at {event_name} in {event_location}.
Your task is to ask the participant for their name in a polite, creative, and varied manner.
Make sure each prompt is unique and doesn't repeat previous phrasings.

Here are some examples of how you might ask:

- "Hi there! What should I call you?"
- "Hello! Could you please share your name with me?"
- "Greetings! May I know your name?"
- "Hey! I'm excited to chat with you. What's your name?"
- "Welcome! I'd love to know your name if you don't mind."

Now, generate a unique and friendly prompt asking for their name, different from the examples and previous prompts. 
Please generate your response as a single message without any quotation marks or surrounding punctuation.

"""

    try:
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": system_message},
            ],
            max_tokens=40,
            temperature=0.85
        )
        if response.choices and response.choices[0].message.content.strip():
            prompt_message = response.choices[0].message.content.strip()
            return prompt_message
        else:
            return "May I have your name, please?"
    except Exception as e:
        logger.error(f"Error generating name prompt with LLM: {e}")
        return "May I have your name, please?"



def generate_age_prompt_with_llm(participant_data, event_id):
    participant_name = participant_data.get('name', None)

    if participant_name:
        participant_name = participant_name.strip().strip('"').strip("'")
    else:
        participant_name = None
    # Fetch event details
    event_info_ref = db.collection(f'AOI_{event_id}').document('info')
    event_info_doc = event_info_ref.get()

    event_name = 'the event'
    event_location = 'the location'

    if event_info_doc.exists:
        event_info = event_info_doc.to_dict()
        event_name = event_info.get('event_name', event_name)
        event_location = event_info.get('event_location', event_location)

    # Start constructing the system message
    system_message = f"""
You are a friendly assistant at {event_name} in {event_location}.
"""

    #if participant_name and participant_name != "Anonymous":
    if is_valid_name(participant_name):

        system_message += f"""
You have collected the participant's name: {participant_name}.
Now, ask for their age in a polite, creative, and varied manner, acknowledging their name.
"""
    else:
        system_message += """
Now, ask for their age in a polite, creative, and varied manner.
"""

    system_message += """
Ensure each prompt is unique and doesn't repeat previous phrasings.

Examples:
"""

    #if participant_name and participant_name != "Anonymous":
    if is_valid_name(participant_name):

        system_message += f"""
- "Thanks, {participant_name}! Could you tell me your age?"
- "Great to meet you, {participant_name}. May I ask how old you are?"
- "Appreciate it, {participant_name}. What's your age?"
- "Wonderful, {participant_name}. Would you mind sharing your age with me?"
- "It's nice chatting with you, {participant_name}. How old are you?"
"""
    else:
        system_message += """
- "Could you let me know your age?"
- "May I ask how old you are?"
- "Would you mind telling me your age?"
- "Please share your age if you don't mind."
- "I'd love to know your age!"
"""

    system_message += """
Now, generate a unique prompt asking for their age, different from the examples and previous prompts.
Please generate your response as a single message without any quotation marks or surrounding punctuation.
"""

    try:
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": system_message},
            ],
            max_tokens=30,
            temperature=0.85
        )
        if response.choices and response.choices[0].message.content.strip():
            prompt_message = response.choices[0].message.content.strip()
            return prompt_message
        else:
            #if participant_name and participant_name != "Anonymous":
            if is_valid_name(participant_name):

                return f"Could you tell me your age, {participant_name}?"
            else:
                return "Could you tell me your age?"
    except Exception as e:
        logger.error(f"Error generating age prompt with LLM: {e}")
        #if participant_name and participant_name != "Anonymous":
        if is_valid_name(participant_name):

            return f"Could you tell me your age, {participant_name}?"
        else:
            return "Could you tell me your age?"







def generate_gender_prompt_with_llm(participant_data, event_id):
    participant_name = participant_data.get('name', None)

    if participant_name:
        participant_name = participant_name.strip().strip('"').strip("'")
    else:
        participant_name = None
    # Fetch event details
    event_info_ref = db.collection(f'AOI_{event_id}').document('info')
    event_info_doc = event_info_ref.get()

    event_name = 'the event'
    event_location = 'the location'

    if event_info_doc.exists:
        event_info = event_info_doc.to_dict()
        event_name = event_info.get('event_name', event_name)
        event_location = event_info.get('event_location', event_location)

    # Start constructing the system message
    system_message = f"""
You are a respectful and inclusive assistant at {event_name} in {event_location}.
"""

    #if participant_name and participant_name != "Anonymous":
    if is_valid_name(participant_name):

        system_message += f"""
You have collected the participant's name: {participant_name}.
Now, ask for their gender in a sensitive, creative, and varied manner, acknowledging their name.
"""
    else:
        system_message += """
Now, ask for their gender in a sensitive, creative, and varied manner.
"""

    system_message += """
Ensure each prompt is unique and doesn't repeat previous phrasings.

Examples:
"""

    #if participant_name and participant_name != "Anonymous":
    if is_valid_name(participant_name):

        system_message += f"""
- "Thanks, {participant_name}. Could you share your gender identity?"
- "Appreciate your responses, {participant_name}. May I ask how you identify your gender?"
- "To better assist you, {participant_name}, could you tell me your gender?"
- "If you're comfortable, {participant_name}, please let me know your gender."
- "{participant_name}, could you inform me of your gender identity?"
"""
    else:
        system_message += """
- "Could you please share your gender identity?"
- "May I ask how you identify your gender?"
- "Would you mind telling me your gender?"
- "Please let me know your gender, if you're comfortable."
- "I'd appreciate knowing your gender identity."
"""

    system_message += """
Now, generate a unique and respectful prompt asking for their gender, different from the examples and previous prompts.
Please generate your response as a single message without any quotation marks or surrounding punctuation.
"""

    try:
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": system_message},
            ],
            max_tokens=40,
            temperature=0.85
        )
        if response.choices and response.choices[0].message.content.strip():
            prompt_message = response.choices[0].message.content.strip()
            return prompt_message
        else:
            #if participant_name and participant_name != "Anonymous":
            if is_valid_name(participant_name):

                return f"Could you share your gender identity, {participant_name}?"
            else:
                return "Could you share your gender identity?"
    except Exception as e:
        logger.error(f"Error generating gender prompt with LLM: {e}")
        #if participant_name and participant_name != "Anonymous":
        if is_valid_name(participant_name):

            return f"Could you share your gender identity, {participant_name}?"
        else:
            return "Could you share your gender identity?"







def generate_region_prompt_with_llm(participant_data, event_id):
    participant_name = participant_data.get('name', None)
    if participant_name:
        participant_name = participant_name.strip().strip('"').strip("'")
    else:
        participant_name = None
    # Fetch event details
    event_info_ref = db.collection(f'AOI_{event_id}').document('info')
    event_info_doc = event_info_ref.get()

    event_name = 'the event'
    event_location = 'the location'

    if event_info_doc.exists:
        event_info = event_info_doc.to_dict()
        event_name = event_info.get('event_name', event_name)
        event_location = event_info.get('event_location', event_location)

    # Start constructing the system message
    system_message = f"""
You are a friendly assistant at {event_name} in {event_location}.
"""

    #if participant_name and participant_name != "Anonymous":
    if is_valid_name(participant_name):

        system_message += f"""
You have collected the participant's name: {participant_name}.
Now, ask for their region or location in a polite, creative, and varied manner, acknowledging their name.
"""
    else:
        system_message += """
Now, ask for their region or location in a polite, creative, and varied manner.
"""

    system_message += """
Ensure each prompt is unique and doesn't repeat previous phrasings.

Examples:
"""

    #if participant_name and participant_name != "Anonymous":
    if is_valid_name(participant_name):

        system_message += f"""
- "By the way, {participant_name}, where are you joining us from?"
- "Just curious, {participant_name}, which part of the world do you call home?"
- "Mind sharing your hometown or region, {participant_name}?"
- "{participant_name}, could you tell me where you're from?"
- "I'd love to know where you're based, {participant_name}."
"""
    else:
        system_message += """
- "Could you let me know where you're from?"
- "Which region or city do you come from?"
- "Where are you joining us from?"
- "May I ask your hometown or region?"
- "I'd love to know where you're based!"
"""

    system_message += """
Now, generate a unique prompt asking for their region, different from the examples and previous prompts.
Please generate your response as a single message without any quotation marks or surrounding punctuation.
"""

    try:
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": system_message},
            ],
            max_tokens=40,
            temperature=0.85
        )
        if response.choices and response.choices[0].message.content.strip():
            prompt_message = response.choices[0].message.content.strip()
            return prompt_message
        else:
            #if participant_name and participant_name != "Anonymous":
            if is_valid_name(participant_name):

                return f"May I ask where you're from, {participant_name}?"
            else:
                return "May I ask where you're from?"
    except Exception as e:
        logger.error(f"Error generating region prompt with LLM: {e}")
        #if participant_name and participant_name != "Anonymous":
        if is_valid_name(participant_name):

            return f"May I ask where you're from, {participant_name}?"
        else:
            return "May I ask where you're from?"
