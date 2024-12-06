#Example Usage in main.py
#Here’s how you can use the openended_mode module in your main.py:

from openended_mode.initialize_openended import initialize_event_collection

# Define event details
event_id = "Dec3FullDynamicFollowUp"
event_name = "Dec3FullDynamicFollowUp"
main_question = "How to be popular like Ariana Grande?"
event_location = "Global"
event_background = "A survey exploring the experiences and challenges of LBQ+ women in various sectors."
event_date = "2024-12-01"

# Initialize Open-Ended Mode event
initialize_event_collection(
    event_id,
    event_name,
    event_location,
    event_background,
    event_date,
    main_question
)
