from twilio.rest import Client
import logging
from decouple import config

# Initialize Twilio
twilio_client = Client(config("TWILIO_ACCOUNT_SID"), config("TWILIO_AUTH_TOKEN"))
twilio_number = config("TWILIO_NUMBER")

def send_whatsapp_message(to_number, body_text):
    if not to_number.startswith("whatsapp:"):
        to_number = f"whatsapp:{to_number}"
    try:
        message = twilio_client.messages.create(
            body=body_text,
            from_=f"whatsapp:{twilio_number}",
            to=to_number
        )
        logging.info(f"Message sent to {to_number}: {message.body}")
    except Exception as e:
        logging.error(f"Error sending message to {to_number}: {e}")
