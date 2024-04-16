# from database import Database
# from utils import send_message
# from openai_api import generate_response
# import firebase_admin
# from firebase_admin import credentials, firestore

# class MessageHandler:
#     def __init__(self):
#         self.db = Database()

#     async def process_message(self, body, from_number):
#         normalized_phone = from_number.lstrip("+").replace("-", "").replace(" ", "")
#         user_doc = self.db.get_document('whatsapp_conversations', normalized_phone)

#         # If the user document does not exist, it's a new conversation
#         if not user_doc:
#             self.db.create_document('whatsapp_conversations', normalized_phone, {'state': 'awaiting_fun_response'})
#             await self.ask_fun_question(from_number)
#             return "Asked fun question"

#         state = user_doc.get('state', 'new_user')

#         if state == 'awaiting_fun_response':
#             self.db.update_document('whatsapp_conversations', normalized_phone, {'state': 'awaiting_animal_response'})
#             await self.ask_animal_question(from_number)
#             return "Asked animal question"

#         elif state == 'awaiting_animal_response':
#             self.db.update_document('whatsapp_conversations', normalized_phone, {'state': 'welcome'})
#             await self.send_welcome_message(from_number)
#             return "Sent welcome message"

#         elif state == 'in_survey':
#             return await self.handle_survey(body, from_number, user_doc)

#         elif state == 'in_conversation':
#             return await self.handle_conversation(body, from_number, user_doc)

#         elif body.strip().lower() == "exit":
#             self.db.update_document('whatsapp_conversations', normalized_phone, {'state': 'exit'})
#             send_message(from_number, "You have exited.")
#             return "Exit acknowledged"

#         else:
#             send_message(from_number, "Not sure what you need, type 'help' for options.")
#             return "Fallback message sent"

#     # async def ask_fun_question(self, from_number):
#     #     # Generate a fun question with GPT
#     #     prompt = "Create a fun and engaging question to start a conversation."
#     #     fun_question = generate_response(prompt)
#     #     send_message(from_number, fun_question)
        
#     async def ask_fun_question(self, from_number):
#         # Generate a fun question with GPT
#         prompt = "Create a fun and engaging very short question to start a conversation."
#         fun_question = generate_response(prompt)
#         if fun_question:  # Check if a response was received
#             send_message(from_number, fun_question)
#         else:
#             send_message(from_number, "I'm having a bit of trouble, let's talk about something else!")

        
#     async def ask_animal_question(self, from_number):
#         animal_data = self.db.get_document('animal_images', 'random_animal')
#         if animal_data:
#             animal_url = animal_data.get('url')
#             # Here we send an empty string as body_text because we are sending an image with a question
#             send_message(from_number, "", media_url=animal_url)
#             send_message(from_number, "Which of these animals do you feel like today?")
#         else:
#             send_message(from_number, "Which animal do you feel like today? (Imagine your favorite animal.)")


#     async def send_welcome_message(self, from_number):
#         welcome_message = ("Welcome to the AOI (AI Objectives Institute)! "
#                            "We are here to learn more about you and your environment. "
#                            "Please select how you would like to interact with me:\n"
#                            "1) Take a general survey\n"
#                            "2) More conversation based\n"
#                            "3) Surprise me")
#         send_message(from_number, welcome_message)

#     def handle_selection(self, body, from_number, user_doc):
#         if body.strip() == '1':
#             self.db.update_document('whatsapp_conversations', from_number, {'state': 'in_survey'})
#             survey_ref = self.db.get_document('surveys', 'community_survey')
#             if survey_ref:
#                 first_question = survey_ref.get('questions', [])[0].get('question')
#                 send_message(from_number, first_question)
#                 self.db.update_document('whatsapp_conversations', from_number, {'survey': {'current_question': 0, 'responses': []}})
#                 return "Survey started"
#         elif body.strip() == '2':
#             self.db.update_document('whatsapp_conversations', from_number, {'state': 'in_conversation'})
#             send_message(from_number, "Conversation mode. How can I assist you today?")
#             return "Conversation started"
#         else:
#             send_message(from_number, "Please reply with '1' for a survey or '2' for conversation.")
#             return "Prompted for valid selection"

#     async def handle_survey(self, body, from_number, user_doc):
#         survey_state = user_doc.get('survey', {})
#         current_question_index = survey_state.get('current_question', 0)
#         survey_ref = self.db.get_document('surveys', 'community_survey')
#         if survey_ref:
#             questions = survey_ref.get('questions', [])
#             if current_question_index < len(questions):
#                 if body.strip().lower() not in ["yes", "exit"]:
#                     self.db.update_document('whatsapp_conversations', from_number, {'survey.responses': firestore.ArrayUnion([body])})
#                     send_message(from_number, "Thank you for your answer. Would you like to elaborate more, or should we move to the next question? (Type 'yes' to continue to the next question)")
#                 elif body.strip().lower() == "yes":
#                     current_question_index += 1
#                     if current_question_index < len(questions):
#                         next_question = questions[current_question_index]['question']
#                         send_message(from_number, next_question)
#                         self.db.update_document('whatsapp_conversations', from_number, {'survey.current_question': current_question_index})
#                     else:
#                         send_message(from_number, "Thank you for completing the survey!")
#                         self.db.update_document('whatsapp_conversations', from_number, {'state': 'completed_survey'})
#                 else:
#                     send_message(from_number, "You have exited the survey.")
#                     self.db.update_document('whatsapp_conversations', from_number, {'state': 'exit'})
#             return "Handled survey response"
#         return "Survey not found"

#     async def handle_conversation(self, body, from_number, user_doc):
#         response = generate_response(body)
#         send_message(from_number, response)
#         self.db.update_document('whatsapp_conversations', from_number, {'interactions': firestore.ArrayUnion([{'message': body, 'response': response, 'timestamp': firestore.SERVER_TIMESTAMP}])})
#         return "Handled conversation response"





######


from database import Database
from utils import send_message
from openai_api import generate_response
import firebase_admin
from firebase_admin import credentials, firestore
import random

class MessageHandler:
    def __init__(self):
        self.db = Database()

    async def process_message(self, body, from_number):
        normalized_phone = from_number.lstrip("+").replace("-", "").replace(" ", "")
        user_doc = self.db.get_document('whatsapp_conversations', normalized_phone)

        if not user_doc:
        #if 1==1:
            self.db.create_document('whatsapp_conversations', normalized_phone, {'state': 'initial'})
            await self.send_welcome_message(from_number)
            return "Welcome message sent"

        state = user_doc.get('state', 'initial')

        if body.strip().lower() == "exit":
            self.db.update_document('whatsapp_conversations', normalized_phone, {'state': 'exit'})
            send_message(from_number, "You have exited.")
            return "Exit acknowledged"

        if body.strip().lower() == "continue" and state != 'awaiting_fun_response':
            self.db.update_document('whatsapp_conversations', normalized_phone, {'state': 'initial'})
            await self.send_welcome_message(from_number)
            return "Continue acknowledged and welcome message sent"

        if state == 'initial':
            if body.strip().lower() == "yes":
                self.db.update_document('whatsapp_conversations', normalized_phone, {'state': 'awaiting_fun_response'})
                await self.ask_fun_question(from_number)
                return "Asked fun question"
            else:
                send_message(from_number, "That's completely fine if you don't want to interact with me today. If you want to continue, say 'continue' or to exit, say 'exit'.")
                return "No interaction"

        elif state == 'awaiting_fun_response':
            self.db.update_document('whatsapp_conversations', normalized_phone, {'state': 'awaiting_animal_response'})
            await self.ask_animal_question(from_number)
            return "Asked animal question"

        elif state == 'awaiting_animal_response':
            self.db.update_document('whatsapp_conversations', normalized_phone, {'state': 'awaiting_next_step'})
            send_message(from_number, "For our next step, please select how you would like to interact with me:\n1) Take a general survey\n2) More conversation based\n3) Surprise me")
            return "Asked for next step interaction"

        elif state == 'awaiting_next_step':
            if body.strip() == '1':
                self.db.update_document('whatsapp_conversations', normalized_phone, {'state': 'in_survey'})
                await self.start_survey(from_number)
                return "Survey started"
            elif body.strip() == '2':
                self.db.update_document('whatsapp_conversations', normalized_phone, {'state': 'in_conversation'})
                send_message(from_number, "Conversation mode. How can I assist you today?")
                return "Conversation started"
            else:
                send_message(from_number, "Please reply with '1' for a survey, '2' for conversation, or '3' for a surprise.")
                return "Prompted for valid selection"

    async def send_welcome_message(self, from_number):
        welcome_message = "Welcome to the AOI (AI Objectives Institute)! If you are ready to answer some short questions for me to get to know you, type 'yes'."
        send_message(from_number, welcome_message)

    async def ask_fun_question(self, from_number):
        prompt = "Create a fun and engaging question to start a conversation."
        fun_question = generate_response(prompt)
        send_message(from_number, fun_question)

    # async def ask_animal_question(self, from_number):
    #     animal_data = self.db.get_document('animal_images', 'random_animal')
    #     if animal_data:
    #         animal_url = animal_data.get('url')
    #         send_message(from_number, "", media_url=animal_url)
    #         send_message(from_number, "Which of these animals do you feel like today?")
    #     else:
    #         send_message(from_number, "Which animal do you feel like today? (Imagine your favorite animal.)")

    

    # async def ask_animal_question(self, from_number):
    #     # List of animal document IDs
    #     animal_ids = [
    #         'Animals+4.jpg',
    #         'Cute+animals+check-in.jpg',
    #         'animal.jpg',
    #         'cute+animals+3.jpg'
    #     ]        # Randomly pick one document ID
    #     random_animal_id = random.choice(animal_ids)
    #     # Fetch the document based on the randomly chosen ID
    #     animal_data = self.db.get_document('animal_images', random_animal_id)
        
    #     if animal_data:
    #         animal_url = animal_data.get('url')
    #         send_message(from_number, "", media_url=animal_url)
    #         send_message(from_number, "Which of these animals do you feel like today?")
    #     else:
    #         send_message(from_number, "Which animal do you feel like today? (Imagine your favorite animal.)")

    async def ask_animal_question(self, from_number):
        # List of document IDs for animal images in Firestore
        animal_doc_ids = ['Animals 4', 'Cute animals check-in', 'animal', 'cute animals 3']
        # Randomly pick one document ID
        random_doc_id = random.choice(animal_doc_ids)
        print("here it is",random_doc_id)
        # Fetch the document from Firestore
        animal_data = self.db.get_document('animal_images', random_doc_id)

        if animal_data:
            animal_url = animal_data.get('url')
            send_message(from_number, "", media_url=animal_url)
            send_message(from_number, "Which of these animals do you feel like today?")
        else:
            send_message(from_number, "Which animal do you feel like today? (Imagine your favorite animal.)")

    async def start_survey(self, from_number):
        survey_data = self.db.get_document('surveys', 'community_survey')
        if survey_data:
            questions = survey_data.get('questions', [])
            if questions:
                first_question = questions[0].get('question')
                send_message(from_number, first_question)
                self.db.update_document('whatsapp_conversations', from_number, {'survey': {'current_question': 0, 'responses': []}})
            else:
                send_message(from_number, "The survey does not have any questions.")
        else:
            send_message(from_number, "Sorry, the survey is currently unavailable.")

    async def handle_survey(self, body, from_number, user_doc):
        survey_state = user_doc.get('survey', {})
        current_question_index = survey_state.get('current_question', 0)
        survey_data = self.db.get_document('surveys', 'community_survey')
        if survey_data:
            questions = survey_data.get('questions', [])
            if current_question_index < len(questions):
                if body.strip().lower() not in ["yes", "exit"]:
                    self.db.update_document('whatsapp_conversations', from_number, {'survey.responses': firestore.ArrayUnion([body])})
                    send_message(from_number, "Thank you for your answer. Would you like to elaborate more, or should we move to the next question? (Type 'yes' to continue to the next question)")
                elif body.strip().lower() == "yes":
                    current_question_index += 1
                    if current_question_index < len(questions):
                        next_question = questions[current_question_index].get('question')
                        send_message(from_number, next_question)
                        self.db.update_document('whatsapp_conversations', from_number, {'survey.current_question': current_question_index})
                    else:
                        send_message(from_number, "Thank you for completing the survey!")
                        self.db.update_document('whatsapp_conversations', from_number, {'state': 'completed_survey'})
                else:
                    send_message(from_number, "You have exited the survey.")
                    self.db.update_document('whatsapp_conversations', from_number, {'state': 'exit'})
            else:
                send_message(from_number, "No more questions in the survey.")
            return "Handled survey response"
        else:
            send_message(from_number, "Survey data not found.")
            return "Survey not found"

    async def handle_conversation(self, body, from_number, user_doc):
        response = generate_response(body)
        send_message(from_number, response)
        self.db.update_document('whatsapp_conversations', from_number, {'interactions': firestore.ArrayUnion([{'message': body, 'response': response, 'timestamp': firestore.SERVER_TIMESTAMP}])})
        return "Handled conversation response"

