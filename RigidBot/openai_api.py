import openai
from decouple import config
import logging

# Configuration
openai_api_key = config('OPENAI_API_KEY')
openai_engine = 'gpt-3.5-turbo-instruct'

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# def generate_response(prompt):
#     """Generate a response from OpenAI's GPT model based on the given prompt."""
#     try:
#         response = openai.Completion.create(
#             engine=openai_engine,
#             prompt=prompt,
#             max_tokens=150,
#             temperature=0.7
#         )
#         return response.choices[0].text.strip()
#     except Exception as e:
#         logger.error(f"Error in generating response from OpenAI: {e}")
#         return "I'm sorry, but I'm having trouble understanding that right now."


def generate_response(prompt):
    """Generate a response from OpenAI's GPT model based on the given prompt."""
    try:
        response = openai.Completion.create(
            engine=openai_engine,
            prompt=prompt,
            max_tokens=150,
            temperature=0.7,
            api_key=openai_api_key  # Ensure the API key is passed correctly
        )
        return response.choices[0].text.strip()
    except Exception as e:
        logger.error("Error in generating response from OpenAI: {}".format(e))
        return None  # Return None or raise the exception to handle it appropriately

