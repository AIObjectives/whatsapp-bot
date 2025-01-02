# Firestore-Integrated WhatsApp Elicitation Bot

A FastAPI-based chatbot that integrates with Firestore, Twilio WhatsApp, and OpenAI (LLM) to facilitate conversational data collection and event-based user management. This solution lets you:

- **Configure and track participants** in specific events.  
- **Gather user details** (name, age, gender, region) through dynamic LLM prompts.  
- **Provide engaging conversations** with OpenAI’s language model.  
- **Store interactions** in Firestore for auditing and analysis.  

---

## Table of Contents

1. [Overview](#overview)  
2. [Features](#features)  
3. [Requirements](#requirements)  
4. [Setup & Installation](#setup--installation)  
   1. [Environment Variables](#environment-variables)  
   2. [Firebase Configuration](#firebase-configuration)  
   3. [Twilio Configuration](#twilio-configuration)  
   4. [OpenAI Configuration](#openai-configuration)  
5. [Project Structure](#project-structure)  
6. [Usage](#usage)  
   1. [Running the FastAPI App](#running-the-fastapi-app)  
   2. [Workflow & Conversation Steps](#workflow--conversation-steps)  
   3. [Event & User Management in Firestore](#event--user-management-in-firestore)  
7. [How It Works](#how-it-works)  
   1. [Event-Based Approach](#event-based-approach)  
   2. [Extraction Logic](#extraction-logic)  
   3. [Dynamic Prompts](#dynamic-prompts)  
8. [Customization](#customization)  
9. [Troubleshooting](#troubleshooting)  
10. [Contributing](#contributing)  
11. [License](#license)  

---

## 1. Overview

This project provides a **WhatsApp chatbot** that manages participants and collects survey-style data for various **events** using **Firestore** (Firebase) as the database. It uses **OpenAI** to generate dynamic responses and prompts, and **Twilio** for WhatsApp messaging.

Use cases include:

- Running targeted surveys or consultations.
- Gathering demographic or contextual information from participants (e.g., name, age, gender, region).
- Holding ongoing conversations with participants for deeper elicitation of opinions and feedback.

---

## 2. Features

- **FastAPI** as the main web framework (exposes `/message/` endpoint to receive WhatsApp messages via Twilio Webhooks).  
- **Firestore** integration for storing:
  - User documents in `user_event_tracking`  
  - Event-specific collections like `AOI_<event_id>`  
- **Twilio WhatsApp** integration to send/receive WhatsApp messages.  
- **OpenAI** (LLM) for:
  - Extracting event IDs, user names, ages, genders, regions.  
  - Generating conversation flows, including follow-up questions.  
- **Event-based logic**: Each user can join multiple events, switch events, or change names.  
- **Voice/Audio transcription**: Audio messages can be transcribed using OpenAI (Whisper).  
- **Inactivity Check**: Prompts users to resume if inactive for more than 24 hours.  

---

## 3. Requirements

- **Python 3.8+**  
- A **Firebase** project with a service account JSON key.  
- A **Twilio** account with a WhatsApp sandbox or sender number.  
- An **OpenAI** account with access to GPT-4 (or your chosen model).  

---

## 4. Setup & Installation

Clone the repository and install dependencies:

```bash
git clone https://github.com/yourname/yourrepo.git
cd yourrepo
pip install -r requirements.txt
```

### 4.1 Environment Variables

Use something like [python-decouple](https://pypi.org/project/python-decouple/) or `.env` file to store secrets. This project references variables such as:

- `OPENAI_API_KEY`  
- `TWILIO_ACCOUNT_SID`  
- `TWILIO_AUTH_TOKEN`  
- `TWILIO_NUMBER` (WhatsApp-enabled phone number)  

A sample `.env` file might include:
```
OPENAI_API_KEY=sk-...
TWILIO_ACCOUNT_SID=AC...
TWILIO_AUTH_TOKEN=...
TWILIO_NUMBER=+1234567890
```

### 4.2 Firebase Configuration

- Download your Firebase **service account key** (JSON).  
- Update the path in the script where the code initializes Firebase:

  ```python
  if not firebase_admin._apps:
      cred = credentials.Certificate('/path/to/your_service_account.json')
      firebase_admin.initialize_app(cred)
  ```

- Verify you have a **Firestore** database set up in your Firebase project.

### 4.3 Twilio Configuration

- Set up a **WhatsApp Sandbox** (or apply for a full WhatsApp sender number).  
- Paste the **Webhook URL** (e.g., `https://<your-domain>/message/`) into Twilio’s Console for incoming WhatsApp messages.

### 4.4 OpenAI Configuration

- In your `.env`, set `OPENAI_API_KEY`.  
- By default, the code uses `gpt-4o`, but you can adjust to another model name in relevant places (e.g., `model="gpt-4o"`).

---

## 5. Project Structure

A simplified layout:

```
yourrepo/
├── main.py                        # Main FastAPI application code
├── agent_functions3_dry.py        # Core helper functions for LLM extraction, prompts, etc.
├── config1.py                     # Configuration references (Firebase, Twilio, OpenAI, etc.)
├── requirements.txt
├── .env
└── README.md
```

- **`main.py`**:  
  - Implements `/message/` endpoint (FastAPI).  
  - Handles user state logic (event assignment, awaiting flags, etc.).  
  - Integrates Twilio for sending responses.  
  - Calls LLM extractors.  

- **`agent_functions3_dry.py`**:  
  - Contains specialized functions for name, age, gender, region extraction.  
  - Generates dynamic LLM prompts (e.g., follow-up or welcome messages).  
  - `send_message` function for Twilio.  

- **`config1.py`**:  
  - Central place for environment/config variables (Firebase, Twilio, OpenAI).  
  - In your actual code, these might be spread or imported as needed.  

---

## 6. Usage

### 6.1 Running the FastAPI App

1. **Start the server**:
   ```bash
   uvicorn main:app --host 0.0.0.0 --port 8000
   ```
2. **Expose** your local server to the internet (for Twilio to send webhooks). One option is using [ngrok](https://ngrok.com/):
   ```bash
   ngrok http 8000
   ```
3. **Configure Twilio**:
   - In your Twilio Console, set the **Webhook URL** of your WhatsApp sandbox to the public URL from `ngrok` (e.g., `https://xxxx.ngrok.io/message/`).

### 6.2 Workflow & Conversation Steps

1. **User sends a WhatsApp message** to your Twilio number.  
2. **Twilio** forwards the request as a webhook to `/message/`.  
3. **FastAPI**:
   - Normalizes the phone number.  
   - Checks `user_event_tracking` to determine if the user is in an event or if they need to be assigned one.  
   - If needed, asks user for an event ID.  
   - If the event requires name/age/gender/region, it prompts the user.  
   - Passes user’s message to **OpenAI** for generating a relevant response or continuing the conversation.  
4. **Response** is stored in Firestore, and the user sees the bot’s message on WhatsApp.

### 6.3 Event & User Management in Firestore

- **`user_event_tracking`**:
  - Document ID = normalized phone number.  
  - Fields:  
    - `events` (array of { event_id, timestamp }),  
    - `current_event_id`,  
    - `awaiting_name`, `awaiting_age`, `awaiting_gender`, `awaiting_region`, etc.  

- **`AOI_<event_id>`**:
  - `info` document: Contains event metadata, toggles, questions, etc.  
  - Individual user documents: Contains interactions (messages) and extracted details.  

---

## 7. How It Works

### 7.1 Event-Based Approach

- Each user can be involved in **multiple events**. A user’s `current_event_id` indicates which event they’re actively interacting with.  
- If a user tries to “change event” mid-conversation, the bot prompts for confirmation, then switches context.

### 7.2 Extraction Logic

LLM-based extraction functions:
- **`extract_event_id_with_llm`**: Attempts to parse user text for a valid event ID in Firestore (`AOI_<eventID>`).  
- **`extract_name_with_llm`**: Looks for a user name or “anonymous” mention.  
- **`extract_age_with_llm`, `extract_gender_with_llm`, `extract_region_with_llm`**: Identify respective info from user input.  

All are **dry** or stateless calls, giving the bot a flexible, conversation-driven approach.

### 7.3 Dynamic Prompts

- The system uses **generate_*_prompt_with_llm** functions to craft various, unique prompts.  
- This ensures the bot’s instructions to the user feel natural and less repetitive.

---

## 8. Customization

- **Model**: Change the `model="gpt-4o"` to another OpenAI model (e.g., `gpt-3.5-turbo`) if needed.  
- **Firestore structure**: Adjust how you name collections, store user data, or track inactivity if you have a different structure.  
- **Event toggles**: You can add logic in `event_info` documents to enable or disable certain features (e.g., skip age or region collection).

---

## 9. Troubleshooting

- **No messages received**: Check Twilio webhook URL and ensure it points to your deployed server.  
- **Event ID not recognized**: Verify you have a Firestore collection named `AOI_<event_id>`.  
- **OpenAI errors**: Check your OpenAI API key usage and model availability.  
- **Logging**: The script uses the `logger` for error reporting—review console logs or log files for details.

---

## 10. Contributing

1. **Fork** this repository and clone locally.  
2. Create a **feature branch** for your changes.  
3. **Test** thoroughly before creating a pull request.  
4. Submit a **pull request** describing your changes in detail.

---


**Happy Building!** If you have any questions or ideas, feel free to open an issue or pull request.