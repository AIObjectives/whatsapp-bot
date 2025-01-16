
# Firebase-Enabled FastAPI Project

This project integrates **Firebase Firestore**, **OpenAI's GPT models**, **Twilio Messaging API**, and **FastAPI** to create an intelligent conversational agent. The agent is designed to interact with users dynamically, collect data, and store relevant information in a Firebase Firestore database.

## Key Features

1. **Dynamic User Interaction**: Handles user messages using FastAPI endpoints.
2. **Firestore Database Integration**: Manages user data and interactions, storing them in Firestore collections.
3. **OpenAI GPT Model Integration**: Processes user input using OpenAI for context-based understanding and decision-making.
4. **Twilio Messaging API**: Sends and receives user messages via SMS or WhatsApp.
5. **User Event Tracking**: Tracks multiple user events and manages user data for personalized interaction.
6. **Audio Transcription**: Converts audio messages to text using OpenAI Whisper.

## Technology Stack

- **Python**
- **FastAPI**
- **Firebase Admin SDK**
- **Twilio SDK**
- **OpenAI GPT API**
- **Pydantic**

## Installation

1. Clone the repository:
   ```bash
   git clone <repository_url>
   cd <repository_name>
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Configure environment variables:
   - Use `.env` to store keys and credentials:
     ```plaintext
     OPENAI_API_KEY=<Your OpenAI API Key>
     FIREBASE_CREDENTIALS_PATH=<Path to Firebase Credentials JSON>
     TWILIO_ACCOUNT_SID=<Your Twilio Account SID>
     TWILIO_AUTH_TOKEN=<Your Twilio Auth Token>
     TWILIO_NUMBER=<Your Twilio Number>
     ```

4. Initialize Firebase Admin SDK:
   - Add your Firebase credentials JSON file to the project.

5. Run the application:
   ```bash
   uvicorn main:app --reload
   ```

## API Endpoints

### `/message/` (POST)
Handles incoming user messages, extracts context, and generates dynamic responses.

**Parameters:**
- `Body` (str): Message text sent by the user.
- `From` (str): User's phone number.
- `MediaUrl0` (optional, str): URL of the media file (e.g., audio).

**Response:**
- Status code 200 on successful processing.

### Example Payload:
```json
{
  "Body": "Hello!",
  "From": "+1234567890",
  "MediaUrl0": null
}
```

## Project Structure

```
.
├── app.py                 # Main FastAPI application
├── agent_functions3_dry.py # Helper functions for OpenAI, Twilio, and processing
├── config1.py             # Configuration file for Firebase and other credentials
├── requirements.txt       # Python dependencies
├── .env                   # Environment variables
└── README.md              # Documentation
```

## Configuration Details

### Firebase Setup

1. Create a Firebase project at [Firebase Console](https://console.firebase.google.com/).
2. Enable Firestore Database and generate credentials (JSON file).
3. Save the credentials file and set its path in the `.env` file.

### OpenAI Setup

1. Get your API key from [OpenAI](https://platform.openai.com/signup/).
2. Add the API key to the `.env` file under `OPENAI_API_KEY`.

### Twilio Setup

1. Sign up for Twilio at [Twilio Console](https://www.twilio.com/).
2. Create a messaging service and get your Account SID, Auth Token, and Twilio number.
3. Add these details to the `.env` file.

## How It Works

### User Flow

1. A user sends a message to the Twilio number.
2. Twilio forwards the message to the FastAPI endpoint (`/message/`).
3. FastAPI processes the message:
   - Normalizes the user's phone number.
   - Checks and updates Firestore for existing or new user data.
   - Uses OpenAI GPT to interpret the user's input.
   - Responds dynamically via Twilio.
4. Responses are logged in Firestore for tracking and analytics.

### Core Functions

- **initialize_user_document(event_id, normalized_phone):**
  Creates a new user document in Firestore with default fields and tracking.

- **is_valid_name(name):**
  Validates user-provided names.

- **reply():**
  Handles incoming requests, extracts intent, processes user data, and sends responses.

## Development Notes

- **Concurrency:** Designed to handle multiple users and events concurrently.
- **Error Handling:** Implements structured logging and error messages.
- **Scalability:** Built with modular components to add features like analytics or custom prompts easily.


## Contribution

Feel free to fork the repository and submit pull requests. For major changes, open an issue first to discuss your proposed changes.

---
**Happy Building!** If you have any questions or ideas, feel free to open an issue or pull request.
