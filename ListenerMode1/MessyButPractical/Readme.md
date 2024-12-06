
# WhatsApp Listener Mode Agent

## Table of Contents
1. [Introduction](#introduction)
2. [Key Features](#key-features)
3. [System Architecture](#system-architecture)
4. [Data Flow and Interaction](#data-flow-and-interaction)
5. [Technology Stack](#technology-stack)
6. [Prerequisites and Environment Setup](#prerequisites-and-environment-setup)
7. [Configuration and Environment Variables](#configuration-and-environment-variables)
8. [Project Structure](#project-structure)
9. [Database Schema and Firestore Collections](#database-schema-and-firestore-collections)
10. [Logic and Handling User States](#logic-and-handling-user-states)
11. [Event and Participant Onboarding Flow](#event-and-participant-onboarding-flow)
12. [Audio Handling and Speech-to-Text Integration](#audio-handling-and-speech-to-text-integration)
13. [LLM (OpenAI) Integration](#llm-openai-integration)
14. [Twilio WhatsApp Integration](#twilio-whatsapp-integration)
15. [Deployment on Heroku](#deployment-on-heroku)
16. [Logging and Error Handling](#logging-and-error-handling)
17. [Scaling and Optimization Strategies](#scaling-and-optimization-strategies)
18. [Testing](#testing)
19. [Security Considerations](#security-considerations)

---

## Introduction

This repository hosts a WhatsApp listener-mode agent designed to passively record discussions and participant feedback during events, while providing minimal interactive responses. The bot acknowledges users, prompts them for necessary metadata (e.g., name, age, gender, region) if configured, and logs all user interactions to a Firestore database. The entire logic centers around a passive listening mode where the bot's primary purpose is to capture user inputs (text and voice messages), optionally transcribe audio, and store all data securely.

The agent leverages:
- **Twilio WhatsApp API** for inbound and outbound message handling.
- **OpenAI GPT-4 APIs** for natural language processing, extracting user details, and generating minimal responses.
- **Firebase Firestore** as a robust NoSQL backend for event/participant data management.
- **FastAPI** for a lightweight and efficient server.
- **Heroku** for seamless cloud deployment and scaling.

---

## Key Features

1. **Passive Listening Mode**: 
   The agent listens to participant inputs at defined events and records the content without actively engaging beyond minimal acknowledgments.

2. **Dynamic Event Configuration**:
   - Supports multiple event IDs.
   - Retrieves event-specific instructions, welcome messages, and extraction settings (name, age, gender, region) from Firestore.
   - Allows changing events mid-conversation.

3. **Participant Onboarding**:
   - Prompting for event IDs if not provided.
   - Asking participant’s name (or accepting anonymity).
   - Optionally extracting age, gender, and region depending on event configuration.

4. **LLM Integration**:
   - Uses OpenAI models for name extraction, event ID validation, and other user attribute extraction.
   - Handles minimal responses and instructions generation via GPT-4.

5. **Audio Transcription**:
   - Accepts audio messages from WhatsApp.
   - Uses OpenAI Whisper model for speech-to-text.

6. **Inactivity Handling**:
   - Identifies user inactivity over 24 hours.
   - Prompts user to select an event to continue with, if multiple events are associated.

7. **Scalability and Logging**:
   - Centralized logging with structured messages.
   - Deployable on Heroku with horizontally scalable dynos.
   
---

## System Architecture

The system integrates multiple external services and a serverless database:
- **WhatsApp/Twilio**: Entry point for user messages. Incoming messages trigger the FastAPI endpoint, which processes and responds via Twilio.
- **OpenAI GPT-4 & Whisper**: Provides natural language understanding, user attribute extraction, and minimalistic prompting.
- **Firebase Firestore**: Stores event configurations, participant states, and interaction logs.
- **Heroku**: Hosts the FastAPI application, scaling it behind a load balancer.

Flow Overview:
1. User sends a WhatsApp message to the Twilio WhatsApp number.
2. Twilio sends a POST request to the deployed FastAPI endpoint.
3. FastAPI processes the message, checks the user’s state in Firestore, and updates or prompts for missing info.
4. If needed, queries OpenAI’s API for extraction tasks (e.g., name, age) or minimal responses.
5. Sends back a short response via Twilio to the user’s WhatsApp, or just silently logs the conversation.
6. Stores all interactions and metadata in Firestore.

---

## Data Flow and Interaction

1. **Initial Contact**:
   - If no event is set, the user is prompted for an event ID.
   - If provided, the system validates the event and, if needed, asks for participant details (name, etc.).

2. **User Profiling**:
   - The system can extract name, age, gender, region using LLM prompts.
   - The extracted data is stored in Firestore.

3. **Message Handling**:
   - Text messages are directly logged.
   - Audio messages are downloaded, transcribed, and logged.
   - The bot responds minimally, guided by event-specific instructions (one to two sentences at most).

4. **Inactivity and Re-engagement**:
   - After 24 hours of inactivity, the system prompts the user to pick an event or continue with the current event.
   - If user tries invalid inputs thrice, defaults to the current event or re-prompts for event ID.

---

## Technology Stack

- **Programming Language**: Python 3.9+ 
- **Framework**: FastAPI
- **Database**: Firebase Firestore 
- **NLP/LLM**: OpenAI GPT-4 for text-based operations and Whisper API for audio transcription
- **Messaging**: Twilio WhatsApp API
- **Deployment**: Heroku

---

## Prerequisites and Environment Setup

1. **Python & Dependencies**:
   - Python 3.9+ recommended.
   - Install dependencies:
     ```bash
     pip install -r requirements.txt
     ```

2. **Firebase Setup**:
   - Create a Firebase project and Firestore database.
   - Obtain `serviceAccountKey.json` credentials.
   - Ensure Firestore rules allow appropriate reads/writes.

3. **OpenAI API**:
   - Sign up for OpenAI API access.
   - Obtain `OPENAI_API_KEY`.

4. **Twilio Setup**:
   - Create a Twilio account, add WhatsApp Sandbox or a dedicated WhatsApp number.
   - Get `TWILIO_ACCOUNT_SID` and `TWILIO_AUTH_TOKEN`.

5. **Heroku CLI**:
   - Install Heroku CLI if deploying to Heroku.
   - `heroku login` to manage deployment.

---

## Configuration and Environment Variables

Environment variables (using `decouple` or `.env`):
- `OPENAI_API_KEY`: OpenAI API Key.
- `TWILIO_ACCOUNT_SID`: Twilio Account SID.
- `TWILIO_AUTH_TOKEN`: Twilio Auth Token.
- `FIREBASE_CREDENTIALS`: Path to your Firebase service account JSON or the credentials loaded as environment config.
- `TWILIO_NUMBER`: The Twilio WhatsApp sender number.
- Additional keys as defined in `config1.py` and `decouple.config`.

Example `.env`:
```env
OPENAI_API_KEY=sk-********
TWILIO_ACCOUNT_SID=AC************
TWILIO_AUTH_TOKEN=***************
TWILIO_NUMBER=+14155238886
FIREBASE_CREDENTIALS=serviceAccountKey.json
```

---

## Project Structure

```
.
├─ config1.py                          # Configuration module for Firebase, Twilio, OpenAI clients
├─ agent_functions2.py                 # Core functions (prompt generation, extraction, sending messages)
├─ main.py                             # Primary FastAPI application endpoint (given code merged here)
├─ requirements.txt                    # Python dependencies
├─ Procfile                            # Heroku process file
├─ runtime.txt                         # Python runtime version for Heroku
└─ README.md                           # This README file
```

**Key Files**:

- **main.py**: 
  Contains the `/message/` FastAPI endpoint that Twilio hits. Implements all logic for handling user messages, updating states, event switching, participant attribute extraction, etc.

- **config1.py**: 
  Instantiates and configures the Firebase Admin SDK, Twilio client, and OpenAI client. Also sets up logging and global variables.

- **agent_functions2.py**:
  Helper functions for sending messages, generating prompts, extracting user details from LLM responses, and applying conversation logic.

---

## Database Schema and Firestore Collections

This solution uses Firestore with a flexible schema:

1. **`user_event_tracking` Collection**:
   - Documents keyed by user’s normalized phone number.
   - Fields: `events`, `current_event_id`, `awaiting_*` flags, `last_inactivity_prompt`, `invalid_attempts`.

2. **Per-Event Collections (e.g., `AOI_<event_id>`)**:
   - **`info` Document**: Contains `event_name`, `event_location`, `welcome_message`, `completion_message`, `extraction_settings` (flags for name, age, gender, region).
   - **`<phone_number>` Documents**: Stores individual participant data: `name`, `age`, `gender`, `region`, `interactions` array for message logs.

This structure allows event-specific configurations and user-specific states within each event.

---

## Logic and Handling User States

**State Management**:
- The code maintains boolean flags like `awaiting_event_id`, `awaiting_name`, `awaiting_age`, etc.
- On receiving messages, the logic checks the state flags and decides how to respond.
- `current_event_id` determines the active event context.

**State Transitions**:
- Once the user provides their event ID, the system sets `current_event_id`.
- If name extraction is required, `awaiting_name = True` until the participant provides a valid name or opts for anonymity.
- After collecting all required attributes, the system sets `awaiting_*` flags to `False` and the conversation continues normally.

---

## Event and Participant Onboarding Flow

1. **No Event Set**:
   - User is prompted for event ID.
   - On valid event ID, event document created/updated in Firestore.

2. **Name Extraction (If Enabled)**:
   - System prompts for participant’s name.
   - Extracts name from response, handles "Anonymous".

3. **Optional Age/Gender/Region Extraction**:
   - If configured, after name extraction, sequentially asks for age, then gender, then region.

4. **Welcome to the Conversation**:
   - After data collection, sends a personalized welcome message.

---

## Audio Handling and Speech-to-Text Integration

- If the message contains a media URL pointing to an audio file:
  - The system downloads the audio.
  - Calls OpenAI Whisper to transcribe the audio into text.
  - The transcribed text is treated as the user’s message content.
- Non-audio media (e.g., images) is currently not supported.

---

## LLM (OpenAI) Integration

- **GPT-4**: 
  Used for name extraction, event ID extraction, and generating minimal responses.
- **Prompt Engineering**: 
  System messages define the role of the assistant (passive listener), guidelines for minimal responses, and instructions for user attribute extraction.

- **Whisper (Speech-to-Text)**:
  Uses the `audio.transcriptions.create` method to get transcribed text from the user's audio inputs.

---

## Twilio WhatsApp Integration

- Inbound messages from WhatsApp come as POST requests from Twilio.
- The `/message/` FastAPI endpoint receives Twilio form data (`Body`, `From`, `MediaUrl0`, etc.).
- Sends responses via Twilio’s API using the `twilio_client.messages.create()` call.

**Twilio Sandbox**:
- For testing, you can use Twilio’s WhatsApp sandbox.
- On production, use your approved WhatsApp Business number.

---

## Deployment on Heroku

1. **Procfile**:
   - Ensure the `Procfile` is configured to run `uvicorn main:app --host=0.0.0.0 --port=$PORT`.

2. **Runtime**:
   - `runtime.txt` specifies the Python runtime.

3. **Deployment Steps**:
   ```bash
   heroku create
   heroku config:set OPENAI_API_KEY=xxx TWILIO_ACCOUNT_SID=xxx TWILIO_AUTH_TOKEN=xxx ...
   git push heroku main
   ```
   
4. **Scaling**:
   - Use `heroku ps:scale web=1` or more as needed.

---

## Logging and Error Handling

- Uses Python's `logging` library.
- Logs key actions: message reception, error conditions, and LLM requests.
- In case of exceptions, logs are recorded, and minimal fallback responses are provided to the user.

---

## Scaling and Optimization Strategies

- **Concurrency**:
  FastAPI and Uvicorn workers can handle concurrent requests.
  
- **Load Balancing**:
  Heroku automatically load-balances across scaled dynos.

- **Caching**:
  - Potential caching for event metadata retrieval to reduce Firestore reads.
  - Consider in-memory caching or a Redis layer if traffic grows large.

- **Rate Limits**:
  - Twilio or OpenAI may have rate limits. Implement backoff strategies or caching results.
  
---

## Testing

- **Unit Tests**:
  - Add tests for extraction functions (e.g., name extraction, event ID validation).
  - Mock Twilio and OpenAI responses.

- **Integration Tests**:
  - Test the whole flow from inbound WhatsApp message to Firestore storage.
  - Use test Firestore instances and Twilio test credentials.

---

## Security Considerations

- **Authentication**:
  - Twilio requests are verified using `twilio.request_validator`. Consider validating inbound requests.
  
- **Secrets Management**:
  - Store all keys (OpenAI, Twilio, Firebase) in environment variables or a secure secret manager.
  
- **Firebase Rules**:
  - Properly configure Firestore security rules to prevent unauthorized access.

- **Data Privacy**:
  - The system may handle sensitive user inputs. Comply with applicable data protection regulations.
  - Store minimum PII and follow anonymization strategies when possible.

---


**More To Come**