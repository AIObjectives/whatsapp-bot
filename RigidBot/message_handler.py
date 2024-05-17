





from database import Database
from utils import send_message
from openai_api import generate_response
import firebase_admin
from firebase_admin import credentials, firestore
import random

class MessageHandler:
    def __init__(self):
        self.db = Database()
        self.welcome_message_sent = {}
        
   
        
    # async def process_message(self, body, from_number):
    #     normalized_phone = from_number.lstrip("+").replace("-", "").replace(" ", "")
    #     user_doc = self.db.get_document('whatsapp_conversations', normalized_phone)
    #     interaction_count = user_doc.get('interaction_count', 0) if user_doc else 0
    #     state = user_doc.get('state', 'initial') if user_doc else 'initial'

    #     if not user_doc:
    #         # Create a new document for a new user with initial state and interaction count
    #         self.db.create_document('whatsapp_conversations', normalized_phone, {
    #             'state': 'initial',
    #             'interaction_count': 1
    #         })
    #         await self.send_welcome_message(from_number, False)
    #         return "New user document created and welcome message sent"

    #     if interaction_count >= 35:
    #         send_message(from_number, "You have reached your limit to interact with the bot. If you want to continue, contact AOI.")
    #         return "Interaction limit reached"

    #     if body.strip().lower() == "exit":
    #         interaction_count += 1
    #         self.db.update_document('whatsapp_conversations', normalized_phone, {
    #             'state': 'initial',
    #             'interaction_count': interaction_count
    #         })
    #         send_message(from_number, "You have exited. Type anything to start again.")
    #         return "Exit acknowledged and state reset"

    #     interaction_count += 1
    #     self.db.update_document('whatsapp_conversations', normalized_phone, {
    #         'interaction_count': interaction_count
    #     })

    #     if state == 'initial' and not self.welcome_message_sent.get(normalized_phone, False):
    #         await self.send_welcome_message(from_number, interaction_count > 0)
    #         self.welcome_message_sent[normalized_phone] = True
    #         return "Welcome message sent"

    #     if body.strip().lower() == "yes" and state == 'initial':
    #         self.db.update_document('whatsapp_conversations', normalized_phone, {'state': 'awaiting_fun_response'})
    #         await self.ask_fun_question(from_number)
    #         return "Asked fun question"

    #     if state == 'awaiting_fun_response':
    #         self.db.update_document('whatsapp_conversations', normalized_phone, {'state': 'awaiting_animal_response'})
    #         await self.ask_animal_question(from_number)
    #         return "Asked animal question"

    #     if state == 'awaiting_animal_response':
    #         self.db.update_document('whatsapp_conversations', normalized_phone, {'state': 'awaiting_next_step'})
    #         send_message(from_number, "For our next step, please select how you would like to interact with me:\n1) Take a general survey\n2) More conversation based\n3) Surprise me")
    #         return "Asked for next step interaction"

    #     if state == 'awaiting_next_step':
    #         if body.strip() == '1':
    #             self.db.update_document('whatsapp_conversations', normalized_phone, {'state': 'in_survey'})
    #             await self.start_survey(from_number)
    #             return "Survey started"
    #         elif body.strip() == '2':
    #             self.db.update_document('whatsapp_conversations', normalized_phone, {'state': 'in_conversation'})
    #             send_message(from_number, "Conversation mode. How can I assist you today?")
    #             return "Conversation started"
    #         else:
    #             send_message(from_number, "Please reply with '1' for a survey, '2' for conversation, or '3' for a surprise.")
    #             return "Prompted for valid selection"

    #     if state == 'in_conversation':
    #         # Handle the conversation mode by sending user input to the GPT-3.5 model
    #         response = generate_response(body)
    #         send_message(from_number, response)
    #         self.db.update_document('whatsapp_conversations', normalized_phone, {
    #             'interactions': firestore.ArrayUnion([{'message': body, 'response': response}])
    #         })
    #         return "Handled conversation response"

    #     if state in ['in_survey', 'awaiting_next_step', 'awaiting_animal_response', 'awaiting_fun_response']:
    #         await self.handle_survey(body, from_number, user_doc)
    #         return "Handled survey response"
        
    async def process_message(self, body, from_number):
        normalized_phone = from_number.lstrip("+").replace("-", "").replace(" ", "")
        user_doc = self.db.get_document('whatsapp_conversations', normalized_phone)
        interaction_count = user_doc.get('interaction_count', 0) if user_doc else 0
        state = user_doc.get('state', 'initial') if user_doc else 'initial'

        if not user_doc:
            # Create a new document for a new user with initial state and interaction count
            self.db.create_document('whatsapp_conversations', normalized_phone, {
                'state': 'initial',
                'interaction_count': 1  # Set to 1 as this is the first interaction
            })
            await self.send_welcome_message(from_number, False)
            self.welcome_message_sent[normalized_phone] = True  # Ensure welcome message is marked as sent
            return "New user document created and welcome message sent"

        if body.strip().lower() == "exit":
            interaction_count += 1  # Increment on exit
            # Reset the state but preserve interaction count and responses for future analysis
            self.db.update_document('whatsapp_conversations', normalized_phone, {
                'state': 'initial',
                'interaction_count': interaction_count
            })
            send_message(from_number, "You have exited. Type anything to start again.")
            self.welcome_message_sent[normalized_phone] = False  # Reset this to allow the welcome message to be sent again
            return "Exit acknowledged and state reset"

        interaction_count += 1  # Increment interaction count for other messages
        self.db.update_document('whatsapp_conversations', normalized_phone, {
            'interaction_count': interaction_count
        })

        # Check if a welcome message needs to be sent for restarting users
        if state == 'initial' and not self.welcome_message_sent.get(normalized_phone, False):
            await self.send_welcome_message(from_number, interaction_count > 1)
            self.welcome_message_sent[normalized_phone] = True
            return "Welcome message sent"

        # Handling other states and transitions
        if state == 'initial':
            if body.strip().lower() == "yes":
                self.db.update_document('whatsapp_conversations', normalized_phone, {'state': 'awaiting_fun_response'})
                await self.ask_fun_question(from_number)
                return "Asked fun question"
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
        elif state == 'in_conversation':
            response = generate_response(body)
            send_message(from_number, response)
            self.db.update_document('whatsapp_conversations', normalized_phone, {
                'interactions': firestore.ArrayUnion([{'message': body, 'response': response}])
            })
            return "Handled conversation response"

        # Handling survey responses if any
        if state in ['in_survey', 'awaiting_next_step', 'awaiting_animal_response', 'awaiting_fun_response']:
            await self.handle_survey(body, from_number, user_doc)
            return "Handled survey response"


    async def send_welcome_message(self, from_number, is_returning_user):
        if is_returning_user:
            welcome_message = "Welcome back to AOI! It's great to see you again. If you're ready to continue, type 'yes'."
        else:
            welcome_message = "Welcome to the AOI (AI Objectives Institute)! If you are ready to answer some short questions for me to get to know you, type 'yes'."
        send_message(from_number, welcome_message)

    async def ask_fun_question(self, from_number):
        prompt = "Create a fun and engaging question to start a conversation."
        fun_question = generate_response(prompt)
        send_message(from_number, fun_question)

    async def ask_animal_question(self, from_number):
        animal_doc_ids = ['Animals 4', 'Cute animals check-in', 'animal', 'cute animals 3']
        random_doc_id = random.choice(animal_doc_ids)
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
                current_survey = self.db.get_document('whatsapp_conversations', from_number)
                if 'survey' not in current_survey or 'responses' not in current_survey['survey']:
                    self.db.update_document('whatsapp_conversations', from_number, {'survey': {'current_question': 0, 'responses': []}})
                # Do not reset responses, just set the current question to start
                else:
                    self.db.update_document('whatsapp_conversations', from_number, {'survey.current_question': 0})
            else:
                send_message(from_number, "The survey does not have any questions.")
        else:
            send_message(from_number, "Sorry, the survey is currently unavailable.")


    
            
    async def handle_survey(self, body, from_number, user_doc):
        survey_state = user_doc.get('survey', {})
        current_question_index = survey_state.get('current_question', 0)
        survey_ref = self.db.get_document('surveys', 'community_survey')
        if survey_ref:
            questions = survey_ref.get('questions', [])
            if current_question_index < len(questions):
                if body.strip().lower() not in ["yes", "exit"]:
                    # Store response as part of an array but do not handle timestamps here
                    self.db.update_document('whatsapp_conversations', from_number, {'survey.responses': firestore.ArrayUnion([body])})
                    send_message(from_number, "Thank you for your answer. Would you like to elaborate more, or should we move to the next question? (Type 'yes' to continue to the next question)")
                elif body.strip().lower() == "yes":
                    current_question_index += 1
                    if current_question_index < len(questions):
                        next_question = questions[current_question_index]['question']
                        send_message(from_number, next_question)
                        self.db.update_document('whatsapp_conversations', from_number, {'survey.current_question': current_question_index})
                    else:
                        send_message(from_number, "Thank you for completing the survey! Type 'exit' to end the conversation.")
                        self.db.update_document('whatsapp_conversations', from_number, {'state': 'completed_survey'})
                else:
                    send_message(from_number, "You have exited the survey.")
                    self.db.update_document('whatsapp_conversations', from_number, {'state': 'exit'})
                return "Handled survey response"
            return "Survey not found"

    async def handle_conversation(self, body, from_number, user_doc):
        response = generate_response(body)
        send_message(from_number, response)
        # Update interaction history without the direct embedding of a timestamp
        self.db.update_document('whatsapp_conversations', from_number, {
            'interactions': firestore.ArrayUnion([{'message': body, 'response': response}])
        })
        return "Handled conversation response"


