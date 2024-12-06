from datetime import datetime

def get_user_event_tracking_data(db):
    """Fetch all documents from 'user_event_tracking' collection."""
    user_event_tracking_ref = db.collection('user_event_tracking')
    docs = user_event_tracking_ref.stream()

    user_data = {}
    event_users = {}
    users_with_multiple_events = []

    print("Fetching user-event tracking data...")

    for doc in docs:
        user_id = doc.id
        data = doc.to_dict()
        events = data.get('events', [])
        awaiting_event_id = data.get('awaiting_event_id', False)
        current_event_id = data.get('current_event_id', None)

        # Compute last_activity from event timestamps
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

    print(f"\nTotal number of different events: {len(event_users)}")
    print("\nNumber of users in each event:")
    for event_id, users in event_users.items():
        print(f"Event '{event_id}': {len(users)} users")

    return user_data, event_users, users_with_multiple_events
