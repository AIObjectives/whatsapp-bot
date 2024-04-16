import os
import tempfile

from dotenv import load_dotenv, find_dotenv
load_dotenv(find_dotenv())

OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
TWILIO_TOKEN = os.getenv('TWILIO_TOKEN')
TWILIO_SID = os.getenv('TWILIO_SID')
FROM = os.getenv('FROM')

ERROR_MESSAGE = 'We are facing an issue.'

OUTPUT_DIR = os.path.join(
    tempfile.gettempdir(),
    'document-gpt',
    'output'
)

os.makedirs(OUTPUT_DIR, exist_ok=True)
