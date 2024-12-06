# AOI Cloud Data Extraction Service

This repository contains a robust AWS Lambda function integrated with Firebase, Google APIs, and AWS services (S3, SES) to extract user data from Firestore collections, generate dynamic CSV files, upload them to S3, and send download links via email. The project enables efficient data retrieval, transformation, and distribution in a secure and automated manner.

---

## Features

1. **AWS Lambda Integration**:
   - Deployed as an AWS Lambda function for serverless data processing.
   - Handles event-based triggers with query parameters for customization.

2. **Firestore Data Extraction**:
   - Retrieves and processes user data from Firestore collections.
   - Excludes unnecessary fields and dynamically handles varying data structures.

3. **Dynamic CSV Generation**:
   - Generates CSV files with headers and fields based on Firestore data.
   - Supports customizable and dynamic data extraction.

4. **S3 Integration**:
   - Uploads generated CSV files to an S3 bucket.
   - Provides secure, time-limited presigned URLs for downloading files.

5. **SES Email Notification**:
   - Sends HTML emails with download links for the generated CSV files.
   - Customizable email templates for professional communication.

6. **Cloud-Native**:
   - Fully compatible with AWS services and Cloud9 EC2 development environments.

---

## Deployment Instructions

### Step 1: Set Up Your Cloud9 EC2 Instance

1. **Create a Cloud9 EC2 Environment**:
   - Go to the AWS Management Console and navigate to the Cloud9 service.
   - Create a new environment with a t3.micro EC2 instance.
   - Ensure the instance has permissions for S3, SES, and Lambda.

2. **Install Required Dependencies**:
   - Update the system and install necessary Python libraries:
     ```bash
     sudo yum update -y
     sudo yum install python3-pip -y
     pip3 install boto3 google-api-python-client google-auth fastapi uvicorn
     ```

3. **Clone the Repository**:
   - Clone this repository to your Cloud9 instance:
     ```bash
     git clone <repository_url>
     cd <repository_folder>
     ```

---

### Step 2: Configure Firebase and AWS

1. **Setup Firebase**:
   - Download your Firebase Admin SDK JSON credentials.
   - Place the file in the project directory (e.g., `firebase_credentials.json`).
   - Update the `config.FIREBASE_CREDENTIALS` path in the code to point to your credentials.

2. **Create an S3 Bucket**:
   - Go to the S3 console and create a new bucket (e.g., `aoiaiwhatsappdata2`).
   - Enable public access if required for presigned URLs.

3. **Set Up SES**:
   - Verify your email addresses (sender and recipient) in SES.
   - Ensure SES is in production mode to send emails without sandbox restrictions.

4. **Configure API Gateway**:
   - Deploy the Lambda function using API Gateway to expose it as an HTTP endpoint.
   - Add query parameters (`email` and `collections`) to the API Gateway configuration.

---

### Step 3: Deploy the Lambda Function

1. **Create a Deployment Package**:
   - Zip the project files and dependencies into a deployment package:
     ```bash
     zip -r lambda_function.zip .
     ```

2. **Upload to AWS Lambda**:
   - Navigate to the AWS Lambda console.
   - Create a new function and upload the `lambda_function.zip` file.
   - Set the handler to `lambda_function.lambda_handler`.

3. **Set Environment Variables**:
   - Configure the following environment variables in the Lambda function:
     - `FIREBASE_CREDENTIALS`: Path to Firebase credentials.
     - `S3_BUCKET_NAME`: Name of the S3 bucket.
     - `SES_EMAIL_SENDER`: Email address for SES notifications.

4. **Test the Lambda Function**:
   - Use the AWS Lambda console to test the function with the following input:
     ```json
     {
       "queryStringParameters": {
         "email": "recipient@example.com",
         "collections": "collection1,collection2"
       }
     }
     ```

---

### Step 4: Use the API Gateway URL

1. **API Gateway URL Example**:
   - Use the deployed API Gateway URL to trigger the Lambda function:
     ```
     https://<api-gateway-url>?email=recipient@example.com&collections=collection1,collection2
     ```

2. **Validate the Workflow**:
   - Verify that the specified Firestore collections are processed.
   - Check your email for download links to the generated CSV files.

---

## Code Walkthrough

### 1. **Firestore Data Retrieval**:
   - Function: `get_collection_data`
   - Fetches all documents from a Firestore collection while filtering unnecessary fields.

### 2. **User Input Processing**:
   - Function: `get_all_user_inputs`
   - Dynamically extracts user messages and additional fields.

### 3. **CSV Generation**:
   - Function: `generate_dynamic_csv`
   - Creates CSV files with headers and rows dynamically based on Firestore data.

### 4. **S3 Upload and URL Generation**:
   - Uploads CSV files to S3 and generates presigned URLs for secure downloads.

### 5. **Email Notifications**:
   - Function: `construct_email_body_html`
   - Sends an HTML email with download links to the user.

---

## Advanced Configuration

### **Customize Email Template**
- Modify the `construct_email_body_html` function to change the look and feel of the email.

### **Adjust S3 Permissions**
- Use bucket policies or IAM roles to restrict access to the uploaded files.

### **Enable Debugging**
- Add logging statements for detailed debugging during development:
   ```python
   import logging
   logging.basicConfig(level=logging.DEBUG)
   ```

---

## Security Considerations

1. **Secure Firebase Credentials**:
   - Store Firebase Admin SDK credentials in AWS Secrets Manager or environment variables.

2. **Limit API Access**:
   - Restrict API Gateway access to authorized users via IAM or API keys.

3. **Presigned URL Expiration**:
   - Configure shorter expiration times for presigned URLs if sensitive data is involved.

---


## Contact

For any questions or assistance, feel free to reach out to **[info@talktothecity.org](mailto:emre@objective.is)**.