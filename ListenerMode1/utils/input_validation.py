import re

def is_valid_name(name):
    """Check if the provided name is valid."""
    if not name:
        return False
    name = name.strip().strip('"').strip("'")
    if not name or name.lower() == "anonymous":
        return False
    return any(char.isalpha() for char in name)

def is_valid_event_id(event_id, valid_event_ids):
    """Check if the event ID is valid."""
    return event_id in valid_event_ids

def is_valid_age(age):
    """Check if the provided age is a valid integer and within a reasonable range."""
    try:
        age = int(age)
        return 0 < age < 120
    except ValueError:
        return False

def is_valid_gender(gender):
    """Check if the provided gender is valid."""
    valid_genders = {"Male", "Female", "Non-binary", "Other"}
    return gender in valid_genders
