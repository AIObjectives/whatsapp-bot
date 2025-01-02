





import firebase_admin
from firebase_admin import credentials, firestore
from fastapi import FastAPI, Form, Response
from openai import OpenAI
from decouple import config
import logging
import json
from twilio.rest import Client as TwilioClient
import os

import asyncio


from agent_functions3_dry import (
    #generate_bot_instructions,
    send_message,
    extract_text_from_messages,
    generate_initial_message1,
    extract_name_with_llm,
    extract_event_id_with_llm,
    event_id_valid,
    create_welcome_message,
    # Assuming these functions are implemented
    extract_age_with_llm,
    extract_gender_with_llm,
    extract_region_with_llm, 
    generate_region_prompt_with_llm, 
    generate_gender_prompt_with_llm, 
    generate_age_prompt_with_llm
)

from config1 import (
    db,
    logger,
    OpenAI,
    client,
    twilio_client,
    twilio_number,
    assistant_id,
    twilio_account_sid,
    twilio_auth_token,
    cred,
    app,
)

from fastapi import HTTPException, Response, Form, UploadFile, File
from uuid import uuid4

import requests
import io
from pydub import AudioSegment

from requests.auth import HTTPBasicAuth

import openai
import re
from datetime import datetime, timedelta

# Configuration
openai_api_key = config('OPENAI_API_KEY')
openai_engine = 'gpt-4o'





def update_global_asked_count(event_id, question_id):
    """Manually increment the global asked_count for a specific question in the info document."""
    # Fetch the info document for the event
    info_doc_ref = db.collection(f'AOI_{event_id}').document('info')
    info_doc = info_doc_ref.get()

    if not info_doc.exists:
        logger.error(f"No event info found for event ID: {event_id}")
        return

    # Get current questions data to ensure question_id exists
    info_data = info_doc.to_dict()
    questions = info_data.get('questions', [])

    # Find the question with the specified ID and increment its asked_count
    updated_questions = []
    question_found = False

    for question in questions:
        if question.get('id') == question_id:
            # Increment the asked_count for the matching question
            question['asked_count'] = question.get('asked_count', 0) + 1
            question_found = True
        # Add the question to the updated list (whether modified or not)
        updated_questions.append(question)

    if not question_found:
        logger.error(f"Question ID: {question_id} not found in event questions.")
        return

    # Update only the questions array in Firestore with the modified asked_count
    info_doc_ref.update({'questions': updated_questions})
    logger.info(f"Global asked count manually incremented for question ID: {question_id}")



import re

def generate_bot_instructions(event_id, normalized_phone):
    """
    Generate dynamic bot instructions based on event details and user interactions.
    Includes all follow-up questions in the instructions so the agent can pick one
    or come up with its own if none are relevant.
    """
    # 1. Fetch event details from Firestore
    event_info_ref = db.collection(f'AOI_{event_id}').document('info')
    event_info_doc = event_info_ref.get()

    if event_info_doc.exists:
        event_info = event_info_doc.to_dict()
        event_name = event_info.get('event_name', 'the event')
        event_location = event_info.get('event_location', 'the location')
        event_background = event_info.get('event_background', 'the background')
        bot_topic = event_info.get('bot_topic', '')
        bot_aim = event_info.get('bot_aim', '')
        bot_principles = event_info.get('bot_principles', [])
        bot_personality = event_info.get('bot_personality', '')
        bot_additional_prompts = event_info.get('bot_additional_prompts', [])

        # Retrieve toggle & question list
        follow_up_toggle = event_info.get('follow_up_questions', {})
        follow_up_enabled = follow_up_toggle.get('enabled', False)
        follow_up_list = follow_up_toggle.get('questions', [])
    else:
        # Default if event info is missing
        event_name = 'the event'
        event_location = 'the location'
        event_background = 'the background'
        bot_topic = ''
        bot_aim = ''
        bot_principles = []
        bot_personality = ''
        bot_additional_prompts = []

        follow_up_toggle = {}
        follow_up_enabled = False
        follow_up_list = []

    # 2. Fetch past interactions for context
    event_doc_ref = db.collection(f'AOI_{event_id}').document(normalized_phone)
    event_doc = event_doc_ref.get()
    if event_doc.exists:
        user_data = event_doc.to_dict()
        interactions = user_data.get('interactions', [])
        bot_questions = [interaction.get('response') for interaction in interactions if 'response' in interaction]
        user_messages = [interaction.get('message') for interaction in interactions if 'message' in interaction]

        # Compile the last ~30 interactions to show context
        past_interactions_text = ''
        for q, m in zip(bot_questions[-30:], user_messages[-30:]):
            past_interactions_text += f'Bot: {q}\nUser: {m}\n'
    else:
        past_interactions_text = ''

    # 3. Prepare text for principles & additional prompts
    bot_principles_text = '\n'.join(f'- {principle}' for principle in bot_principles)
    bot_additional_prompts_text = '\n'.join(f'- {prompt}' for prompt in bot_additional_prompts)

    # 4. Convert follow-up questions into a simple enumerated list to show in prompt
    if follow_up_enabled and follow_up_list:
        print("11111Follow-up questions enabled and list is not empty")
        follow_up_list_text = "\n".join(f"{idx+1}. {q}" for idx, q in enumerate(follow_up_list))
    else:
        follow_up_list_text = ""  # If toggle is off or list is empty, no list is provided
        print("NOT ACTIVEFALSEEE-11111Follow-up questions enabled and list is not empty")

    

    # 5. Instructions for the LLM to pick a follow-up question or create its own
    if follow_up_enabled and follow_up_list:
        follow_up_instructions = """
Below is a list of possible follow-up questions. 
Please read the user's last response, pick (or adapt) the question that best fits their context, 
and replace "X" with relevant keywords or content from the user's response. 

If none of these follow-up questions seem relevant, 
please create your own question or statement to deepen the conversation.

Possible Follow-up Questions:
""" + follow_up_list_text
    else:
        # If toggle is OFF or there's no list, revert to a single "default" approach
        follow_up_instructions = """
No specialized follow-up questions are enabled at this time. 
Use your own approach to continue the conversation in a thoughtful way.
"""

    # 6. Build final instructions
    instructions = f"""
You are an "Elicitation bot", designed to interact conversationally with individual users on WhatsApp, and help draw out their opinions towards the assigned topic. The conversation should be engaging, friendly, and sometimes humorous to keep the interaction light-hearted yet productive. You provide an experience that lets users feel better heard. You also encourage users to think from a wider perspective and help them revise their initial opinions by considering broader perspectives.

### Event Information
Event Name: {event_name}
Event Location: {event_location}
Event Background: {event_background}

### Topic, Bot Objective, Conversation Principles, and Bot Personality
- **Topic**: {bot_topic}
- **Aim**: {bot_aim}
- **Principles**:
{bot_principles_text}
- **Personality**: {bot_personality}

### Past User Interactions
{past_interactions_text}

### Additional Prompts
{bot_additional_prompts_text}

### Follow-Up Questions and Instructions
{follow_up_instructions}

### Conversation Management
- If the user would like to change their name or event during the session, respond with: 'To change your name, type "change name [new name]". To change your event, type "change event [event name]".'
- Be respectful and avoid sensitive topics unless they are part of the assigned topic.
- Do not provide personal opinions or biases.

### Final Notes
Your role is to facilitate a meaningful conversation that helps the user express their authentic opinions on {bot_topic}, while ensuring they feel heard and valued.
""".strip()

    return instructions





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



@app.post("/message/")
async def reply(Body: str = Form(...), From: str = Form(...), MediaUrl0: str = Form(default=None)):
    logger.info(f"Received message from {From} with body '{Body}' and media URL {MediaUrl0}")

    # Normalize phone number
    normalized_phone = From.replace("+", "").replace("-", "").replace(" ", "")

    # Step 1: Retrieve or initialize user tracking document
    user_tracking_ref = db.collection('user_event_tracking').document(normalized_phone)
    user_tracking_doc = user_tracking_ref.get()
    if user_tracking_doc.exists:
        user_data = user_tracking_doc.to_dict()
    else:
        # Initialize user document with additional awaiting flags
        user_data = {
            'events': [],
            'current_event_id': None,
            'awaiting_event_id': False,
            'awaiting_name': False,
            'awaiting_age': False,
            'awaiting_gender': False,
            'awaiting_region': False,
            'awaiting_event_change_confirmation': False,
            'last_inactivity_prompt': None
        }
        user_tracking_ref.set(user_data)

    # Variables for easier access
    user_events = user_data.get('events', [])
    current_event_id = user_data.get('current_event_id')
    awaiting_event_id = user_data.get('awaiting_event_id', False)
    awaiting_name = user_data.get('awaiting_name', False)
    awaiting_age = user_data.get('awaiting_age', False)
    awaiting_gender = user_data.get('awaiting_gender', False)
    awaiting_region = user_data.get('awaiting_region', False)
    awaiting_event_change_confirmation = user_data.get('awaiting_event_change_confirmation', False)
    last_inactivity_prompt = user_data.get('last_inactivity_prompt', None)

    # Remove duplicate events from user_events
    unique_events = {}
    for event in user_events:
        event_id = event['event_id']
        if event_id not in unique_events:
            unique_events[event_id] = event
        else:
            # If duplicate, keep the most recent timestamp
            existing_event_time = datetime.fromisoformat(unique_events[event_id]['timestamp'])
            current_event_time = datetime.fromisoformat(event['timestamp'])
            if current_event_time > existing_event_time:
                unique_events[event_id] = event  # Update to more recent event
    user_events = list(unique_events.values())

    # Update user_events in user_data
    user_data['events'] = user_events

    # Update the deduplicated events in Firestore
    user_tracking_ref.update({'events': user_events})

    # Check if current_event_id is still valid
    if current_event_id:
        event_info_ref = db.collection(f'AOI_{current_event_id}').document('info')
        event_info_doc = event_info_ref.get()
        if not event_info_doc.exists:
            # Event is no longer valid
            # Remove the invalid event from user's event list
            user_events = [event for event in user_events if event['event_id'] != current_event_id]

            user_tracking_ref.update({
                'current_event_id': None,
                'events': user_events,  # Update the user's events list
                'awaiting_event_id': True
            })
            send_message(From, f"The event '{current_event_id}' is no longer active. Please enter a new event ID to continue.")
            return Response(status_code=200)

    # Step 2: Check for inactivity (every 24 hours)
    current_time = datetime.utcnow()
    user_inactive = False

    # Determine if user has been inactive for more than 24 hours in all events
    if user_events:
        last_interaction_times = []
        for event in user_events:
            event_timestamp = event.get('timestamp', None)
            if event_timestamp:
                event_time = datetime.fromisoformat(event_timestamp)
                last_interaction_times.append(event_time)

        if last_interaction_times:
            most_recent_interaction = max(last_interaction_times)
            time_since_last_interaction = current_time - most_recent_interaction

            if time_since_last_interaction > timedelta(hours=24):
                user_inactive = True

    # Check if we should send an inactivity prompt
    if user_inactive:
        # Check if we've already sent an inactivity prompt within the last 24 hours
        if last_inactivity_prompt:
            last_prompt_time = datetime.fromisoformat(last_inactivity_prompt)
            time_since_last_prompt = current_time - last_prompt_time
            if time_since_last_prompt < timedelta(hours=24):
                # We've already sent a prompt recently, do not send another
                pass
            else:
                # Send inactivity prompt
                event_list = '\n'.join([f"{i+1}. {event['event_id']}" for i, event in enumerate(user_events)])
                send_message(From, f"You have been inactive for more than 24 hours.\nYour events:\n{event_list}\nPlease reply with the number of the event you'd like to continue.")
                user_tracking_ref.update({'last_inactivity_prompt': current_time.isoformat()})
                return Response(status_code=200)
        else:
            # Send inactivity prompt
            event_list = '\n'.join([f"{i+1}. {event['event_id']}" for i, event in enumerate(user_events)])
            send_message(From, f"You have been inactive for more than 24 hours.\nYour events:\n{event_list}\nPlease reply with the number of the event you'd like to continue.")
            user_tracking_ref.update({'last_inactivity_prompt': current_time.isoformat()})
            return Response(status_code=200)

    # Add 'invalid_attempts' to track invalid responses
    invalid_attempts = user_data.get('invalid_attempts', 0)

    # Step 3: Handle user selection for event continuation
    if last_inactivity_prompt:
        if Body.isdigit() and 1 <= int(Body) <= len(user_events):
            # User selected an event to continue
            selected_event = user_events[int(Body) - 1]['event_id']
            send_message(From, f"You are now continuing in event {selected_event}.")
            current_event_id = selected_event

            # Update the timestamp of the selected event in user_events
            current_time_iso = datetime.utcnow().isoformat()
            for event in user_events:
                if event['event_id'] == selected_event:
                    event['timestamp'] = current_time_iso  # Update timestamp
                    break

            # Reset last_inactivity_prompt and invalid_attempts
            user_tracking_ref.update({
                'current_event_id': current_event_id,
                'events': user_events,
                'last_inactivity_prompt': None,
                'invalid_attempts': 0  # Reset attempts
            })
            return Response(status_code=200)
        else:
            # Handle invalid response to inactivity prompt
            invalid_attempts += 1  # Increment invalid attempts
            if invalid_attempts < 2:
                # Allow the user to try again
                user_tracking_ref.update({'invalid_attempts': invalid_attempts})
                send_message(From, "The input you provided does not match any of the events. Please reply with the number corresponding to the event you'd like to continue.")
                return Response(status_code=200)
            else:
                # Exceeded invalid attempts
                if current_event_id:
                    send_message(From, f"No valid selection made. Continuing with your current event '{current_event_id}'.")
                    # Update the timestamp of the current event in user_events
                    current_time_iso = datetime.utcnow().isoformat()
                    for event in user_events:
                        if event['event_id'] == current_event_id:
                            event['timestamp'] = current_time_iso  # Update timestamp
                            break
                    # Update user_tracking_ref with current_event_id and events
                    user_tracking_ref.update({
                        'current_event_id': current_event_id,
                        'events': user_events,
                        'last_inactivity_prompt': None,
                        'invalid_attempts': 0
                    })
                    return Response(status_code=200)

                else:
                    # No current event; prompt for event ID
                    send_message(From, "No valid selection made and no current event found. Please provide your event ID to proceed.")
                    user_tracking_ref.update({
                        'awaiting_event_id': True,
                        'last_inactivity_prompt': None,
                        'invalid_attempts': 0
                    })
                    return Response(status_code=200)

    elif awaiting_event_change_confirmation:
        # Existing code for event change confirmation
        if Body.strip().lower() in ['yes', 'y']:
            # User confirms to change event
            new_event_id = user_data.get('new_event_id_pending')
            if not event_id_valid(new_event_id):
                send_message(From, f"The event ID '{new_event_id}' is no longer valid. Please enter a new event ID.")
                user_tracking_ref.update({
                    'awaiting_event_change_confirmation': False,
                    'new_event_id_pending': None,
                    'awaiting_event_id': True
                })
                return Response(status_code=200)

            current_event_id = new_event_id
            current_time_iso = datetime.utcnow().isoformat()

            # Add or update the event in the user's event list
            event_exists = False
            for event in user_events:
                if event['event_id'] == current_event_id:
                    event['timestamp'] = current_time_iso  # Update timestamp
                    event_exists = True
                    break
            if not event_exists:
                user_events.append({
                    'event_id': current_event_id,
                    'timestamp': current_time_iso
                })

            # Fetch extraction settings
            event_details_ref = db.collection(f'AOI_{current_event_id}').document('info')
            event_details_doc = event_details_ref.get()
            if event_details_doc.exists:
                event_details = event_details_doc.to_dict()
                extraction_settings = event_details.get('extraction_settings', {})
                name_extraction_enabled = extraction_settings.get('name_extraction', True)
                age_extraction_enabled = extraction_settings.get('age_extraction', False)
                gender_extraction_enabled = extraction_settings.get('gender_extraction', False)
                region_extraction_enabled = extraction_settings.get('region_extraction', False)
            else:
                name_extraction_enabled = True
                age_extraction_enabled = False
                gender_extraction_enabled = False
                region_extraction_enabled = False

            # Initialize awaiting flags
            awaiting_name = name_extraction_enabled
            awaiting_age = False
            awaiting_gender = False
            awaiting_region = False

            user_tracking_ref.update({
                'current_event_id': current_event_id,
                'events': user_events,
                'awaiting_event_change_confirmation': False,
                'new_event_id_pending': None,
                'awaiting_name': awaiting_name,
                'awaiting_age': awaiting_age,
                'awaiting_gender': awaiting_gender,
                'awaiting_region': awaiting_region
            })

            

            event_doc_ref = db.collection(f'AOI_{current_event_id}').document(normalized_phone)
            event_doc = event_doc_ref.get()
            if not event_doc.exists:
                #user_data = initialize_user_document(current_event_id, normalized_phone)
                if not user_data:
                    # Handle the case where event info is missing
                    send_message(From, "There was an issue accessing event information. Please try again later.")
                    return Response(status_code=200)
                participant_name = user_data.get('name', None)
            else:
                data = event_doc.to_dict()
                participant_name = data.get('name', None)
                if participant_name:
                    user_tracking_ref.update({'awaiting_name': False})



                    # Proceed to check if other features need to be collected
                    if age_extraction_enabled and 'age' not in data:
                        user_tracking_ref.update({'awaiting_age': True})
                        send_message(From, "Please tell me your age.")
                        return Response(status_code=200)
                    elif gender_extraction_enabled and 'gender' not in data:
                        user_tracking_ref.update({'awaiting_gender': True})
                        send_message(From, "Please tell me your gender.")
                        return Response(status_code=200)
                    elif region_extraction_enabled and 'region' not in data:
                        user_tracking_ref.update({'awaiting_region': True})
                        send_message(From, "Please tell me your region.")
                        return Response(status_code=200)
                    else:
                        send_message(From, f"You have switched to event {current_event_id}. Please continue with the conversation.")
                        return Response(status_code=200)

            if awaiting_name:
                send_message(From, f"You have switched to event {current_event_id}. Now, please tell me your name.")
            else:
                send_message(From, f"You have switched to event {current_event_id}.")
                # Proceed to ask for next feature if enabled
                if age_extraction_enabled:
                    user_tracking_ref.update({'awaiting_age': True})
                    send_message(From, "Please tell me your age.")
                elif gender_extraction_enabled:
                    user_tracking_ref.update({'awaiting_gender': True})
                    send_message(From, "Please tell me your gender.")
                elif region_extraction_enabled:
                    user_tracking_ref.update({'awaiting_region': True})
                    send_message(From, "Please tell me your region.")
                else:
                    send_message(From, "You can now continue with the conversation.")
            return Response(status_code=200)
        else:
            # User cancels event change
            user_tracking_ref.update({
                'awaiting_event_change_confirmation': False,
                'new_event_id_pending': None
            })
            send_message(From, f"Event change cancelled. You remain in event {current_event_id}. Please continue with the conversation.")
            return Response(status_code=200)

    elif awaiting_event_id:
        # User is expected to provide event ID
        extracted_event_id = extract_event_id_with_llm(Body)
        if extracted_event_id and event_id_valid(extracted_event_id):
            event_id = extracted_event_id
            current_event_id = event_id
            current_time_iso = datetime.utcnow().isoformat()

            # Check if event already exists in user_events
            event_exists = False
            for event in user_events:
                if event['event_id'] == event_id:
                    event['timestamp'] = current_time_iso  # Update timestamp
                    event_exists = True
                    break
            if not event_exists:
                user_events.append({
                    'event_id': event_id,
                    'timestamp': current_time_iso
                })

            # Fetch extraction settings
            event_details_ref = db.collection(f'AOI_{current_event_id}').document('info')
            event_details_doc = event_details_ref.get()
            if event_details_doc.exists:
                event_details = event_details_doc.to_dict()
                extraction_settings = event_details.get('extraction_settings', {})
                name_extraction_enabled = extraction_settings.get('name_extraction', True)
                age_extraction_enabled = extraction_settings.get('age_extraction', False)
                gender_extraction_enabled = extraction_settings.get('gender_extraction', False)
                region_extraction_enabled = extraction_settings.get('region_extraction', False)
            else:
                name_extraction_enabled = True
                age_extraction_enabled = False
                gender_extraction_enabled = False
                region_extraction_enabled = False

            # Initialize awaiting flags
            awaiting_name = name_extraction_enabled
            awaiting_age = False
            awaiting_gender = False
            awaiting_region = False

            user_tracking_ref.update({
                'events': user_events,
                'current_event_id': current_event_id,
                'awaiting_event_id': False,
                'awaiting_name': awaiting_name,
                'awaiting_age': awaiting_age,
                'awaiting_gender': awaiting_gender,
                'awaiting_region': awaiting_region
            })

            

            event_doc_ref = db.collection(f'AOI_{event_id}').document(normalized_phone)
            event_doc = event_doc_ref.get()
            if not event_doc.exists:
                #user_data = initialize_user_document(event_id, normalized_phone)
                if not user_data:
                    # Handle the case where event info is missing
                    send_message(From, "There was an issue accessing event information. Please try again later.")
                    return Response(status_code=200)
                participant_name = user_data.get('name', None)
            else:
                data = event_doc.to_dict()
                participant_name = data.get('name', None)

            if awaiting_name:
                #send_message(From, f"Thank you! Your event ID has been set to {event_id}. Now, please tell me your name.")
                
                #send_message(From, f"""Hello and welcome to this demo of Talk to the City's smart elicitation tools! Please tell me your name, or say "Anonymous" if you'd rather your answers aren't associated with your name.""")
                default_initial_message = """Thank you for agreeing to participate. We want to assure you that none of the data you provide will be directly linked back to you. Your identity is protected through secure and encrypted links. How would you like to be addressed during this session? (Please feel free to use your own name, or another name.)"""

                default_completion_message = """Congratulations, you’ve completed the survey! Thank you so much for taking the time to share your experiences. Your input will help Utopia Network Kenya create programs and advocate for meaningful change. If you have any questions, concerns, or feedback, please don’t hesitate to contact us. Your voice matters, and we deeply appreciate your participation."""

                event_info_ref = db.collection(f'AOI_{current_event_id}').document('info')
                event_info_doc = event_info_ref.get()
                if event_info_doc.exists:
                    event_info = event_info_doc.to_dict()
                    initial_message = event_info.get('initial_message', default_initial_message)
                else:
                    initial_message = default_initial_message

                send_message(From, initial_message)

            else:
                #send_message(From, f"Thank you! Your event ID has been set to {event_id}.")
                #send_message(From, f"""Hello and welcome to this demo of Talk to the City's smart elicitation tools! Please tell me your name, or say "Anonymous" if you'd rather your answers aren't associated with your name.""")
                default_initial_message = """Thank you for agreeing to participate. We want to assure you that none of the data you provide will be directly linked back to you. Your identity is protected through secure and encrypted links. How would you like to be addressed during this session? (Please feel free to use your own name, or another name.)"""

                default_completion_message = """Congratulations, you’ve completed the survey! Thank you so much for taking the time to share your experiences. Your input will help Utopia Network Kenya create programs and advocate for meaningful change. If you have any questions, concerns, or feedback, please don’t hesitate to contact us. Your voice matters, and we deeply appreciate your participation."""

                event_info_ref = db.collection(f'AOI_{current_event_id}').document('info')
                event_info_doc = event_info_ref.get()
                if event_info_doc.exists:
                    event_info = event_info_doc.to_dict()
                    initial_message = event_info.get('initial_message', default_initial_message)
                else:
                    initial_message = default_initial_message

                send_message(From, initial_message)




                # Proceed to ask for next feature if enabled
                if age_extraction_enabled:
                    user_tracking_ref.update({'awaiting_age': True})
                    send_message(From, "Please tell me your age.")
                elif gender_extraction_enabled:
                    user_tracking_ref.update({'awaiting_gender': True})
                    send_message(From, "Please tell me your gender.")
                elif region_extraction_enabled:
                    user_tracking_ref.update({'awaiting_region': True})
                    send_message(From, "Please tell me your region.")
                else:
                    send_message(From, "You can now start the conversation.")
            return Response(status_code=200)
        else:
            logger.info(f"Invalid event ID: {Body}")
            send_message(From, "The event ID you provided is invalid. Please re-enter the correct event ID or contact support.")
            return Response(status_code=200)

    elif awaiting_name or awaiting_age or awaiting_gender or awaiting_region:
        # Fetch participant data
        event_doc_ref = db.collection(f'AOI_{current_event_id}').document(normalized_phone)
        event_doc = event_doc_ref.get()
        participant_data = event_doc.to_dict() if event_doc.exists else {}


        
        if MediaUrl0:
            # Handle media URLs (e.g., audio)
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


        

        # Fetch extraction settings
        event_details_ref = db.collection(f'AOI_{current_event_id}').document('info')
        event_details_doc = event_details_ref.get()
        if event_details_doc.exists:
            event_details = event_details_doc.to_dict()
            extraction_settings = event_details.get('extraction_settings', {})
            name_extraction_enabled = extraction_settings.get('name_extraction', True)
            age_extraction_enabled = extraction_settings.get('age_extraction', False)
            gender_extraction_enabled = extraction_settings.get('gender_extraction', False)
            region_extraction_enabled = extraction_settings.get('region_extraction', False)
        else:
            name_extraction_enabled = True
            age_extraction_enabled = False
            gender_extraction_enabled = False
            region_extraction_enabled = False

       

        if awaiting_name:
            # Process name
            extracted_name = extract_name_with_llm(Body, current_event_id)
            
            # if extracted_name and extracted_name.lower() == "anonymous":
            #     event_doc_ref.update({'name': "Anonymous"})
            #     participant_data['name'] = "Anonymous"
            
            # elif extracted_name:
            #     # Only call strip() if extracted_name is not None
            #     extracted_name = extracted_name.strip().strip('"').strip("'")
            #     if not is_valid_name(extracted_name):
            #         event_doc_ref.set({'name': None}, merge=True)
            #         participant_data['name'] = None
            #     else:
            #         event_doc_ref.set({'name': extracted_name}, merge=True)
            #         participant_data['name'] = extracted_name
            # else:
            #     event_doc_ref.set({'name': None}, merge=True)
            #     participant_data['name'] = None

            # user_tracking_ref.update({'awaiting_name': False})


            if extracted_name and extracted_name.lower() == "anonymous":
                event_doc_ref.set({'name': "Anonymous"}, merge=True)
                participant_data['name'] = "Anonymous"
            elif extracted_name:
                extracted_name = extracted_name.strip().strip('"').strip("'")
                if not is_valid_name(extracted_name):
                    event_doc_ref.set({'name': None}, merge=True)
                    participant_data['name'] = None
                else:
                    event_doc_ref.set({'name': extracted_name}, merge=True)
                    participant_data['name'] = extracted_name
            else:
                event_doc_ref.set({'name': None}, merge=True)
                participant_data['name'] = None

            user_tracking_ref.update({'awaiting_name': False})


            # Proceed to next feature if enabled
            if age_extraction_enabled:
                user_tracking_ref.update({'awaiting_age': True})
                prompt_message = generate_age_prompt_with_llm(participant_data, current_event_id)
                send_message(From, prompt_message)
            elif gender_extraction_enabled:
                user_tracking_ref.update({'awaiting_gender': True})
                prompt_message = generate_gender_prompt_with_llm(participant_data, current_event_id)
                send_message(From, prompt_message)
            elif region_extraction_enabled:
                user_tracking_ref.update({'awaiting_region': True})
                prompt_message = generate_region_prompt_with_llm(participant_data, current_event_id)
                send_message(From, prompt_message)
            else:
                welcome_msg = create_welcome_message(current_event_id, participant_name=participant_data['name'])
                send_message(From, welcome_msg)
                await asyncio.sleep(2)

                event_info_ref = db.collection(f'AOI_{current_event_id}').document('info')
                event_info_doc = event_info_ref.get()
                main_question="Here is the question:"
                if event_info_doc.exists:
                    event_info = event_info_doc.to_dict()
                    main_question = event_info.get('main_question', main_question)
                else:
                    main_question = main_question

                #send_message(From, main_question)

                #send_message(From, f""" Please tell us about how you identify in terms of your (a) gender (eg man, woman, non- binary etc) and (b) sexuality (eg lesbian, gay, bisexual, queer etc)? Please also say something about whether you express yourself in a more “femme” or “masculine” or other way.""")
                await asyncio.to_thread(send_message, From, main_question)

            return Response(status_code=200)






        elif awaiting_age:
            # Process age
            extracted_age = extract_age_with_llm(Body, current_event_id)
            if extracted_age == "No age found":
                # User did not provide age, proceed to next step
                event_doc_ref.update({'age': None})
            else:
                event_doc_ref.update({'age': extracted_age})
            user_tracking_ref.update({'awaiting_age': False})

            # Proceed to next feature if enabled
            if gender_extraction_enabled:
                user_tracking_ref.update({'awaiting_gender': True})
                prompt_message = generate_gender_prompt_with_llm(participant_data, current_event_id)
                send_message(From, prompt_message)
            elif region_extraction_enabled:
                user_tracking_ref.update({'awaiting_region': True})
                prompt_message = generate_region_prompt_with_llm(participant_data, current_event_id)
                send_message(From, prompt_message)
            else:
                participant_name = participant_data.get('name', None)
                welcome_msg = create_welcome_message(current_event_id, participant_name=participant_name)
                send_message(From, welcome_msg)
                # After sending the welcome message
                await asyncio.sleep(2)

                # #send_message(From, f""" Please tell us about how you identify in terms of your (a) gender (eg man, woman, non- binary etc) and (b) sexuality (eg lesbian, gay, bisexual, queer etc)? Please also say something about whether you express yourself in a more “femme” or “masculine” or other way.""")
                # await asyncio.to_thread(send_message, From, "Q1. Please tell us about how you identify in terms of your (a) gender (eg man, woman, non- binary etc) and (b) sexuality (eg lesbian, gay, bisexual, queer etc)? Please also say something about whether you express yourself in a more “femme” or “masculine” or other way.")

                event_info_ref = db.collection(f'AOI_{current_event_id}').document('info')
                event_info_doc = event_info_ref.get()
                main_question="Here is the question:"
                if event_info_doc.exists:
                    event_info = event_info_doc.to_dict()
                    main_question = event_info.get('main_question', main_question)
                else:
                    main_question = main_question

                #send_message(From, main_question)

                #send_message(From, f""" Please tell us about how you identify in terms of your (a) gender (eg man, woman, non- binary etc) and (b) sexuality (eg lesbian, gay, bisexual, queer etc)? Please also say something about whether you express yourself in a more “femme” or “masculine” or other way.""")
                await asyncio.to_thread(send_message, From, main_question)

            return Response(status_code=200)



        elif awaiting_gender:
            # Process gender
            extracted_gender = extract_gender_with_llm(Body, current_event_id)
            if extracted_gender == "No gender found":
                # User did not provide gender, proceed to next step
                event_doc_ref.update({'gender': None})
            else:
                event_doc_ref.update({'gender': extracted_gender})
            user_tracking_ref.update({'awaiting_gender': False})

            # Proceed to next feature if enabled
            if region_extraction_enabled:
                user_tracking_ref.update({'awaiting_region': True})
                prompt_message = generate_region_prompt_with_llm(participant_data, current_event_id)
                send_message(From, prompt_message)
            else:
                participant_name = participant_data.get('name', None)
                welcome_msg = create_welcome_message(current_event_id, participant_name=participant_name)
                send_message(From, welcome_msg)

                # After sending the welcome message
                await asyncio.sleep(2)

                #send_message(From, f""" Please tell us about how you identify in terms of your (a) gender (eg man, woman, non- binary etc) and (b) sexuality (eg lesbian, gay, bisexual, queer etc)? Please also say something about whether you express yourself in a more “femme” or “masculine” or other way.""")
                #await asyncio.to_thread(send_message, From, "Q1. Please tell us about how you identify in terms of your (a) gender (eg man, woman, non- binary etc) and (b) sexuality (eg lesbian, gay, bisexual, queer etc)? Please also say something about whether you express yourself in a more “femme” or “masculine” or other way.")

                event_info_ref = db.collection(f'AOI_{current_event_id}').document('info')
                event_info_doc = event_info_ref.get()
                main_question="Here is the question:"
                if event_info_doc.exists:
                    event_info = event_info_doc.to_dict()
                    main_question = event_info.get('main_question', main_question)
                else:
                    main_question = main_question

                #send_message(From, main_question)

                #send_message(From, f""" Please tell us about how you identify in terms of your (a) gender (eg man, woman, non- binary etc) and (b) sexuality (eg lesbian, gay, bisexual, queer etc)? Please also say something about whether you express yourself in a more “femme” or “masculine” or other way.""")
                await asyncio.to_thread(send_message, From, main_question)
            return Response(status_code=200)


        elif awaiting_region:
            # Process region
            extracted_region = extract_region_with_llm(Body, current_event_id)
            if extracted_region == "No region found":
                # User did not provide region, proceed to next step
                event_doc_ref.update({'region': None})
            else:
                event_doc_ref.update({'region': extracted_region})
            user_tracking_ref.update({'awaiting_region': False})

            # All features collected, send welcome message
            participant_name = participant_data.get('name', None)
            welcome_msg = create_welcome_message(current_event_id, participant_name=participant_name)
            send_message(From, welcome_msg)

            # After sending the welcome message
            await asyncio.sleep(2)


            #send_message(From, f""" Please tell us about how you identify in terms of your (a) gender (eg man, woman, non- binary etc) and (b) sexuality (eg lesbian, gay, bisexual, queer etc)? Please also say something about whether you express yourself in a more “femme” or “masculine” or other way.""")
            #await asyncio.to_thread(send_message, From, "Q1. Please tell us about how you identify in terms of your (a) gender (eg man, woman, non- binary etc) and (b) sexuality (eg lesbian, gay, bisexual, queer etc)? Please also say something about whether you express yourself in a more “femme” or “masculine” or other way.")

            event_info_ref = db.collection(f'AOI_{current_event_id}').document('info')
            event_info_doc = event_info_ref.get()
            main_question="Here is the question:"
            if event_info_doc.exists:
                event_info = event_info_doc.to_dict()
                main_question = event_info.get('main_question', main_question)
            else:
                main_question = main_question

            #send_message(From, main_question)

            #send_message(From, f""" Please tell us about how you identify in terms of your (a) gender (eg man, woman, non- binary etc) and (b) sexuality (eg lesbian, gay, bisexual, queer etc)? Please also say something about whether you express yourself in a more “femme” or “masculine” or other way.""")
            await asyncio.to_thread(send_message, From, main_question)

            return Response(status_code=200)



   

    elif not current_event_id:
        # User has no current event, attempt to extract event ID from Body
        extracted_event_id = extract_event_id_with_llm(Body)
        if extracted_event_id and event_id_valid(extracted_event_id):
            event_id = extracted_event_id
            current_event_id = event_id
            current_time_iso = datetime.utcnow().isoformat()

            # Check if event already exists in user_events
            event_exists = False
            for event in user_events:
                if event['event_id'] == event_id:
                    event['timestamp'] = current_time_iso  # Update timestamp
                    event_exists = True
                    break
            if not event_exists:
                user_events.append({
                    'event_id': event_id,
                    'timestamp': current_time_iso
                })

            # Fetch extraction settings
            event_details_ref = db.collection(f'AOI_{current_event_id}').document('info')
            event_details_doc = event_details_ref.get()
            if event_details_doc.exists:
                event_details = event_details_doc.to_dict()
                extraction_settings = event_details.get('extraction_settings', {})
                name_extraction_enabled = extraction_settings.get('name_extraction', True)
                age_extraction_enabled = extraction_settings.get('age_extraction', False)
                gender_extraction_enabled = extraction_settings.get('gender_extraction', False)
                region_extraction_enabled = extraction_settings.get('region_extraction', False)
            else:
                name_extraction_enabled = True
                age_extraction_enabled = False
                gender_extraction_enabled = False
                region_extraction_enabled = False

            # Initialize awaiting flags
            awaiting_name = name_extraction_enabled
            awaiting_age = False
            awaiting_gender = False
            awaiting_region = False

            user_tracking_ref.update({
                'events': user_events,
                'current_event_id': current_event_id,
                'awaiting_event_id': False,
                'awaiting_name': awaiting_name,
                'awaiting_age': awaiting_age,
                'awaiting_gender': awaiting_gender,
                'awaiting_region': awaiting_region
            })

          



            event_doc_ref = db.collection(f'AOI_{event_id}').document(normalized_phone)
            event_doc = event_doc_ref.get()
            if not event_doc.exists:
                #user_data = initialize_user_document(event_id, normalized_phone)
                if not user_data:
                    # Handle the case where event info is missing
                    send_message(From, "There was an issue accessing event information. Please try again later.")
                    return Response(status_code=200)
                participant_name = user_data.get('name', None)
            else:
                data = event_doc.to_dict()
                participant_name = data.get('name', None)

            if awaiting_name:
                #send_message(From, f"Thank you! Your event ID has been set to {event_id}. Now, please tell me your name.")
                #send_message(From, f"""Hello and welcome to this demo of Talk to the City's smart elicitation tools! Please tell me your name, or say "Anonymous" if you'd rather your answers aren't associated with your name.""")
                default_initial_message = """Thank you for agreeing to participate. We want to assure you that none of the data you provide will be directly linked back to you. Your identity is protected through secure and encrypted links. How would you like to be addressed during this session? (Please feel free to use your own name, or another name.)"""

                default_completion_message = """Congratulations, you’ve completed the survey! Thank you so much for taking the time to share your experiences. Your input will help Utopia Network Kenya create programs and advocate for meaningful change. If you have any questions, concerns, or feedback, please don’t hesitate to contact us. Your voice matters, and we deeply appreciate your participation."""

                event_info_ref = db.collection(f'AOI_{current_event_id}').document('info')
                event_info_doc = event_info_ref.get()
                if event_info_doc.exists:
                    event_info = event_info_doc.to_dict()
                    initial_message = event_info.get('initial_message', default_initial_message)
                else:
                    initial_message = default_initial_message

                send_message(From, initial_message)
            else:
                #send_message(From, f"Thank you! Your event ID has been set to {event_id}.")
                #send_message(From, f"""Hello and welcome to this demo of Talk to the City's smart elicitation tools! Please tell me your name, or say "Anonymous" if you'd rather your answers aren't associated with your name.""")
                default_initial_message = """Thank you for agreeing to participate. We want to assure you that none of the data you provide will be directly linked back to you. Your identity is protected through secure and encrypted links. How would you like to be addressed during this session? (Please feel free to use your own name, or another name.)"""

                default_completion_message = """Congratulations, you’ve completed the survey! Thank you so much for taking the time to share your experiences. Your input will help Utopia Network Kenya create programs and advocate for meaningful change. If you have any questions, concerns, or feedback, please don’t hesitate to contact us. Your voice matters, and we deeply appreciate your participation."""

                event_info_ref = db.collection(f'AOI_{current_event_id}').document('info')
                event_info_doc = event_info_ref.get()
                if event_info_doc.exists:
                    event_info = event_info_doc.to_dict()
                    initial_message = event_info.get('initial_message', default_initial_message)
                else:
                    initial_message = default_initial_message

                send_message(From, initial_message)
                # Proceed to ask for next feature if enabled
                if age_extraction_enabled:
                    user_tracking_ref.update({'awaiting_age': True})
                    send_message(From, "Please tell me your age.")
                elif gender_extraction_enabled:
                    user_tracking_ref.update({'awaiting_gender': True})
                    send_message(From, "Please tell me your gender.")
                elif region_extraction_enabled:
                    user_tracking_ref.update({'awaiting_region': True})
                    send_message(From, "Please tell me your region.")
                else:
                    send_message(From, "You can now start the conversation.")
            return Response(status_code=200)
        else:
            # Event ID not found in message, ask for event ID
            send_message(From, "Welcome! Please provide your event ID to proceed.")
            user_tracking_ref.update({'awaiting_event_id': True})
            return Response(status_code=200)


    # Handle "change name" command
    if Body.lower().startswith("change name "):
        new_name = Body[12:].strip()
        if new_name:
            event_doc_ref = db.collection(f'AOI_{current_event_id}').document(normalized_phone)
            event_doc_ref.update({'name': new_name})
            send_message(From, f"Your name has been updated to {new_name}. Please continue with the conversation.")
        else:
            send_message(From, "It seems there was an error updating your name. Please try again.")
        return Response(status_code=200)

    # Handle "change event" command
    elif Body.lower().startswith("change event "):
        new_event_id = Body[13:].strip()
        if event_id_valid(new_event_id):
            # Check if the user is already in the new event
            if new_event_id == current_event_id:
                send_message(From, f"You are already in event {new_event_id}.")
                return Response(status_code=200)
            # Prompt the user to confirm the event change
            send_message(From, f"You requested to change to event {new_event_id}. Please confirm by replying 'yes' or cancel with 'no'.")
            user_tracking_ref.update({
                'awaiting_event_change_confirmation': True,
                'new_event_id_pending': new_event_id
            })
        else:
            send_message(From, f"The event ID '{new_event_id}' is invalid. Please check and try again.")
        return Response(status_code=200)

    # Proceed with the conversation
    # Fetch event details and extraction settings
    event_details_ref = db.collection(f'AOI_{current_event_id}').document('info')
    event_details_doc = event_details_ref.get()

    # Set default values in case event details are missing
    event_name = "the event"
    event_location = ""
    welcome_message = "Welcome! You can now start sending text and audio messages."
    extraction_settings = {}
    name_extraction_enabled = True
    age_extraction_enabled = False
    gender_extraction_enabled = False
    region_extraction_enabled = False

    if event_details_doc.exists:
        event_details = event_details_doc.to_dict()
        event_name = event_details.get('event_name', event_name)
        event_location = event_details.get('event_location', event_location)
        welcome_message = event_details.get('welcome_message', welcome_message)
        extraction_settings = event_details.get('extraction_settings', {})
        name_extraction_enabled = extraction_settings.get('name_extraction', True)
        age_extraction_enabled = extraction_settings.get('age_extraction', False)
        gender_extraction_enabled = extraction_settings.get('gender_extraction', False)
        region_extraction_enabled = extraction_settings.get('region_extraction', False)

    # Generate event instructions
    event_instructions = generate_bot_instructions(current_event_id,normalized_phone)

    #Handle media messages (if any)
    if MediaUrl0:
        # Handle media URLs (e.g., audio)
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
    

    if Body.strip().lower() in ['finalize', 'finish']:
        # User wants to end the survey early
        #send_message(From, "Congratulations, you’ve completed the survey! Thank you so much for taking the time to share your experiences. Your input will help Utopia Network Kenya create programs and advocate for meaningful change. If you have any questions, concerns, or feedback, please don’t hesitate to contact us. Your voice matters, and we deeply appreciate your participation.")
        # Optionally, set survey_complete flag
        default_completion_message = """Congratulations, you’ve completing this! Thank you so much for taking the time to share your experiences.  Your voice matters, and we deeply appreciate your participation."""


        # Fetch 'completion_message' from Firebase
        event_info_ref = db.collection(f'AOI_{current_event_id}').document('info')
        event_info_doc = event_info_ref.get()
        if event_info_doc.exists:
            event_info = event_info_doc.to_dict()
            completion_message = event_info.get('completion_message', default_completion_message)
        else:
            completion_message = default_completion_message

        send_message(From, completion_message)

  


    event_doc_ref = db.collection(f'AOI_{current_event_id}').document(normalized_phone)
    event_doc = event_doc_ref.get()

    if event_doc.exists:
        data = event_doc.to_dict()
        interactions = data.get('interactions', [])
        participant_name = data.get('name', None)
        questions_asked = data.get('questions_asked', {})
        # Ensure all question IDs are present in questions_asked
        event_info_ref = db.collection(f'AOI_{current_event_id}').document('info')
        event_info_doc = event_info_ref.get()
        if event_info_doc.exists:
            event_info = event_info_doc.to_dict()
            questions = event_info.get('questions', [])
            question_ids = [str(question['id']) for question in questions]
            updated = False
            for q_id in question_ids:
                if q_id not in questions_asked:
                    questions_asked[q_id] = False
                    updated = True
            if updated:
                # Update the user document if questions_asked was modified
                event_doc_ref.update({'questions_asked': questions_asked})
    else:
        # Initialize the user document with a populated questions_asked
        if not data:
            # Handle the case where event info is missing
            send_message(From, "There was an issue accessing event information. Please try again later.")
            return Response(status_code=200)
        interactions = data.get('interactions', [])
        participant_name = data.get('name', None)
        questions_asked = data.get('questions_asked', {})

    if len(interactions) >= 450:
        send_message(From, "You have reached your interaction limit with AOI. Please contact AOI for further assistance.")
        return Response(status_code=200)

    # Proceed with the conversation
    thread = client.beta.threads.create()
    message = client.beta.threads.messages.create(
        thread_id=thread.id,
        role="user",
        content=Body
    )

    event_doc_ref.update({
        'interactions': firestore.ArrayUnion([{'message': Body}])
    })

    run = client.beta.threads.runs.create_and_poll(
        thread_id=thread.id,
        assistant_id=assistant_id,
        instructions=event_instructions
    )



    if run.status == 'completed':
        messages = client.beta.threads.messages.list(thread_id=thread.id)
        assistant_response = extract_text_from_messages(messages)

        

        send_message(From, assistant_response)
        event_doc_ref.update({
            'interactions': firestore.ArrayUnion([{'response': assistant_response}])
        })
    else:
        send_message(From, "There was an issue processing your request.")

    return Response(status_code=200)
