from openai import OpenAI
import logging
from decouple import config

# Initialize OpenAI
openai = OpenAI(api_key=config("OPENAI_API_KEY"))

def generate_completion(system_message, user_input, max_tokens=150, temperature=0.5):
    try:
        response = openai.ChatCompletion.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": system_message},
                {"role": "user", "content": user_input}
            ],
            max_tokens=max_tokens,
            temperature=temperature,
        )
        return response.choices[0].message.content.strip() if response.choices else None
    except Exception as e:
        logging.error(f"Error generating OpenAI completion: {e}")
        return None
