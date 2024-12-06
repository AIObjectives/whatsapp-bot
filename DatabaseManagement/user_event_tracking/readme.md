# Firebase User Event Management Tool

This script provides utilities to manage user-event tracking data stored in a Firestore database. It includes functionality to analyze user data, determine inactive users, and clean up users based on various criteria.

---

## Features

1. **Fetch User-Event Data**:
   - Retrieves all user-event tracking data from the Firestore `user_event_tracking` collection.
   - Analyzes the data to:
     - Compute the last activity timestamp for each user.
     - Identify users associated with multiple events.
     - Count the number of users per event.

2. **Delete Users by Last Activity**:
   - Deletes users who have been inactive since a specified cutoff date.
   - Supports a dry-run mode to preview the deletions before executing.

3. **Delete Users by Event ID**:
   - Deletes users associated with a specific event ID.
   - Updates users to remove the event from their event list if they are part of other events.

4. **Dry-Run Mode**:
   - Allows you to preview the actions without making any actual changes to the database.

---

## Setup

### Prerequisites

1. **Python Environment**:
   - Python 3.8 or later.
   - Required libraries:
     - `firebase-admin`
     - `google-cloud-firestore`
   - Install dependencies using:
     ```bash
     pip install -r requirements.txt
     ```

2. **Firebase Configuration**:
   - Obtain a Firebase Admin SDK service account key and save it locally (e.g., `aoiwhatsappbot-firebase-adminsdk.json`).
   - Update the script with the correct path to your service account key:
     ```python
     cred = credentials.Certificate('/path/to/your/service-account-key.json')
     ```

3. **Firestore Database**:
   - Ensure you have a `user_event_tracking` collection in your Firestore database.

---

## Usage

### 1. Fetch User-Event Tracking Data

The script analyzes the `user_event_tracking` collection and provides:
- A summary of all events and their associated users.
- Details of users with multiple events.
- Last activity timestamps for each user.

### 2. Delete Users by Last Activity

- Prompts for a cutoff date (in `YYYY-MM-DD` format) to select inactive users.
- In dry-run mode, previews the users that would be deleted without making changes.
- Switch to actual deletion mode after confirming the dry-run results.

### 3. Delete Users by Event ID

- Prompts for an event ID to identify users associated with the event.
- Removes the event from user data:
  - If the user has no remaining events, they are deleted.
  - If the user has other events, their data is updated to exclude the specified event.
- Supports a dry-run mode for previewing changes.

---

## Script Flow

1. **Initialization**:
   - The Firebase Admin SDK is initialized to connect to the Firestore database.

2. **Main Operations**:
   - Fetch user-event data and print summary information.
   - Prompt for deletion actions:
     - Delete users based on inactivity.
     - Delete users based on an event ID.

3. **Dry-Run Safety**:
   - For deletion operations, the script first runs in dry-run mode.
   - Allows you to confirm actions before making changes to the database.

---

## How to Run

1. Clone the repository and navigate to the script directory.

2. Run the script:
   ```bash
   python <script_name>.py
   ```

3. Follow the interactive prompts to:
   - View user-event data.
   - Delete users based on inactivity or event ID.

---

## Key Functions

### 1. `get_user_event_tracking_data()`
- Retrieves and summarizes user-event data.
- Computes the last activity for each user.

### 2. `delete_users_by_criteria(user_data, dry_run=True)`
- Deletes users inactive before a specified date.
- Parameters:
  - `user_data`: Dictionary of user-event tracking data.
  - `dry_run`: Preview changes without making actual deletions.

### 3. `delete_users_by_event_id(user_data, dry_run=True)`
- Deletes or updates users based on a specific event ID.
- Parameters:
  - `user_data`: Dictionary of user-event tracking data.
  - `dry_run`: Preview changes without making actual deletions.

### 4. `main()`
- Orchestrates the script flow:
  - Fetches user-event data.
  - Provides options to delete users by criteria or event ID.

---

## Example Output

### Fetching User-Event Data
```
Fetching user-event tracking data...

Total number of different events: 5

Number of users in each event:
Event 'event1': 15 users
Event 'event2': 10 users

Total number of users with more than one event: 3

Users with more than one event:
User 'user1' is in events: ['event1', 'event2']
```

### Dry Run for Deletion
```
[DRY RUN] Users that would be deleted based on the criteria:
- User 'user1'
- User 'user3'

Total users that would be deleted: 2

This is a dry run. No changes have been made.
```

---

## Notes

- **Error Handling**:
  - The script validates date formats and ensures safe deletion with confirmation prompts.
  - Handles invalid or missing data gracefully.

- **Scalability**:
  - Designed to handle large datasets with efficient querying and processing.

- **Customization**:
  - Modify deletion criteria or event handling logic to fit your specific requirements.

---

