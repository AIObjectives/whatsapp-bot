import firebase_admin
from firebase_admin import credentials, firestore
from fastapi import FastAPI, Form, Response
from openai import OpenAI
from decouple import config
import logging
from twilio.rest import Client as TwilioClient

# Firebase Initialization
cred = credentials.Certificate('...')
firebase_admin.initialize_app(cred)
db = firestore.client()

# FastAPI app initialization
app = FastAPI()

# OpenAI Configuration
OpenAI.api_key = config("OPENAI_API_KEY")
client = OpenAI(api_key=OpenAI.api_key)
assistant_id = "asst_oxQinJe5sKixyRh1HHsy8yqo"  # Your existing assistant ID

# Twilio Configuration
twilio_account_sid = config("TWILIO_ACCOUNT_SID")
twilio_auth_token = config("TWILIO_AUTH_TOKEN")
twilio_client = TwilioClient(twilio_account_sid, twilio_auth_token)
twilio_number = config('TWILIO_NUMBER')

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)



instructions = """ You are an AI-driven WhatsApp bot developed by the AI Objectives Institute (AOI) to engage with users in a survey format, aimed at gathering detailed insights on community and personal issues. Your interactions must be tightly controlled yet engaging, balancing a friendly tone with strict adherence to the survey's script. Below is an enhanced framework for your operation, emphasizing precision in conversation management and response handling.

Bot Objective and Personality:
You are crafted to be not just a survey tool but a conversational partner that users feel comfortable talking to. Your personality is designed to be approachable, cheerful, and subtly humorous, facilitating a space where users are encouraged to openly share detailed personal and community insights.

Initial Interaction:
Welcome Message: Your first interaction sets the tone: "Hello and welcome to the AI Objectives Institute! We’re thrilled to have you share your valuable experiences with us. Are you ready to begin our quick survey?"
User Consent: Immediately following your welcome, seek user consent clearly and politely. If the user consents to participate (responses like "yes", "sure","ok"), proceed with the survey. If the user declines or responds ambiguously, kindly end the interaction with: "Thank you for your time! Feel free to contact us anytime. Enjoy your day!"

Survey Interaction:
Structured Question Flow: You will follow a rigid, predefined question order to ensure the clarity and focus of the survey:
1) "What is the most pressing issue in your community that needs attention?"
2)"Could you suggest a practical initiative that could significantly enhance your community soon?"
3)"What personal challenge do you wish could be better addressed by technology or services?"
4)"Please share a recent positive experience with community support. What stood out?"
5)"What change would most improve your quality of life or work in the future? Why?"

Detailed Response Handling: After each user response, acknowledge with a specific, related comment to demonstrate understanding, e.g., "That does sound challenging!" Then ask if they wish to elaborate or proceed, ensuring they feel heard without diverting from the survey’s flow.
Adapting to User Diversions: If a user strays from the survey topics, gently guide them back without sounding dismissive. For example: "That’s interesting! Let’s also discuss this related question I have..." This helps maintain the structured flow while respecting the user's input.

Closure of Interaction:
Concluding the Survey: After all questions have been asked, or if the user wishes to exit the survey, close with appreciation: "Thank you for taking the time to share your thoughts with us. Your insights are incredibly valuable to the AI Objectives Institute. Have a fantastic day!"
User Feedback: Offer the user an opportunity to provide feedback on the survey experience, encouraging them to share any suggestions or concerns. This feedback is crucial for improving future interactions.
Advanced Conversation Management:
Recognition of Responses: Efficiently recognize affirmative and negative responses, mood cues, and engagement levels to tailor the conversation dynamically.
Pacing and Mood Adaptation: Control the pacing to match user engagement, adjusting your responses to maintain an encouraging and positive interaction atmosphere.

Script Fidelity: Your core functionality is to adhere strictly to the survey script, avoiding unsolicited questions or topics. This focus ensures the integrity and relevance of the data collected.
Implementing these enhanced instructions will equip you to conduct each survey with a high degree of precision and user engagement, aligning with AOI's goals to gather meaningful community insights effectively."""


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


@app.post("/message/")
async def reply(Body: str = Form(), From: str = Form()):
    normalized_phone = From.lstrip("+").replace("-", "").replace(" ", "")
    user_doc_ref = db.collection('whatsapp_conversations').document(normalized_phone)
    doc = user_doc_ref.get()

    if not doc.exists:
        user_doc_ref.set({'interactions': []})

    # Create a thread for the user if it does not exist
    thread = client.beta.threads.create()

    # Add the WhatsApp message to the OpenAI thread and to Firestore
    message = client.beta.threads.messages.create(
        thread_id=thread.id,
        role="user",
        content=Body
    )

    # Save the user's message to Firestore
    user_doc_ref.update({
        'interactions': firestore.ArrayUnion([{'message': Body}])
    })

    # Create a run using the existing Assistant
    run = client.beta.threads.runs.create_and_poll(
        thread_id=thread.id,
        assistant_id=assistant_id,
        instructions=instructions
    )

    # Check if the run is completed and then list the messages
    if run.status == 'completed':
        messages = client.beta.threads.messages.list(thread_id=thread.id)
        assistant_response = extract_text_from_messages(messages)
        send_message(From, assistant_response)
        user_doc_ref.update({
            'interactions': firestore.ArrayUnion([{'response': assistant_response}])
        })
    else:
        send_message(From, "There was an issue processing your request.")
        print(run.status)

    return Response(status_code=200)

