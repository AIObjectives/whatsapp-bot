from listener_mode.initialize_listener import initialize_listener_event
from survey_mode.initialize_survey import initialize_survey_event
from opened_mode.initialize_opened import initialize_opened_event

def main():
    mode = input("Enter mode (listener/survey/opened): ").strip().lower()
    if mode == "listener":
        # Example configuration
        config = {"event_name": "Listener Test", "event_date": "2024-12-01"}
        initialize_listener_event("test_listener_event", config)
    elif mode == "survey":
        # Example configuration
        config = {"event_name": "Survey Test", "event_date": "2024-12-01"}
        initialize_survey_event("test_survey_event", config)
    elif mode == "opened":
        # Example configuration
        config = {"event_name": "Opened Test", "event_date": "2024-12-01"}
        initialize_opened_event("test_opened_event", config)
    else:
        print("Invalid mode selected.")

if __name__ == "__main__":
    main()
