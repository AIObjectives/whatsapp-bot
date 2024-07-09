# import logging
# from twilio.rest import Client
# from decouple import config

# # Configuration
# account_sid = config('TWILIO_ACCOUNT_SID')
# auth_token = config('TWILIO_AUTH_TOKEN')
# twilio_number = config('TWILIO_NUMBER')

# # Set up the Twilio client
# client = Client(account_sid, auth_token)

# # Set up logging
# logging.basicConfig(level=logging.INFO)
# logger = logging.getLogger(__name__)

# def send_message(to_number, body_text):
#     """Send a message via WhatsApp using Twilio API."""
#     formatted_number = f'whatsapp:{to_number}' if not to_number.startswith('whatsapp:') else to_number

#     try:
#         message = client.messages.create(
#             body=body_text,
#             from_=f'whatsapp:{twilio_number}',
#             to=formatted_number
#         )
#         logger.info(f"Message sent to {formatted_number}: {message.body}")
#     except Exception as e:
#         logger.error(f"Error sending message to {formatted_number}: {e}")



# ### this is working below:::

# # Standard library import
# import logging

# # Third-party imports
# from twilio.rest import Client
# from decouple import config



# account_sid = config("TWILIO_ACCOUNT_SID")
# auth_token = config("TWILIO_AUTH_TOKEN")
# client = Client(account_sid, auth_token)
# twilio_number = config('TWILIO_NUMBER')

# # Set up logging
# logging.basicConfig(level=logging.INFO)
# logger = logging.getLogger(__name__)


# def send_message(to_number, body_text):
#     # Log the phone number to inspect its format before sending
#     logger.info(f"Attempting to send message to: {to_number}")

#     # Ensure `to_number` is in the correct format, e.g., '+13109546871'
#     if not to_number.startswith('whatsapp:'):
#         to_number = f'whatsapp:{to_number}'

#     try:
#         message = client.messages.create(
#             body=body_text,
#             from_=f'whatsapp:{twilio_number}',
#             to=to_number
#         )
#         logger.info(f"Message sent to {to_number}: {message.body}")
#     except Exception as e:
#         logger.error(f"Error sending message to {to_number}: {e}")

from twilio.rest import Client
from decouple import config
import logging

# Initialize Twilio client
account_sid = config("TWILIO_ACCOUNT_SID")
auth_token = config("TWILIO_AUTH_TOKEN")
client = Client(account_sid, auth_token)
twilio_number = config('TWILIO_NUMBER')

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def send_message(to_number, body_text, media_url=None):
    # Log the phone number to inspect its format before sending
    logger.info(f"Attempting to send message to: {to_number}")

    # Ensure `to_number` is in the correct format, e.g., '+13109546871'
    if not to_number.startswith('whatsapp:'):
        to_number = f'whatsapp:{to_number}'

    try:
        if media_url:
            # Sending message with media
            message = client.messages.create(
                body=body_text,
                from_=f'whatsapp:{twilio_number}',
                to=to_number,
                media_url=[media_url]
            )
        else:
            # Sending message without media
            message = client.messages.create(
                body=body_text,
                from_=f'whatsapp:{twilio_number}',
                to=to_number
            )
        logger.info(f"Message sent to {to_number}: {message.body}")
    except Exception as e:
        logger.error(f"Error sending message to {to_number}: {e}")


