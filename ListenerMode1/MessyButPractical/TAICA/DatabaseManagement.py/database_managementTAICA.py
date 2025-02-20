
import firebase_admin
from firebase_admin import credentials, firestore
from datetime import datetime, timezone

# ------------------------------------------------------------------------------
# Initialize the Firebase app
# ------------------------------------------------------------------------------
if not firebase_admin._apps:
    cred = credentials.Certificate('...')
    firebase_admin.initialize_app(cred)

db = firestore.client()


# ------------------------------------------------------------------------------
# Fetch user-event tracking data
# ------------------------------------------------------------------------------
def get_user_event_tracking_data():
    """
    Fetches and structures data from the 'user_event_tracking' collection.
    Returns:
        user_data (dict)           : Keyed by user_id (phone), each value is a dict containing:
                                      'events', 'last_activity', 'awaiting_event_id', 'current_event_id'
        event_users (dict)         : Keyed by event_id, each value is a set of user_ids
        users_with_multiple_events (list) : List of user_ids that have more than one event
    """
    user_event_tracking_ref = db.collection('user_event_tracking')
    docs = user_event_tracking_ref.stream()

    user_data = {}
    event_users = {}
    users_with_multiple_events = []

    print("Fetching user-event tracking data...")

    for doc in docs:
        user_id = doc.id  # Typically the normalized phone number
        data = doc.to_dict() or {}
        events = data.get('events', [])
        awaiting_event_id = data.get('awaiting_event_id', False)
        current_event_id = data.get('current_event_id', None)

        # Calculate last_activity by examining event timestamps
        last_activity = None
        if events:
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

        # Track users with multiple events
        if len(events) > 1:
            users_with_multiple_events.append(user_id)

        # Build an index of event -> set of user_ids
        for event in events:
            event_id = event.get('event_id')
            if event_id:
                if event_id not in event_users:
                    event_users[event_id] = set()
                event_users[event_id].add(user_id)

    # Summary prints
    total_events = len(event_users)
    print(f"\nTotal number of different events: {total_events}")

    print("\nNumber of users in each event:")
    for event_id, users in event_users.items():
        print(f"Event '{event_id}': {len(users)} users")

    total_users_with_multiple_events = len(users_with_multiple_events)
    print(f"\nTotal number of users with more than one event: {total_users_with_multiple_events}")

    print("\nUsers with more than one event:")
    for user_id in users_with_multiple_events:
        event_ids = [e['event_id'] for e in user_data[user_id]['events']]
        print(f"User '{user_id}' is in events: {event_ids}")

    return user_data, event_users, users_with_multiple_events


# ------------------------------------------------------------------------------
# Delete users by last activity date
# ------------------------------------------------------------------------------
def delete_users_by_criteria(user_data, dry_run=True):
    """
    Deletes users from 'user_event_tracking' based on last activity date.

    Parameters:
        user_data (dict): Dictionary containing user data from get_user_event_tracking_data().
        dry_run    (bool): If True, only previews the actions without making changes.
                           If False, performs the actual deletions.
    """
    # Define criteria for deletion
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
            # If no last_activity, consider user for deletion
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
            # Perform actual deletion (recursively call with dry_run=False)
            delete_users_by_criteria(user_data, dry_run=False)
    else:
        # Actual deletion
        for user_id in users_to_delete:
            print(f"Deleting user '{user_id}' from 'user_event_tracking' collection...")
            db.collection('user_event_tracking').document(user_id).delete()
            
            # Also remove user from each event collection
            user_events = user_data[user_id].get('events', [])
            for event in user_events:
                event_id = event.get('event_id')
                if event_id:
                    print(f"Deleting user '{user_id}' from event collection 'AOI_{event_id}'...")
                    db.collection(f'AOI_{event_id}').document(user_id).delete()

        print("\nDeletion completed.")


# ------------------------------------------------------------------------------
# Delete users by a specific event ID
# ------------------------------------------------------------------------------
def delete_users_by_event_id(user_data, dry_run=True):
    """
    Deletes or updates users associated with a specific event ID from 
    'user_event_tracking', and also removes them from the relevant event collection.

    Parameters:
        user_data (dict): Dictionary containing user data from get_user_event_tracking_data().
        dry_run    (bool): If True, only previews the actions without making changes.
                           If False, performs the actual deletions/updates.
    """
    event_id_to_delete = input("\nEnter the event ID to delete users from: ").strip()

    if not event_id_to_delete:
        print("No event ID entered. Operation cancelled.")
        return

    users_to_delete = []
    users_to_update = []

    # Identify which users will be deleted entirely vs. updated
    for user_id, data in user_data.items():
        events = data.get('events', [])
        event_ids = [e.get('event_id') for e in events]
        if event_id_to_delete in event_ids:
            new_events = [e for e in events if e.get('event_id') != event_id_to_delete]
            if not new_events:
                # No events left after removal -> user is deleted
                users_to_delete.append(user_id)
            else:
                # Remove only this event, keep the user doc
                users_to_update.append((user_id, new_events))

    if not users_to_delete and not users_to_update:
        print("\nNo users are associated with the specified event ID.")
        return

    # Preview
    print(f"\n{'[DRY RUN] ' if dry_run else ''}Users that would be deleted or updated for event '{event_id_to_delete}':")

    for user_id in users_to_delete:
        print(f"- User '{user_id}' would be DELETED (no events left).")

    for user_id, _ in users_to_update:
        print(f"- User '{user_id}' would be UPDATED to remove event '{event_id_to_delete}'.")

    total_affected_users = len(users_to_delete) + len(users_to_update)
    print(f"\nTotal users that would be deleted or updated: {total_affected_users}")

    if dry_run:
        print("\nThis is a dry run. No changes have been made.")
        proceed = input("Do you want to proceed with the actual deletion? Type 'yes' to confirm: ").strip().lower()
        if proceed != 'yes':
            print("No changes have been made.")
            return
        else:
            # Perform actual deletion (recursively call with dry_run=False)
            delete_users_by_event_id(user_data, dry_run=False)
    else:
        # Actual deletion
        for user_id in users_to_delete:
            print(f"Deleting user '{user_id}' from 'user_event_tracking' collection...")
            db.collection('user_event_tracking').document(user_id).delete()

            print(f"Deleting user '{user_id}' from event collection 'AOI_{event_id_to_delete}'...")
            db.collection(f'AOI_{event_id_to_delete}').document(user_id).delete()

        # Actual updates (partial event removal)
        for user_id, new_events in users_to_update:
            print(f"Updating user '{user_id}' to remove event '{event_id_to_delete}' from 'user_event_tracking'...")
            db.collection('user_event_tracking').document(user_id).update({'events': new_events})
            
            print(f"Deleting user '{user_id}' from event collection 'AOI_{event_id_to_delete}'...")
            db.collection(f'AOI_{event_id_to_delete}').document(user_id).delete()

        print("\nDeletion and updates completed.")


# ------------------------------------------------------------------------------
# NEW: Delete a specific phone number from all or some events
# ------------------------------------------------------------------------------
def delete_users_by_phone_number(user_data, dry_run=True):
    """
    Allows deleting a single phone number (user) from one, multiple, or all events.
    - If all events are removed, the user document is deleted from 'user_event_tracking'.
    - If some events are removed, the user document is updated accordingly.

    Parameters:
        user_data (dict): Dictionary containing user data from get_user_event_tracking_data().
        dry_run    (bool): If True, only previews the actions without making changes.
                           If False, performs the actual deletions/updates.
    """
    phone_number = input("\nEnter the phone number to delete or remove from events: ").strip()

    if not phone_number:
        print("No phone number entered. Operation cancelled.")
        return

    # Check if the user exists in user_data
    if phone_number not in user_data:
        print(f"\nUser '{phone_number}' not found in 'user_event_tracking'.")
        return

    events = user_data[phone_number].get('events', [])
    if not events:
        print(f"\nUser '{phone_number}' is not associated with any events.")
        return

    print(f"\nUser '{phone_number}' is associated with these events:")
    for event in events:
        print(f" - {event.get('event_id')}")

    remove_all = input("\nDo you want to remove the user from ALL events? (Type 'yes' to proceed): ").strip().lower()

    if remove_all == 'yes':
        # Remove from ALL events
        events_to_remove = [e.get('event_id') for e in events if e.get('event_id')]
    else:
        # Let the user specify which events to remove
        event_ids = [e.get('event_id') for e in events if e.get('event_id')]
        print("\nEnter a comma-separated list of event IDs to remove the user from (exact match):")
        for e_id in event_ids:
            print(f" - {e_id}")
        chosen = input("Event IDs to remove: ").strip()
        if not chosen:
            print("No events specified. Operation cancelled.")
            return
        else:
            # Validate input against known event_ids
            chosen_list = [e.strip() for e in chosen.split(",")]
            events_to_remove = [e for e in chosen_list if e in event_ids]

        if not events_to_remove:
            print("No valid event IDs to remove. Operation cancelled.")
            return

    # Build the new list of events after removal
    new_events = [ev for ev in events if ev.get('event_id') not in events_to_remove]

    # Preview
    print(f"\n{'[DRY RUN] ' if dry_run else ''}The following actions will be taken:")
    for e_id in events_to_remove:
        print(f" - Remove user '{phone_number}' from event '{e_id}' (collection 'AOI_{e_id}').")

    if not new_events:
        print(f" - Delete user '{phone_number}' from 'user_event_tracking' (no events left).")
    else:
        print(f" - Update user '{phone_number}' in 'user_event_tracking' to remove events: {events_to_remove}.")

    if dry_run:
        print("\nThis is a dry run. No changes have been made.")
        proceed = input("Do you want to proceed with actual deletion? Type 'yes' to confirm: ").strip().lower()
        if proceed != 'yes':
            print("No changes have been made.")
            return
        else:
            # Perform actual deletion by calling the function recursively with dry_run=False
            delete_users_by_phone_number(user_data, dry_run=False)
    else:
        # Actual deletion/updates
        # 1. Delete user from each chosen event collection
        for e_id in events_to_remove:
            print(f"Deleting user '{phone_number}' from event collection 'AOI_{e_id}'...")
            db.collection(f'AOI_{e_id}').document(phone_number).delete()

        # 2. If no events left, remove the entire user doc
        if not new_events:
            print(f"Deleting user '{phone_number}' entirely from 'user_event_tracking'...")
            db.collection('user_event_tracking').document(phone_number).delete()
        else:
            # 3. Otherwise, just update the user doc
            print(f"Updating user '{phone_number}' to remove events {events_to_remove}...")
            db.collection('user_event_tracking').document(phone_number).update({'events': new_events})

        print("\nDeletion/Update completed.")


# ------------------------------------------------------------------------------
# Main
# ------------------------------------------------------------------------------
def main():
    # Retrieve user-event tracking data
    user_data, event_users, users_with_multiple_events = get_user_event_tracking_data()

    # Option 1: Delete by last activity date
    delete_by_activity = input("\nDo you want to delete users based on last activity date? (yes/no): ").strip().lower()
    if delete_by_activity == 'yes':
        delete_users_by_criteria(user_data, dry_run=True)

    # Option 2: Delete by event ID
    delete_by_event = input("\nDo you want to delete users by event ID? (yes/no): ").strip().lower()
    if delete_by_event == 'yes':
        delete_users_by_event_id(user_data, dry_run=True)

    # Option 3: Delete a specific phone number from all or some events
    delete_by_phone = input("\nDo you want to delete a phone number from all or some events? (yes/no): ").strip().lower()
    if delete_by_phone == 'yes':
        delete_users_by_phone_number(user_data, dry_run=True)


if __name__ == '__main__':
    main()
