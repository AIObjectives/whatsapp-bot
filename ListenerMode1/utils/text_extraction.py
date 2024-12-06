import re

def extract_text_from_messages(messages):
    texts = []
    for message in messages:
        if message.role == "assistant":
            for content_block in message.content:
                if hasattr(content_block, "text") and hasattr(content_block.text, "value"):
                    texts.append(content_block.text.value)
    return " ".join(texts)

def extract_name_with_llm(response, system_message, client):
    try:
        name = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": system_message},
                {"role": "user", "content": response},
            ],
            max_tokens=50,
            temperature=0.6
        )
        return name.choices[0].message.content.strip() if name.choices else None
    except Exception as e:
        logging.error(f"Error in extracting name with LLM: {e}")
        return None
