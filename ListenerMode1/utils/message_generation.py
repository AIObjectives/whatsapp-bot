def generate_prompt_with_llm(event_name, event_location, participant_name=None):
    base_prompt = f"You are a friendly assistant at {event_name} in {event_location}."
    if participant_name:
        base_prompt += f" You have the participant's name: {participant_name}."
    return base_prompt
