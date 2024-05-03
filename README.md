# WhatsApp Survey Bot for AI Objectives Institute (AOI)

This repository contains the code for a WhatsApp survey bot developed using FastAPI, Firebase, Twilio, and OpenAI. The bot is designed to conduct structured surveys with users over WhatsApp, gathering insights on community and personal issues in a conversational and engaging manner.

## Features

- **Firebase Integration**: Stores user interaction history and manages session data.
- **Twilio WhatsApp API**: Handles sending and receiving WhatsApp messages.
- **OpenAI API**: Powers the conversational AI, ensuring responses are engaging and contextually relevant.
- **FastAPI**: Provides a robust and scalable backend framework.

## Setup and Installation

### Prerequisites

- Python 3.8 or higher
- Firebase account and a service account key
- Twilio account with a WhatsApp-enabled number
- OpenAI API key/assistant

### Installation Steps

1. **Clone the repository**:
   ```
   git clone https://github.com/yourusername/whatsapp-survey-bot.git
   cd whatsapp-survey-bot
   ```

2. **Install dependencies**:
   ```
   pip install fastapi uvicorn firebase-admin openai python-decouple twilio
   ```

3. **Setup environment variables**:
   Create a `.env` file in the root directory and fill in your credentials:
   ```
   OPENAI_API_KEY='Your OpenAI API Key'
   TWILIO_ACCOUNT_SID='Your Twilio Account SID'
   TWILIO_AUTH_TOKEN='Your Twilio Auth Token'
   TWILIO_NUMBER='Your Twilio WhatsApp Number'
   GOOGLE_APPLICATION_CREDENTIALS='Path to your Firebase admin SDK JSON file'
   ```

4. **Run the server**:
   ```
   uvicorn AOI_bot_customgpt:app --reload
   ```

5. **Expose it to the world**:
   ```
   Use localtunnel or Ngrok to test it locally and add the link to Twilio as POST request.
   ```

## Usage

Send a WhatsApp message to the configured Twilio number to begin interacting with the survey bot. The bot will guide you through a series of questions, maintaining a conversational and friendly tone.

## Bot Interaction Flow

1. **Welcome Message**: Greet users and ask for consent to participate in the survey.
2. **Survey Questions**: Sequentially ask predefined questions, ensuring clarity and focus.
3. **Response Handling**: Dynamically handle user responses, acknowledging input and prompting further discussion as needed.
4. **Closure**: Politely conclude the survey once all questions are answered or the user decides to exit.

## Advanced Features

- **Contextual Continuity**: Maintain conversation context effectively even with minimal user responses.
- **Adaptive Response Management**: Handle diverse user inputs intelligently, ensuring the conversation stays on track.
- **Exception Handling**: Robustly handle unexpected or off-topic responses without breaking the flow.




