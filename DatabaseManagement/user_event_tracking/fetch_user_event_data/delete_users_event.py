def delete_users_by_event_id(db, user_data, dry_run=True):
    """Delete users based on event ID."""
    event_id_to_delete = input("Enter the event ID: ").strip()
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

    print(f"{'[DRY RUN]' if dry_run else ''} Users affected by event ID:")
    for user_id in users_to_delete:
        print(f"- Deleting user '{user_id}'")
    for user_id, _ in users_to_update:
        print(f"- Updating user '{user_id}'")

    if dry_run:
        proceed = input("Proceed with deletion? Type 'yes': ").strip().lower()
        if proceed == 'yes':
            delete_users_by_event_id(db, user_data, dry_run=False)
    else:
        for user_id in users_to_delete:
            db.collection('user_event_tracking').document(user_id).delete()
        for user_id, new_events in users_to_update:
            db.collection('user_event_tracking').document(user_id).update({'events': new_events})
        print("Deletion completed.")
