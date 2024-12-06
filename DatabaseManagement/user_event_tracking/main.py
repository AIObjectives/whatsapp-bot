from user_event_tracking.utils.firebase_setup import initialize_firebase
from user_event_tracking.fetch_user_event_data.get_user_event_data import get_user_event_tracking_data
from user_event_tracking.fetch_user_event_data.delete_users_criteria import delete_users_by_criteria
from user_event_tracking.fetch_user_event_data.delete_users_event import delete_users_by_event_id

def main():
    db = initialize_firebase()
    user_data, event_users, users_with_multiple_events = get_user_event_tracking_data(db)

    delete_by_activity = input("Delete users by last activity? (yes/no): ").strip().lower()
    if delete_by_activity == 'yes':
        delete_users_by_criteria(db, user_data, dry_run=True)

    delete_by_event = input("Delete users by event ID? (yes/no): ").strip().lower()
    if delete_by_event == 'yes':
        delete_users_by_event_id(db, user_data, dry_run=True)

if __name__ == "__main__":
    main()
