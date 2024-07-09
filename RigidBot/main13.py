from fastapi import FastAPI, Form
from message_handler import MessageHandler
from fastapi.responses import JSONResponse

app = FastAPI()
handler = MessageHandler()

@app.post("/message")
#async def reply(body: str = Form(...), from_number: str = Form(...)):
async def reply(Body: str = Form(), From: str = Form()):

    response = await handler.process_message(Body, From)
    return JSONResponse(status_code=200, content={"message": response})





# from fastapi import FastAPI, Form, Response
# from fastapi.responses import JSONResponse

# app = FastAPI()

# @app.post("/message")
# async def reply(body: str = Form(...), from_number: str = Form(...)):
#     # Process the message here (example logging)
#     print(f"Received message from {from_number}: {body}")
#     # Dummy response for demonstration
#     return JSONResponse(status_code=200, content={"message": "Processed"})

# from fastapi import FastAPI, Form, Response

# app = FastAPI()

# @app.post("/message")
# async def reply(body: str = Form(...), from_number: str = Form(...)):
#     print(f"Message from {from_number}: {body}")
#     return Response(content="Message received", status_code=200)








# import openai
# from fastapi import FastAPI, Form, Response
# import firebase_admin
# from firebase_admin import credentials, firestore
# from utils import send_message
# from twilio.twiml.messaging_response import MessagingResponse
# from decouple import config

# # Initialize Firebase
# cred = credentials.Certificate('/Users/emreturan/Desktop/firebase/aoiwhatsappbot-firebase-adminsdk-rki5n-9526831994.json')
# firebase_admin.initialize_app(cred)
# db = firestore.client()

# # Initialize FastAPI and OpenAI
# app = FastAPI()
# openai.api_key = config("OPENAI_API_KEY")

# @app.post("/message")
# async def reply(Body: str = Form(), From: str = Form()):
#     normalized_phone = From.lstrip("+").replace("-", "").replace(" ", "")
#     user_doc_ref = db.collection('whatsapp_conversations').document(normalized_phone)
#     doc = user_doc_ref.get()
    
#     if Body.strip().lower() == "exit":
#         user_doc_ref.update({'state': 'exit'})
#         send_message(From, "You have exited the survey.")
#         return Response(status_code=200)
    
#     if not doc.exists or doc.to_dict().get('state') == 'exit':
#         send_welcome_message(From, user_doc_ref)
#         return Response(status_code=200)
    
#     user_data = doc.to_dict()
#     user_state = user_data.get('state', 'awaiting_selection')

#     if user_state == 'awaiting_selection':
#         handle_selection(Body, From, user_doc_ref)
#     elif user_state == 'in_survey':
#         await handle_survey(Body, From, user_doc_ref, user_data)
#     elif user_state == 'in_conversation':
#         await handle_conversation(Body, From, user_doc_ref)

#     return Response(status_code=200)

# def send_welcome_message(to_number, doc_ref):
#     welcome_message = ("Welcome to the AOI (AI Objectives Institute)! "
#                        "We are here to learn more about you and your environment. "
#                        "Please select how you would like to interact with me:\n"
#                        "1) Take a general survey\n"
#                        "2) More conversation based.")
#     send_message(to_number, welcome_message)
#     doc_ref.set({'state': 'awaiting_selection', 'interactions': [], 'last_interaction': firestore.SERVER_TIMESTAMP}, merge=True)

# def handle_selection(body, to_number, doc_ref):
#     if body.strip() == '1':
#         doc_ref.update({'state': 'in_survey'})
#         survey_ref = db.collection('surveys').document('community_survey')
#         survey_doc = survey_ref.get()
#         survey_data = survey_doc.to_dict()
#         first_question = survey_data['questions'][0]['question']
#         send_message(to_number, first_question)
#         doc_ref.update({'survey': {'current_question': 0, 'responses': []}}, merge=True)
#     elif body.strip() == '2':
#         doc_ref.update({'state': 'in_conversation'})
#         send_message(to_number, "You've selected more conversation based interaction. How can I assist you today?")
#     else:
#         send_message(to_number, "Please reply with '1' for a survey, or '2' for conversation.")

# async def handle_survey(body, to_number, doc_ref, user_data):
#     survey_state = user_data.get('survey', {})
#     current_question_index = survey_state.get('current_question', 0)
#     survey_ref = db.collection('surveys').document('community_survey')
#     survey_doc = survey_ref.get()
#     survey_data = survey_doc.to_dict()
#     questions = survey_data['questions']

#     if current_question_index < len(questions):
#         if body.strip().lower() not in ["yes", "exit"]:
#             # Append the response to the survey responses array and ask if the user wants to continue
#             doc_ref.update({'survey.responses': firestore.ArrayUnion([body])})
#             send_message(to_number, "Thank you for your answer. Would you like to elaborate more, or should we move to the next question? (Type 'yes' to continue to the next question)")
#         elif body.strip().lower() == "yes":
#             current_question_index += 1
#             if current_question_index < len(questions):
#                 next_question = questions[current_question_index]['question']
#                 send_message(to_number, next_question)
#                 doc_ref.update({'survey.current_question': current_question_index})
#             else:
#                 send_message(to_number, "Thank you for completing the survey!")
#                 doc_ref.update({'state': 'completed_survey'})
#         else:
#             send_message(to_number, "You have exited the survey.")
#             doc_ref.update({'state': 'exit'})


# async def handle_conversation(body, to_number, doc_ref):
#     response = openai.Completion.create(engine="gpt-3.5-turbo-instruct", prompt=body, max_tokens=200)
#     chat_response = response.choices[0].text.strip()
#     send_message(to_number, chat_response)
#     doc_ref.update({'interactions': firestore.ArrayUnion([{'message': body, 'response': chat_response, 'timestamp': firestore.SERVER_TIMESTAMP}])}, merge=True)


