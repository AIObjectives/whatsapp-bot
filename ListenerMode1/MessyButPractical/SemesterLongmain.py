


#PERFECTION! Added additional, fully modifiable questions that can be managed directly from the Firestore database. 
# These questions can easily be added or deleted if you want to gather more data at the beginning, before starting the conference. 
# All the collected data will be stored in a separate column in the aggregated CSV file!
import firebase_admin
from firebase_admin import credentials, firestore
from fastapi import FastAPI, Form, Response
from openai import OpenAI
from decouple import config
import logging
import json
from twilio.rest import Client as TwilioClient
import os

from agent_functions2 import (
    send_message,
    extract_text_from_messages,
    generate_initial_message1,
    extract_name_with_llm,
    extract_event_id_with_llm,
    event_id_valid,
    create_welcome_message,
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


def generate_bot_instructions(event_id):
    """Generate dynamic bot instructions based on the event's name and location."""
    event_info_ref = db.collection(f'AOI_{event_id}').document('info')
    event_info_doc = event_info_ref.get()

    if event_info_doc.exists:
        event_info = event_info_doc.to_dict()
        event_name = event_info.get('event_name', 'the event')
        event_location = event_info.get('event_location', 'the location')
        event_background = event_info.get('event_background', 'the background')
    else:
        event_name = 'the event'
        event_location = 'the location'
        event_background = 'the background'

    # Generate dynamic bot instructions
    instructions = f"""
    Bot Objective
    The AI bot is primarily designed to listen and record discussions at the {event_name} in {event_location} with minimal interaction. Its responses are restricted to one or two sentences only, to maintain focus on the participants' discussions.

    Event Background
    {event_background}

    Bot Personality
    The bot is programmed to be non-intrusive and neutral, offering no more than essential interaction required to acknowledge participants' inputs.

    Listening Mode
    Data Retention: The bot is in a passive listening mode, capturing important discussion points without actively participating.
    Minimal Responses: The bot remains largely silent, offering brief acknowledgments if directly addressed.

    Change Session/Event/Name
    If the user would like to change their name or event during the session, the bot will respond with: 'To change your name, type "change name [new name]". To change your event, type "change event [event name]".'

    Interaction Guidelines
    Ultra-Brief Responses: If the bot needs to respond, it will use no more than one to two sentences, strictly adhering to this rule to prevent engaging beyond necessary acknowledgment.
    Acknowledgments: For instance, if a participant makes a point or asks if the bot is recording, it might say, "Acknowledged," or, "Yes, I'm recording."

    Conversation Management
    Directive Responses: On rare occasions where direction is required and appropriate, the bot will use concise prompts like "Please continue," or "Could you clarify?"
    Passive Engagement: The bot uses minimal phrases like "Understood" or "Noted" with professional emojis to confirm its presence and listening status without adding substance to the conversation.

    Closure of Interaction
    Concluding Interaction: When a dialogue concludes or a user ends the interaction, the bot responds succinctly with, "Thank you for the discussion."

    Overall Management
    The bot ensures it does not interfere with or distract from the human-centric discussions at the {event_name} in {event_location}. Its primary role is to support by listening and only acknowledging when absolutely necessary, ensuring that all interactions remain brief and to the point.
    """
    return instructions


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
            'last_inactivity_prompt': None,
            ### NEW OR CHANGED CODE HERE: 
            # Add flags for extra questions
            'awaiting_extra_questions': False,
            'current_extra_question_index': 0 
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

    ### NEW OR CHANGED CODE HERE:
    # Extra questions tracking
    awaiting_extra_questions = user_data.get('awaiting_extra_questions', False)
    current_extra_question_index = user_data.get('current_extra_question_index', 0)
    ### END NEW

    # Remove duplicate events from user_events
    unique_events = {}
    for event in user_events:
        eid = event['event_id']
        if eid not in unique_events:
            unique_events[eid] = event
        else:
            # If duplicate, keep the most recent timestamp
            existing_event_time = datetime.fromisoformat(unique_events[eid]['timestamp'])
            current_event_time = datetime.fromisoformat(event['timestamp'])
            if current_event_time > existing_event_time:
                unique_events[eid] = event  # Update to more recent event
    user_events = list(unique_events.values())
    user_data['events'] = user_events
    user_tracking_ref.update({'events': user_events})

    # Check if current_event_id is still valid
    if current_event_id:
        event_info_ref = db.collection(f'AOI_{current_event_id}').document('info')
        event_info_doc = event_info_ref.get()
        if not event_info_doc.exists:
            # Event is no longer valid
            user_events = [e for e in user_events if e['event_id'] != current_event_id]

            user_tracking_ref.update({
                'current_event_id': None,
                'events': user_events,
                'awaiting_event_id': True
            })
            send_message(From, f"The event '{current_event_id}' is no longer active. Please enter a new event ID to continue.")
            return Response(status_code=200)

    # Step 2: Check for inactivity (every 24 hours)
    current_time = datetime.utcnow()
    user_inactive = False

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
        if last_inactivity_prompt:
            last_prompt_time = datetime.fromisoformat(last_inactivity_prompt)
            time_since_last_prompt = current_time - last_prompt_time
            if time_since_last_prompt < timedelta(hours=24):
                pass
            else:
                event_list = '\n'.join([f"{i+1}. {evt['event_id']}" for i, evt in enumerate(user_events)])
                send_message(From, f"You have been inactive for more than 24 hours.\nYour events:\n{event_list}\nPlease reply with the number of the event you'd like to continue.")
                user_tracking_ref.update({'last_inactivity_prompt': current_time.isoformat()})
                return Response(status_code=200)
        else:
            event_list = '\n'.join([f"{i+1}. {evt['event_id']}" for i, evt in enumerate(user_events)])
            send_message(From, f"You have been inactive for more than 24 hours.\nYour events:\n{event_list}\nPlease reply with the number of the event you'd like to continue.")
            user_tracking_ref.update({'last_inactivity_prompt': current_time.isoformat()})
            return Response(status_code=200)

    # Add 'invalid_attempts' to track invalid responses
    invalid_attempts = user_data.get('invalid_attempts', 0)

    # Step 3: Handle user selection for event continuation
    if last_inactivity_prompt:
        if Body.isdigit() and 1 <= int(Body) <= len(user_events):
            selected_event = user_events[int(Body) - 1]['event_id']
            send_message(From, f"You are now continuing in event {selected_event}.")
            current_event_id = selected_event

            current_time_iso = datetime.utcnow().isoformat()
            for evt in user_events:
                if evt['event_id'] == selected_event:
                    evt['timestamp'] = current_time_iso
                    break

            user_tracking_ref.update({
                'current_event_id': current_event_id,
                'events': user_events,
                'last_inactivity_prompt': None,
                'invalid_attempts': 0
            })
            return Response(status_code=200)
        else:
            invalid_attempts += 1
            if invalid_attempts < 2:
                user_tracking_ref.update({'invalid_attempts': invalid_attempts})
                send_message(From, "Invalid event selection. Please reply with the number corresponding to the event you'd like to continue.")
                return Response(status_code=200)
            else:
                if current_event_id:
                    send_message(From, f"No valid selection made. Continuing with your current event '{current_event_id}'.")
                    current_time_iso = datetime.utcnow().isoformat()
                    for evt in user_events:
                        if evt['event_id'] == current_event_id:
                            evt['timestamp'] = current_time_iso
                            break
                    user_tracking_ref.update({
                        'current_event_id': current_event_id,
                        'events': user_events,
                        'last_inactivity_prompt': None,
                        'invalid_attempts': 0
                    })
                    return Response(status_code=200)
                else:
                    send_message(From, "No valid selection made and no current event found. Please provide your event ID to proceed.")
                    user_tracking_ref.update({
                        'awaiting_event_id': True,
                        'last_inactivity_prompt': None,
                        'invalid_attempts': 0
                    })
                    return Response(status_code=200)

    elif awaiting_event_change_confirmation:
        if Body.strip().lower() in ['yes', 'y']:
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

            event_exists = False
            for evt in user_events:
                if evt['event_id'] == current_event_id:
                    evt['timestamp'] = current_time_iso
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
                'awaiting_region': awaiting_region,
                ### NEW:
                'awaiting_extra_questions': False,
                'current_extra_question_index': 0
            })

            # Initialize or retrieve user doc in the new event
            event_doc_ref = db.collection(f'AOI_{current_event_id}').document(normalized_phone)
            event_doc = event_doc_ref.get()
            if not event_doc.exists:
                event_doc_ref.set({
                    'name': None,
                    'interactions': [],
                    'event_id': current_event_id
                })
            else:
                data = event_doc.to_dict()
                participant_name = data.get('name', None)
                if participant_name:
                    user_tracking_ref.update({'awaiting_name': False})
                    # Proceed to check if other features are needed
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
                        # ### NEW: Check for extra questions
                        extra_questions = event_details.get('extra_questions', {})
                        enabled_questions = [k for k,v in extra_questions.items() if v.get('enabled')]
                        if enabled_questions:
                            user_tracking_ref.update({
                                'awaiting_extra_questions': True,
                                'current_extra_question_index': 0
                            })
                            # Ask the first extra question
                            first_question_key = enabled_questions[0]
                            first_question_text = extra_questions[first_question_key]['text']
                            send_message(From, first_question_text)
                            return Response(status_code=200)
                        else:
                            # if no extra questions, just continue
                            send_message(From, f"You have switched to event {current_event_id}. Please continue.")
                            return Response(status_code=200)

            if awaiting_name:
                send_message(From, f"You have switched to event {current_event_id}. Now, please tell me your name.")
            else:
                send_message(From, f"You have switched to event {current_event_id}.")
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
                    # ### NEW: Check for extra questions
                    extra_questions = event_details.get('extra_questions', {})
                    enabled_questions = [k for k,v in extra_questions.items() if v.get('enabled')]
                    if enabled_questions:
                        user_tracking_ref.update({
                            'awaiting_extra_questions': True,
                            'current_extra_question_index': 0
                        })
                        first_question_key = enabled_questions[0]
                        first_question_text = extra_questions[first_question_key]['text']
                        send_message(From, first_question_text)
                        return Response(status_code=200)
                    else:
                        send_message(From, "You can now continue with the conversation.")
            return Response(status_code=200)

        else:
            user_tracking_ref.update({
                'awaiting_event_change_confirmation': False,
                'new_event_id_pending': None
            })
            send_message(From, f"Event change cancelled. You remain in event {current_event_id}. Please continue.")
            return Response(status_code=200)

    elif awaiting_event_id:
        # User is expected to provide event ID
        extracted_event_id = extract_event_id_with_llm(Body)
        if extracted_event_id and event_id_valid(extracted_event_id):
            event_id = extracted_event_id
            current_event_id = event_id
            current_time_iso = datetime.utcnow().isoformat()

            event_exists = False
            for evt in user_events:
                if evt['event_id'] == event_id:
                    evt['timestamp'] = current_time_iso
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
                'awaiting_region': awaiting_region,
                ### new:
                'awaiting_extra_questions': False,
                'current_extra_question_index': 0
            })

            event_doc_ref = db.collection(f'AOI_{event_id}').document(normalized_phone)
            event_doc_ref.set({'name': None, 'interactions': [], 'event_id': event_id})

            if awaiting_name:
                default_initial_message = """Thank you for agreeing to participate... (Your initial message)"""
                event_info_ref = db.collection(f'AOI_{current_event_id}').document('info')
                event_info_doc = event_info_ref.get()
                if event_info_doc.exists:
                    event_info = event_info_doc.to_dict()
                    initial_message = event_info.get('initial_message', default_initial_message)
                else:
                    initial_message = default_initial_message

                send_message(From, initial_message)
            else:
                default_initial_message = """Thank you for agreeing to participate... (Your initial message)"""
                event_info_ref = db.collection(f'AOI_{current_event_id}').document('info')
                event_info_doc = event_info_ref.get()
                if event_info_doc.exists:
                    event_info = event_info_doc.to_dict()
                    initial_message = event_info.get('initial_message', default_initial_message)
                else:
                    initial_message = default_initial_message

                send_message(From, initial_message)
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
                    # ### NEW: Check for extra questions
                    extra_questions = event_info.get('extra_questions', {})
                    enabled_questions = [k for k,v in extra_questions.items() if v.get('enabled')]
                    if enabled_questions:
                        user_tracking_ref.update({
                            'awaiting_extra_questions': True,
                            'current_extra_question_index': 0
                        })
                        first_question_key = enabled_questions[0]
                        first_question_text = extra_questions[first_question_key]['text']
                        send_message(From, first_question_text)
                        return Response(status_code=200)
                    else:
                        send_message(From, "You can now start the conversation.")
            return Response(status_code=200)
        else:
            logger.info(f"Invalid event ID: {Body}")
            send_message(From, "The event ID you provided is invalid. Please re-enter the correct event ID or contact support.")
            return Response(status_code=200)

    elif (awaiting_name or awaiting_age or awaiting_gender or awaiting_region or awaiting_extra_questions):
        # We are awaiting some data from user

        # Fetch participant data from event doc
        event_doc_ref = db.collection(f'AOI_{current_event_id}').document(normalized_phone)
        event_doc = event_doc_ref.get()
        participant_data = event_doc.to_dict() if event_doc.exists else {}

        # Possibly handle media (audio) -> transcribe
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

        # Fetch event info to get extra questions if needed
        event_details_ref = db.collection(f'AOI_{current_event_id}').document('info')
        event_details_doc = event_details_ref.get()
        if event_details_doc.exists:
            event_details = event_details_doc.to_dict()
            extraction_settings = event_details.get('extraction_settings', {})
            extra_questions = event_details.get('extra_questions', {})
        else:
            extraction_settings = {}
            extra_questions = {}

        name_extraction_enabled = extraction_settings.get('name_extraction', True)
        age_extraction_enabled = extraction_settings.get('age_extraction', False)
        gender_extraction_enabled = extraction_settings.get('gender_extraction', False)
        region_extraction_enabled = extraction_settings.get('region_extraction', False)

        # -------------- NAME --------------
        if awaiting_name:
            extracted_name = extract_name_with_llm(Body, current_event_id)
            if extracted_name and extracted_name.lower() == "anonymous":
                event_doc_ref.update({'name': "Anonymous"})
                participant_data['name'] = "Anonymous"
            elif extracted_name:
                extracted_name = extracted_name.strip().strip('"').strip("'")
                if not is_valid_name(extracted_name):
                    event_doc_ref.update({'name': None})
                    participant_data['name'] = None
                else:
                    event_doc_ref.update({'name': extracted_name})
                    participant_data['name'] = extracted_name
            else:
                event_doc_ref.update({'name': None})
                participant_data['name'] = None

            user_tracking_ref.update({'awaiting_name': False})

            # Next checks
            if age_extraction_enabled:
                user_tracking_ref.update({'awaiting_age': True})
                prompt_message = generate_age_prompt_with_llm(participant_data, current_event_id)
                send_message(From, prompt_message)
                return Response(status_code=200)
            elif gender_extraction_enabled:
                user_tracking_ref.update({'awaiting_gender': True})
                prompt_message = generate_gender_prompt_with_llm(participant_data, current_event_id)
                send_message(From, prompt_message)
                return Response(status_code=200)
            elif region_extraction_enabled:
                user_tracking_ref.update({'awaiting_region': True})
                prompt_message = generate_region_prompt_with_llm(participant_data, current_event_id)
                send_message(From, prompt_message)
                return Response(status_code=200)
            else:
                # ### NEW: check for extra questions
                enabled_questions = [k for k,v in extra_questions.items() if v.get('enabled')]
                if enabled_questions:
                    user_tracking_ref.update({
                        'awaiting_extra_questions': True,
                        'current_extra_question_index': 0
                    })
                    first_key = enabled_questions[0]
                    first_text = extra_questions[first_key]['text']
                    send_message(From, first_text)
                    return Response(status_code=200)
                else:
                    # no extra questions
                    welcome_msg = create_welcome_message(current_event_id, participant_name=participant_data['name'])
                    send_message(From, welcome_msg)
                return Response(status_code=200)

        # -------------- AGE --------------
        elif awaiting_age:
            extracted_age = extract_age_with_llm(Body, current_event_id)
            if extracted_age == "No age found":
                event_doc_ref.update({'age': None})
            else:
                event_doc_ref.update({'age': extracted_age})
            user_tracking_ref.update({'awaiting_age': False})

            if gender_extraction_enabled:
                user_tracking_ref.update({'awaiting_gender': True})
                prompt_message = generate_gender_prompt_with_llm(participant_data, current_event_id)
                send_message(From, prompt_message)
                return Response(status_code=200)
            elif region_extraction_enabled:
                user_tracking_ref.update({'awaiting_region': True})
                prompt_message = generate_region_prompt_with_llm(participant_data, current_event_id)
                send_message(From, prompt_message)
                return Response(status_code=200)
            else:
                # ### NEW: check for extra questions
                enabled_questions = [k for k,v in extra_questions.items() if v.get('enabled')]
                if enabled_questions:
                    user_tracking_ref.update({
                        'awaiting_extra_questions': True,
                        'current_extra_question_index': 0
                    })
                    first_key = enabled_questions[0]
                    first_text = extra_questions[first_key]['text']
                    send_message(From, first_text)
                    return Response(status_code=200)
                else:
                    participant_name = participant_data.get('name', None)
                    welcome_msg = create_welcome_message(current_event_id, participant_name=participant_name)
                    send_message(From, welcome_msg)
            return Response(status_code=200)

        # -------------- GENDER --------------
        elif awaiting_gender:
            extracted_gender = extract_gender_with_llm(Body, current_event_id)
            if extracted_gender == "No gender found":
                event_doc_ref.update({'gender': None})
            else:
                event_doc_ref.update({'gender': extracted_gender})
            user_tracking_ref.update({'awaiting_gender': False})

            if region_extraction_enabled:
                user_tracking_ref.update({'awaiting_region': True})
                prompt_message = generate_region_prompt_with_llm(participant_data, current_event_id)
                send_message(From, prompt_message)
                return Response(status_code=200)
            else:
                # ### NEW: check for extra questions
                enabled_questions = [k for k,v in extra_questions.items() if v.get('enabled')]
                if enabled_questions:
                    user_tracking_ref.update({
                        'awaiting_extra_questions': True,
                        'current_extra_question_index': 0
                    })
                    first_key = enabled_questions[0]
                    first_text = extra_questions[first_key]['text']
                    send_message(From, first_text)
                    return Response(status_code=200)
                else:
                    participant_name = participant_data.get('name', None)
                    welcome_msg = create_welcome_message(current_event_id, participant_name=participant_name)
                    send_message(From, welcome_msg)
            return Response(status_code=200)

        # -------------- REGION --------------
        elif awaiting_region:
            extracted_region = extract_region_with_llm(Body, current_event_id)
            if extracted_region == "No region found":
                event_doc_ref.update({'region': None})
            else:
                event_doc_ref.update({'region': extracted_region})
            user_tracking_ref.update({'awaiting_region': False})

            # ### NEW: check for extra questions
            enabled_questions = [k for k,v in extra_questions.items() if v.get('enabled')]
            if enabled_questions:
                user_tracking_ref.update({
                    'awaiting_extra_questions': True,
                    'current_extra_question_index': 0
                })
                first_key = enabled_questions[0]
                first_text = extra_questions[first_key]['text']
                send_message(From, first_text)
                return Response(status_code=200)
            else:
                participant_name = participant_data.get('name', None)
                welcome_msg = create_welcome_message(current_event_id, participant_name=participant_name)
                send_message(From, welcome_msg)
            return Response(status_code=200)

        # -------------- EXTRA QUESTIONS --------------
        elif awaiting_extra_questions:
            # We are in the process of collecting extra question responses
            enabled_questions = [k for k,v in extra_questions.items() if v.get('enabled')]

            # if current_extra_question_index < len(enabled_questions):
            #     # Store user's response for the last asked question
            #     question_key = enabled_questions[current_extra_question_index]
            #     # create or update a nested dict for answers
            #     existing_extra_answers = participant_data.get('extra_answers', {})
            #     existing_extra_answers[question_key] = Body  # or store the transcribed audio as text
            #     event_doc_ref.update({'extra_answers': existing_extra_answers})

            #     # Move to next question
            #     current_extra_question_index += 1
            #     user_tracking_ref.update({'current_extra_question_index': current_extra_question_index})

            #     if current_extra_question_index < len(enabled_questions):
            #         # Ask next question
            #         next_question_key = enabled_questions[current_extra_question_index]
            #         next_question_text = extra_questions[next_question_key]['text']
            #         send_message(From, next_question_text)
            #     else:
            #         # no more extra questions
            #         user_tracking_ref.update({'awaiting_extra_questions': False})
            #         participant_name = participant_data.get('name', None)
            #         welcome_msg = create_welcome_message(current_event_id, participant_name=participant_name)
            #         send_message(From, welcome_msg)

            # return Response(status_code=200)

            if current_extra_question_index < len(enabled_questions):
                question_key = enabled_questions[current_extra_question_index]
                
                # Instead of putting everything in 'extra_answers',
                # directly update the document with the question key as a top-level field:
                event_doc_ref.update({
                    question_key: Body
                })
                
                current_extra_question_index += 1
                user_tracking_ref.update({'current_extra_question_index': current_extra_question_index})
                
                if current_extra_question_index < len(enabled_questions):
                    next_question_key = enabled_questions[current_extra_question_index]
                    next_question_text = extra_questions[next_question_key]['text']
                    send_message(From, next_question_text)
                else:
                    user_tracking_ref.update({'awaiting_extra_questions': False})
                    participant_name = participant_data.get('name', None)
                    welcome_msg = create_welcome_message(current_event_id, participant_name=participant_name)
                    send_message(From, welcome_msg)
        return Response(status_code=200)

    elif not current_event_id:
        # If user has no current event, attempt to extract event ID from Body
        extracted_event_id = extract_event_id_with_llm(Body)
        if extracted_event_id and event_id_valid(extracted_event_id):
            event_id = extracted_event_id
            current_event_id = event_id
            current_time_iso = datetime.utcnow().isoformat()

            event_exists = False
            for evt in user_events:
                if evt['event_id'] == event_id:
                    evt['timestamp'] = current_time_iso
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
                'awaiting_region': awaiting_region,
                ### new:
                'awaiting_extra_questions': False,
                'current_extra_question_index': 0
            })

            event_doc_ref = db.collection(f'AOI_{event_id}').document(normalized_phone)
            event_doc_ref.set({'name': None, 'interactions': [], 'event_id': event_id})

            if awaiting_name:
                default_initial_message = """Thank you for agreeing to participate... (Your initial message)"""
                event_info_ref = db.collection(f'AOI_{current_event_id}').document('info')
                event_info_doc = event_info_ref.get()
                if event_info_doc.exists:
                    event_info = event_info_doc.to_dict()
                    initial_message = event_info.get('initial_message', default_initial_message)
                else:
                    initial_message = default_initial_message

                send_message(From, initial_message)
            else:
                default_initial_message = """Thank you for agreeing to participate... (Your initial message)"""
                event_info_ref = db.collection(f'AOI_{current_event_id}').document('info')
                event_info_doc = event_info_ref.get()
                if event_info_doc.exists:
                    event_info = event_info_doc.to_dict()
                    initial_message = event_info.get('initial_message', default_initial_message)
                else:
                    initial_message = default_initial_message

                send_message(From, initial_message)
                # Next, handle age/gender/region or extra questions
                if age_extraction_enabled:
                    user_tracking_ref.update({'awaiting_age': True})
                    send_message(From, "Please tell me your age.")
                    return Response(status_code=200)
                elif gender_extraction_enabled:
                    user_tracking_ref.update({'awaiting_gender': True})
                    send_message(From, "Please tell me your gender.")
                    return Response(status_code=200)
                elif region_extraction_enabled:
                    user_tracking_ref.update({'awaiting_region': True})
                    send_message(From, "Please tell me your region.")
                    return Response(status_code=200)
                else:
                    # ### NEW: check for extra questions
                    extra_questions = event_info.get('extra_questions', {})
                    enabled_questions = [k for k,v in extra_questions.items() if v.get('enabled')]
                    if enabled_questions:
                        user_tracking_ref.update({
                            'awaiting_extra_questions': True,
                            'current_extra_question_index': 0
                        })
                        first_key = enabled_questions[0]
                        first_text = extra_questions[first_key]['text']
                        send_message(From, first_text)
                        return Response(status_code=200)
                    else:
                        send_message(From, "You can now start the conversation.")

            return Response(status_code=200)
        else:
            send_message(From, "Welcome! Please provide your event ID to proceed.")
            user_tracking_ref.update({'awaiting_event_id': True})
            return Response(status_code=200)

    # Handle "change name" command
    if Body.lower().startswith("change name "):
        new_name = Body[12:].strip()
        if new_name:
            event_doc_ref = db.collection(f'AOI_{current_event_id}').document(normalized_phone)
            event_doc_ref.update({'name': new_name})
            send_message(From, f"Your name has been updated to {new_name}. Please continue.")
        else:
            send_message(From, "It seems there was an error updating your name. Please try again.")
        return Response(status_code=200)

    # Handle "change event" command
    elif Body.lower().startswith("change event "):
        new_event_id = Body[13:].strip()
        if event_id_valid(new_event_id):
            if new_event_id == current_event_id:
                send_message(From, f"You are already in event {new_event_id}.")
                return Response(status_code=200)
            send_message(From, f"You requested to change to event {new_event_id}. Please confirm by replying 'yes' or cancel with 'no'.")
            user_tracking_ref.update({
                'awaiting_event_change_confirmation': True,
                'new_event_id_pending': new_event_id
            })
        else:
            send_message(From, f"The event ID '{new_event_id}' is invalid. Please check and try again.")
        return Response(status_code=200)

    # If user types 'finalize' or 'finish'
    if Body.strip().lower() in ['finalize', 'finish']:
        default_completion_message = """Congratulations, you’ve completing this! Thank you so much for taking the time..."""
        event_info_ref = db.collection(f'AOI_{current_event_id}').document('info')
        event_info_doc = event_info_ref.get()
        if event_info_doc.exists:
            event_info = event_info_doc.to_dict()
            completion_message = event_info.get('completion_message', default_completion_message)
        else:
            completion_message = default_completion_message

        send_message(From, completion_message)
        return Response(status_code=200)

    # Otherwise, proceed with the normal conversation
    event_details_ref = db.collection(f'AOI_{current_event_id}').document('info')
    event_details_doc = event_details_ref.get()
    event_name = "the event"
    event_location = ""
    welcome_message = "Welcome! You can now start sending text and audio messages."
    if event_details_doc.exists:
        event_details = event_details_doc.to_dict()
        event_name = event_details.get('event_name', event_name)
        event_location = event_details.get('event_location', event_location)
        welcome_message = event_details.get('welcome_message', welcome_message)

    event_instructions = generate_bot_instructions(current_event_id)

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

    # Store user message
    event_doc_ref = db.collection(f'AOI_{current_event_id}').document(normalized_phone)
    event_doc = event_doc_ref.get()
    if not event_doc.exists:
        event_doc_ref.set({'interactions': [], 'name': None, 'limit_reached_notified': False})

    data = event_doc.to_dict()
    interactions = data.get('interactions', [])
    if len(interactions) >= 450:
        send_message(From, "You have reached your interaction limit with AOI. Please contact AOI for further assistance.")
        return Response(status_code=200)

    # Send user prompt to an OpenAI function or your LLM
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
