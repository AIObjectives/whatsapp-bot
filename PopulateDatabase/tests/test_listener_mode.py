
#Example Usage in main.py
#Here’s how you can use the listener_mode module in your main.py:

from listener_mode.initialize_listener import initialize_event_collection

# Define event details
event_id = "Dec3FullDynamicListenerMode"
event_name = "Dec3FullDynamicListenerMode"
event_location = "Global"
event_background = "A survey exploring the experiences and challenges of LBQ+ women in various sectors."
event_date = "2024-12-01"

# Initialize Listener Mode event
initialize_event_collection(
    event_id,
    event_name,
    event_location,
    event_background,
    event_date
)
