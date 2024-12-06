

import firebase_admin
from firebase_admin import credentials, firestore
from datetime import datetime, timezone

# Initialize the Firebase app
if not firebase_admin._apps:
    cred = credentials.Certificate('yourpathxxx.json')
    firebase_admin.initialize_app(cred)

db = firestore.client()

def get_user_event_tracking_data():
    # Fetch all documents from 'user_event_tracking' collection
    user_event_tracking_ref = db.collection('user_event_tracking')
    docs = user_event_tracking_ref.stream()

    user_data = {}
    event_users = {}
    users_with_multiple_events = []

    print("Fetching user-event tracking data...")

    for doc in docs:
        user_id = doc.id  # normalized_phone
        data = doc.to_dict()
        events = data.get('events', [])
        awaiting_event_id = data.get('awaiting_event_id', False)
        current_event_id = data.get('current_event_id', None)

        # Compute last_activity from event timestamps
        last_activity = None
        if events:
            # Extract timestamps and convert to datetime objects
            event_timestamps = []
            for event in events:
                timestamp_str = event.get('timestamp')
                if timestamp_str:
                    try:
                        timestamp = datetime.fromisoformat(timestamp_str)
                        event_timestamps.append(timestamp)
                    except ValueError:
                        print(f"Invalid timestamp format for user '{user_id}': {timestamp_str}")
            if event_timestamps:
                # Find the most recent timestamp
                last_activity = max(event_timestamps)
                last_activity_str = last_activity.isoformat()
            else:
                last_activity_str = None
        else:
            last_activity_str = None

        user_data[user_id] = {
            'events': events,
            'last_activity': last_activity_str,
            'awaiting_event_id': awaiting_event_id,
            'current_event_id': current_event_id
        }

        if len(events) > 1:
            users_with_multiple_events.append(user_id)

        for event in events:
            event_id = event.get('event_id')
            if event_id:
                if event_id not in event_users:
                    event_users[event_id] = set()
                event_users[event_id].add(user_id)

    total_events = len(event_users)
    print(f"\nTotal number of different events: {total_events}")

    print("\nNumber of users in each event:")
    for event_id, users in event_users.items():
        print(f"Event '{event_id}': {len(users)} users")

    total_users_with_multiple_events = len(users_with_multiple_events)
    print(f"\nTotal number of users with more than one event: {total_users_with_multiple_events}")

    print("\nUsers with more than one event:")
    for user_id in users_with_multiple_events:
        event_ids = [event['event_id'] for event in user_data[user_id]['events']]
        print(f"User '{user_id}' is in events: {event_ids}")

    print("\nUser last activity timestamps:")
    for user_id, data in user_data.items():
        last_activity = data.get('last_activity')
        #print(f"User '{user_id}': Last activity at {last_activity}")

    return user_data, event_users, users_with_multiple_events

def delete_users_by_criteria(user_data, dry_run=True):
    """
    Deletes users from 'user_event_tracking' collection based on specified criteria.

    Parameters:
    - user_data (dict): Dictionary containing user data.
    - dry_run (bool): If True, the function will only preview the actions without making changes.
                      Set to False to perform actual deletions.
    """
    # Define criteria for deletion
    # For example, delete users whose last activity was before a certain date
    cutoff_date_str = input("\nEnter the cutoff date (YYYY-MM-DD) for last activity (users inactive before this date will be selected): ").strip()
    try:
        cutoff_date = datetime.strptime(cutoff_date_str, "%Y-%m-%d").replace(tzinfo=timezone.utc)
    except ValueError:
        print("Invalid date format. Please enter the date in YYYY-MM-DD format.")
        return

    # Collect users to delete
    users_to_delete = []
    for user_id, data in user_data.items():
        last_activity_str = data.get('last_activity')
        if last_activity_str:
            last_activity = datetime.fromisoformat(last_activity_str).replace(tzinfo=timezone.utc)
            if last_activity < cutoff_date:
                users_to_delete.append(user_id)
        else:
            # If last_activity is not set, consider the user for deletion
            users_to_delete.append(user_id)

    if not users_to_delete:
        print("\nNo users meet the criteria for deletion.")
        return

    print(f"\n{'[DRY RUN] ' if dry_run else ''}Users that would be deleted based on the criteria:")
    for user_id in users_to_delete:
        print(f"- User '{user_id}'")

    print(f"\nTotal users that would be deleted: {len(users_to_delete)}")

    if dry_run:
        print("\nThis is a dry run. No changes have been made.")
        proceed = input("Do you want to proceed with the actual deletion? Type 'yes' to confirm: ").strip().lower()
        if proceed != 'yes':
            print("No changes have been made.")
            return
        else:
            # Perform actual deletion
            delete_users_by_criteria(user_data, dry_run=False)
    else:
        # Uncomment the deletion line below to perform actual deletion
        # for user_id in users_to_delete:
        #     print(f"Deleting user '{user_id}' from 'user_event_tracking' collection...")
        #     # Uncomment/comment the line below to perform the actual deletion
        #     db.collection('user_event_tracking').document(user_id).delete()
        # print("\nDeletion completed.")

       
    # Perform actual deletion
        for user_id in users_to_delete:
            print(f"Deleting user '{user_id}' from 'user_event_tracking' collection...")
            # Delete from 'user_event_tracking'
            # Uncomment/comment the line below to perform the actual deletion

            db.collection('user_event_tracking').document(user_id).delete()
            
            # Also delete user from each event collection
            user_events = user_data[user_id].get('events', [])
            for event in user_events:
                event_id = event.get('event_id')
                if event_id:
                    print(f"Deleting user '{user_id}' from event collection 'AOI_{event_id}'...")
                    db.collection(f'AOI_{event_id}').document(user_id).delete()
        print("\nDeletion completed.")


def delete_users_by_event_id(user_data, dry_run=True):
    """
    Deletes users associated with a specific event ID from 'user_event_tracking' collection.

    Parameters:
    - user_data (dict): Dictionary containing user data.
    - dry_run (bool): If True, the function will only preview the actions without making changes.
                      Set to False to perform actual deletions.
    """
    event_id_to_delete = input("\nEnter the event ID to delete users from: ").strip()

    if not event_id_to_delete:
        print("No event ID entered. Operation cancelled.")
        return

    users_to_delete = []
    users_to_update = []

    for user_id, data in user_data.items():
        events = data.get('events', [])
        event_ids = [event.get('event_id') for event in events]
        if event_id_to_delete in event_ids:
            new_events = [event for event in events if event.get('event_id') != event_id_to_delete]
            if not new_events:
                users_to_delete.append(user_id)
            else:
                users_to_update.append((user_id, new_events))

    if not users_to_delete and not users_to_update:
        print("\nNo users are associated with the specified event ID.")
        return

    print(f"\n{'[DRY RUN] ' if dry_run else ''}Users that would be deleted or updated based on the event ID '{event_id_to_delete}':")

    for user_id in users_to_delete:
        print(f"- User '{user_id}' would be DELETED (no events left)")

    for user_id, _ in users_to_update:
        print(f"- User '{user_id}' would be UPDATED to remove event '{event_id_to_delete}'")

    total_affected_users = len(users_to_delete) + len(users_to_update)
    print(f"\nTotal users that would be deleted or updated: {total_affected_users}")

    if dry_run:
        print("\nThis is a dry run. No changes have been made.")
        proceed = input("Do you want to proceed with the actual deletion? Type 'yes' to confirm: ").strip().lower()
        if proceed != 'yes':
            print("No changes have been made.")
            return
        else:
            # Perform actual deletion
            delete_users_by_event_id(user_data, dry_run=False)
    # else:
    #     # Uncomment the deletion/update lines below to perform actual deletion
    #     for user_id in users_to_delete:
    #         print(f"Deleting user '{user_id}' from 'user_event_tracking' collection...")
    #         db.collection('user_event_tracking').document(user_id).delete()

    #     for user_id, new_events in users_to_update:
    #         print(f"Updating user '{user_id}' to remove event '{event_id_to_delete}'...")
    #         db.collection('user_event_tracking').document(user_id).update({'events': new_events})

    #     print("\nDeletion and updates completed.")
    else:
    # Perform actual deletion
        for user_id in users_to_delete:
            print(f"Deleting user '{user_id}' from 'user_event_tracking' collection...")
            db.collection('user_event_tracking').document(user_id).delete()
            
            # Also delete the user document from the specific event collection
            print(f"Deleting user '{user_id}' from event collection 'AOI_{event_id_to_delete}'...")
            db.collection(f'AOI_{event_id_to_delete}').document(user_id).delete()

        for user_id, new_events in users_to_update:
            print(f"Updating user '{user_id}' to remove event '{event_id_to_delete}'...")
            db.collection('user_event_tracking').document(user_id).update({'events': new_events})
            
            # Also delete the user document from the specific event collection
            print(f"Deleting user '{user_id}' from event collection 'AOI_{event_id_to_delete}'...")
            db.collection(f'AOI_{event_id_to_delete}').document(user_id).delete()

        print("\nDeletion and updates completed.")


def main():
    # Get detailed user-event tracking data
    user_data, event_users, users_with_multiple_events = get_user_event_tracking_data()

    # Option to delete users based on last activity
    delete_by_activity = input("\nDo you want to delete users based on last activity date? Type 'yes' to proceed: ").strip().lower()
    if delete_by_activity == 'yes':
        delete_users_by_criteria(user_data, dry_run=True)

    # Option to delete users by event ID
    delete_by_event = input("\nDo you want to delete users by event ID? Type 'yes' to proceed: ").strip().lower()
    if delete_by_event == 'yes':
        delete_users_by_event_id(user_data, dry_run=True)

if __name__ == '__main__':
    main()
