

## FirestoreEventUserCleanup

A Python script for managing user data stored in a Firestore collection named `user_event_tracking`. This tool allows you to:

1. **View** user-event mappings and identify users associated with multiple events.  
2. **Delete** users based on last activity date (with a dry-run preview).  
3. **Delete** users by a specific event ID.  
4. **Remove** a single phone number (user) from one or multiple events, or from all events entirely.

### Features

- **Dry-Run Mode**  
  Preview which users or records would be deleted before committing changes to Firestore.

- **Selective Deletion**  
  - By last activity cutoff date.  
  - By event ID.  
  - By individual phone number (for one, multiple, or all events).

- **Automatic Cleanup**  
  If removing a user from all events, the script deletes their `user_event_tracking` document and cleans up associated event collections.

### Getting Started

1. **Clone This Repository**  
   ```bash
   git clone https://github.com/xx/FirestoreEventUserCleanup.git
   cd FirestoreEventUserCleanup
   ```

2. **Configure Firebase**  
   - Place your Firebase service account key (`.json` file) in the appropriate directory.  
   - Update the script to point to your service account file path.

3. **Install Dependencies**  
   ```bash
   pip install firebase-admin
   ```

4. **Run the Script**  
   ```bash
   python FirestoreEventUserCleanup.py
   ```
   You will be prompted through various cleanup options (last activity date, event ID, phone number removal). All actions have a preview (dry-run) mode to avoid accidental deletions.

### Usage Notes

- **Backup First:** Always back up your Firestore data before running this or any cleanup script.  
- **Check Dry-Run Output:** Carefully review the preview output before confirming a deletion.  
- **Proceed with Caution:** Deletions are permanent once confirmed!

### Contributing

Feel free to open issues or submit pull requests if you find bugs or want to suggest enhancements.

