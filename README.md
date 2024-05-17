

<p align="center">
   <img src="https://github.com/explomind1/twiliowhatsappbot/blob/main/d_SuSxWXmC.svg" />
</p>

# WhatsApp Survey Bot for AI Objectives Institute (AOI)

This repository contains the advanced codebase for a WhatsApp survey bot, leveraging FastAPI, Firebase, Twilio, and OpenAI. The bot is expertly designed to conduct structured and engaging surveys over WhatsApp, collecting valuable insights on community and personal issues directly from users.

## Key Features

- **Firebase Integration**: Manages user interaction history and session data effectively.
- **Twilio WhatsApp API**: Enables robust sending and receiving of WhatsApp messages.
- **OpenAI API**: Utilizes cutting-edge AI to deliver engaging, contextually appropriate responses.
- **FastAPI Framework**: Offers a scalable and efficient backend, ideal for real-time applications.

## Setup and Installation

### Prerequisites

- Python 3.8+
- Firebase account with a service account key
- Twilio account with WhatsApp capabilities
- OpenAI API key
- ngrok or localtunnel account for local testing
- Heroku account for deployment

### Installation Steps

1. **Clone the repository**:
   ```bash
   git clone https://github.com/yourusername/whatsapp-survey-bot.git
   cd whatsapp-survey-bot
   ```

2. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Set up environment variables**:
   Create a `.env` file in the project root with the following:
   ```plaintext
   OPENAI_API_KEY='Your OpenAI API Key'
   TWILIO_ACCOUNT_SID='Your Twilio Account SID'
   TWILIO_AUTH_TOKEN='Your Twilio Auth Token'
   TWILIO_NUMBER='Your Twilio WhatsApp Number'
   GOOGLE_APPLICATION_CREDENTIALS='Path to your Firebase admin SDK JSON file'
   ```

4. **Run the server locally**:
   ```bash
   uvicorn yourmainfilename:app --reload
   ```

### Local Testing

To test the application locally, expose your local server to the internet using either ngrok or localtunnel:

- **Using ngrok**:
  ```bash
  ngrok http 8000
  ```
  This will provide you with a public URL that you can use in Twilio's WhatsApp webhook settings.

- **Using localtunnel**:
  ```bash
  npx localtunnel --port 8000
  ```
  Similar to ngrok, this will provide a public URL to use with Twilio.

Update the webhook URL in your Twilio dashboard to point to the URL provided by ngrok or localtunnel.

### Deployment to Heroku

1. **Create a Heroku app**:
   ```bash
   heroku create your-app-name
   ```

2. **Add buildpacks**:
   ```bash
   heroku buildpacks:set heroku/python
   ```

3. **Set environment variables on Heroku**:
   ```bash
   heroku config:set OPENAI_API_KEY='Your OpenAI API Key'
   heroku config:set TWILIO_ACCOUNT_SID='Your Twilio Account SID'
   heroku config:set TWILIO_AUTH_TOKEN='Your Twilio Auth Token'
   heroku config:set TWILIO_NUMBER='Your Twilio WhatsApp Number'
   ```

4. **Deploy your application**:
   ```bash
   git push heroku master
   ```

5. **Update Twilio's webhook URL to point to your Heroku app**.

## Usage

Begin by sending a WhatsApp message to the configured Twilio number. The bot will engage you in a conversation, guiding you through a series of structured questions to gather insights.

## Interaction Flow

- **Initial Greeting**: Warmly welcomes users and seeks consent for participation.
- **Conducting the Survey**: Methodically presents questions, maintaining clarity and focus throughout.
- **Dynamic Response Handling**: Adaptively manages user responses, prompting further discussion where necessary.
- **Conclusion**: Graciously concludes the interaction after all questions are addressed.

## Advanced Features

- **Contextual Continuity**: Keeps track of conversation context effectively, even with brief user responses.
- **Adaptive Response Management**: Smartly adjusts to varied user inputs to keep discussions on track.
- **Exception Handling**: Expertly handles unexpected inputs or deviations without disrupting the conversation flow.
