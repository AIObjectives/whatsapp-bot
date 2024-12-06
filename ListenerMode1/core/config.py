# core/config.py


import firebase_admin
from firebase_admin import credentials, firestore
from fastapi import FastAPI, Form, Response
from openai import OpenAI
from decouple import config
import logging
import json
from twilio.rest import Client as TwilioClient



firebase_credentials = json.loads(os.environ.get('FIREBASE_CREDENTIALS'))
cred = credentials.Certificate(firebase_credentials)
firebase_admin.initialize_app(cred)
db = firestore.client()


# FastAPI app initialization
app = FastAPI()

# OpenAI Configuration
OpenAI.api_key = config("OPENAI_API_KEY")
client = OpenAI(api_key=OpenAI.api_key)


# Twilio Configuration
twilio_account_sid = config("TWILIO_ACCOUNT_SID")
twilio_auth_token = config("TWILIO_AUTH_TOKEN")
twilio_client = TwilioClient(twilio_account_sid, twilio_auth_token)
twilio_number = config('TWILIO_NUMBER')



assistant_id = "xxx" ## 


# # Twilio Configuration
# twilio_account_sid = config("TWILIO_ACCOUNT_SID")
# twilio_auth_token = config("TWILIO_AUTH_TOKEN")
# twilio_client = TwilioClient(twilio_account_sid, twilio_auth_token)
# twilio_number = config('TWILIO_NUMBER')

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)



from fastapi import HTTPException, Response, Form, UploadFile, File
from uuid import uuid4
import os

import requests
import io
from pydub import AudioSegment

from requests.auth import HTTPBasicAuth

from openai import OpenAI


import openai
import re

# Configuration
openai_api_key = config('OPENAI_API_KEY')
openai_engine = 'gpt-4o'

