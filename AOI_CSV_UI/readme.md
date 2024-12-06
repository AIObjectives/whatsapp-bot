# FastAPI CSV Extraction Application

This project is a FastAPI-based web application designed to trigger an AWS API Gateway for generating CSV files based on user inputs. The application provides a simple HTML form for collecting user credentials and interacting with the AWS API Gateway. 

---

## Features

1. **HTML Form**:
   - A user-friendly form built with Jinja2 templates.
   - Collects user email, username, and password.

2. **Password Validation**:
   - Ensures only authorized users can trigger the API using a hardcoded password (for now).

3. **AWS API Gateway Integration**:
   - Formats API requests dynamically using user-provided data (email and username as collection name).
   - Sends GET requests to an AWS API Gateway endpoint to initiate CSV extraction.

4. **Error Handling**:
   - Provides feedback for invalid passwords.
   - Displays error messages for failed API calls or unexpected issues.

---

## Application Flow

1. User visits the form at the root endpoint (`/`).
2. The user fills in their:
   - **Email**
   - **Username**
   - **Password**
3. On form submission:
   - The password is validated against a hardcoded value.
   - If valid, a collection name is created using the username.
   - The application triggers the AWS API Gateway with the email and collection name.
   - The user is notified of success or failure.

---

## Endpoints

### 1. **Root Endpoint (`/`)**
- **Method**: `GET`
- **Description**: Displays the HTML form for user input.
- **Response**: Renders the `style_final.html` template.

### 2. **Form Submission Endpoint (`/submit`)**
- **Method**: `POST`
- **Parameters**:
  - `email`: User's email address (required).
  - `username`: Username for identifying the collection (required).
  - `password`: Password for validation (required).
- **Functionality**:
  - Validates the password.
  - Formats the AWS API Gateway URL using the email and username.
  - Sends a GET request to the AWS API.
  - Returns success or error messages based on the API response.

---

## Files and Directories

- **`app.py`**: The main FastAPI application code.
- **`templates/style_final.html`**: The Jinja2 template for rendering the HTML form and displaying messages.

---

## Setup and Installation

### Prerequisites
- Python 3.8 or later
- Virtual environment (optional but recommended)
- Required libraries:
  - `fastapi`
  - `jinja2`
  - `requests`
  - `uvicorn`

### Steps

1. **Clone the Repository**:
   ```bash
   git clone <repository_url>
   cd <repository_folder>
   ```

2. **Install Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Run the Application**:
   ```bash
   python app.py
   ```

4. **Access the Application**:
   - Open your browser and navigate to:
     ```
     http://localhost:8000
     ```

---

## Configuration

- **Hardcoded Password**:
  - The password for validation is currently hardcoded as `xxxx`.
  - You can change it by modifying the `HARD_CODED_PASSWORD` variable in `app.py`.

- **AWS API Gateway**:
  - The API endpoint is defined in `AWS_API_URL_TEMPLATE`. Update it with your specific AWS API Gateway URL:
    ```python
    AWS_API_URL_TEMPLATE = "https://your-api-gateway-url?email={email}&collections={collection}"
    ```

---

## Error Handling

- **Invalid Password**:
  - Displays an error message: *"Invalid password, please try again."*

- **Failed API Requests**:
  - Handles network issues and invalid responses.
  - Displays specific error messages for debugging.

- **Form Input Errors**:
  - Ensure all fields are filled before submission to avoid errors.

---

## Example Workflow

1. Open the app in the browser.
2. Fill out the form:
   - Email: `user@example.com`
   - Username: `test_collection`
   - Password: `xxx`
3. Submit the form:
   - On success: *"API triggered successfully. Check your email for the CSV file."*
   - On failure: Displays an error message indicating what went wrong.

---

## Notes

- **Security**:
  - Avoid using hardcoded passwords in production. Use a secure authentication mechanism.
  - Ensure HTTPS is enabled for secure communication with the AWS API Gateway.

- **Scalability**:
  - This application can be extended to support additional features like user authentication, enhanced form validation, or database integration.

- **Customization**:
  - Update the Jinja2 template (`style_final.html`) to match your application's branding and design requirements.

---

