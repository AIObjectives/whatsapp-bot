from fastapi import APIRouter
from openai_service import OpenAIService
from twilio_service import TwilioService
from firebase_service import FirebaseService
from config import Config

app_routes = APIRouter()
app_config = Config()
openai_service = OpenAIService(app_config)
twilio_service = TwilioService(app_config)
firebase_service = FirebaseService(app_config)

@app_routes.post("/message/")
async def reply(request_body: dict):
    """Endpoint to handle incoming messages and respond using AI."""
    try:
        from_number = request_body['From']
        message_body = request_body['Body']
        response = openai_service.create_thread(message_body)
        twilio_service.send_whatsapp_message(from_number, response)
        return {"status": "Success", "message": "Reply sent"}
    except Exception as e:
        return {"status": "Error", "message": str(e)}

# Example usage: Add this router to your FastAPI app in main.py
