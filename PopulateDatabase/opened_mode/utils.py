# Utility functions for Open-Ended Mode

def validate_main_question(main_question):
    """Validates that the main question is non-empty and meaningful."""
    if not main_question or len(main_question.strip()) == 0:
        raise ValueError("Main question must be a non-empty string.")
    return main_question
