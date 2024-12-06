# Conference Management System

This project is a modular system designed to populate and manage different types of conferences in a **Firebase Firestore** database. It supports three distinct modes for hosting conferences:

1. **Listener Mode**: Focuses on passive data collection with minimal user interaction.
2. **Survey Mode**: Gathers structured feedback through predefined questions.
3. **Opened Mode**: Encourages free-form interactions for open-ended discussions.

The project leverages **Firebase Firestore** for data storage and allows most configurations to be managed through the Firebase UI, reducing the need for manual code adjustments.

---

## Features

### 1. **Three Conference Modes**
- **Listener Mode**:
  - Passive listening with minimal interaction.
  - Typically used for observing and recording discussions.
- **Survey Mode**:
  - Structured surveys with predefined questions.
  - Ideal for collecting actionable insights.
- **Opened Mode**:
  - Free-form discussions for open-ended topics.
  - Encourages creativity and broader engagement.

### 2. **Centralized Firebase Integration**
- **Firestore Database**:
  - All conference data is securely stored in Firebase Firestore.
  - Each conference mode creates its own collection for better organization.
- **Firebase UI**:
  - Most of the configurations, such as event details, questions, and settings, can be managed directly through the Firebase console.
  - Easily edit or update events without modifying code.

### 3. **Modular Architecture**
- Each conference mode is isolated in its own module, ensuring clean and maintainable code.
- Shared utilities are centralized in a `/shared` folder for reusability across modes.

### 4. **Scalability**
- The system is designed to handle multiple conferences simultaneously.
- Supports multilingual events with customizable settings.

---

## Project Structure

```
/project-root
│
├── /listener_mode           # Contains all files specific to Listener Mode
│   ├── __init__.py
│   ├── config.py
│   ├── initialize_listener.py
│   └── utils.py
│
├── /survey_mode             # Contains all files specific to Survey Mode
│   ├── __init__.py
│   ├── config.py
│   ├── initialize_survey.py
│   └── utils.py
│
├── /opened_mode             # Contains all files specific to Opened Mode
│   ├── __init__.py
│   ├── config.py
│   ├── initialize_opened.py
│   └── utils.py
│
├── /shared                  # Shared utilities and setup files
│   ├── __init__.py
│   ├── firebase_setup.py
│   ├── logger.py
│   ├── validators.py
│   └── constants.py
│
├── /tests                   # Test files for each module
│   ├── test_listener_mode.py
│   ├── test_survey_mode.py
│   ├── test_opened_mode.py
│   └── test_shared.py
│
├── main.py                  # Entry point for the application
├── requirements.txt         # Python dependencies
└── README.md                # Documentation for the project
```

---

## Installation

1. Clone the repository:
   ```bash
   git clone <repository_url>
   cd project-root
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Set up Firebase:
   - Add your Firebase credentials JSON file to the project.
   - Update the path in `shared/firebase_setup.py` to point to your credentials file.

---

## Usage

1. Run the main application:
   ```bash
   python main.py
   ```

2. Choose a mode:
   - The system will prompt you to select a mode (`listener`, `survey`, `opened`).
   - Based on your choice, the respective module will initialize the conference in Firestore.

3. Customize conference details:
   - Navigate to the **Firebase Firestore Console**.
   - Edit or update the `info` document under the corresponding conference collection (`Listener_<event_id>`, `Survey_<event_id>`, or `Opened_<event_id>`).
   - Fields such as event name, questions, bot personality, and more can be adjusted directly in the Firebase UI.

---

## Configuration

### Firebase Firestore
- **Database Structure**:
  - Each conference mode creates its own collection prefixed with the mode name (e.g., `Listener_<event_id>`).
  - The main event information is stored in the `info` document within each collection.

- **Customizable Fields in Firebase UI**:
  - `event_name`: The name of the event.
  - `event_date`: The date of the event.
  - `welcome_message`: Custom welcome messages for participants.
  - `questions`: For survey mode, you can directly update the list of questions in Firestore.
  - `languages`: Supported languages for the conference.

### Shared Utilities
- **Firebase Setup**: Centralized in `shared/firebase_setup.py`.
- **Logging**: Configured in `shared/logger.py` for standardized logs across modules.
- **Validation**: Input validation is handled in `shared/validators.py`.

---

## Customization via Firebase UI

The **Firebase Console** allows you to easily manage and update conference details without modifying the code. Here’s what you can do directly in Firebase:

1. **Edit Conference Details**:
   - Update fields such as `event_name`, `event_date`, `bot_topic`, and more in the `info` document.

2. **Add or Modify Questions** (Survey Mode):
   - Navigate to the `questions` field in the `info` document.
   - Add, edit, or remove questions as needed.

3. **Languages**:
   - Update the `languages` field to support additional languages for participants.

4. **Dynamic Prompts**:
   - Add custom prompts to the `bot_additional_prompts` field for better engagement.

### Advantages of Using Firebase UI
- No need to redeploy the application for most updates.
- Instant updates reflected for users without downtime.
- Simple and intuitive interface for non-technical team members.


---

## Future Enhancements

1. **Enhanced Firebase Integration**:
   - Automatically sync conference updates from Firestore to a front-end dashboard.

2. **Advanced Analytics**:
   - Add real-time analytics for conferences using Firebase Analytics.

3. **User Authentication**:
   - Implement Firebase Authentication for secure user access.

4. **Event Notifications**:
   - Enable notifications for upcoming events using Firebase Cloud Messaging.

---

## Contributing

1. Fork the repository.
2. Create a feature branch: `git checkout -b feature-name`.
3. Commit your changes: `git commit -m 'Add feature-name'`.
4. Push to the branch: `git push origin feature-name`.
5. Submit a pull request.

---


### Quick and Practical Setup

If you're looking for a **fast and straightforward method** to get started, you can use the scripts in the `MessyButPractical` folder. Simply update the **event ID** and other necessary details in the script files, then run them. Your changes will be instantly reflected in your **Firebase Firestore Database**.

