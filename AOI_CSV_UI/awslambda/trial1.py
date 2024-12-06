

import json
import boto3
from google.oauth2 import service_account
from googleapiclient.discovery import build
from io import StringIO
import csv
import urllib.parse
from firebase_admin import credentials, firestore, initialize_app, get_app
import config

def get_collection_data(db, collection_name):
    """ Fetch all documents from the Firestore collection, excluding the 'info' document """
    collection_ref = db.collection(collection_name)
    docs = collection_ref.stream()
    data = {}
    
    for doc in docs:
        doc_data = doc.to_dict()
        
        # Skip the 'info' document
        if doc.id == 'info':
            continue

        # Filter out any empty fields
        filtered_data = {key: value for key, value in doc_data.items() if value}
        data[doc.id] = filtered_data

    return data

# def get_all_user_inputs(db, collection_name):
#     """ Fetch all user messages (excluding bot responses) across documents in the collection, and any additional fields """
#     try:
#         collection_data = db.collection(collection_name).stream()
#         all_messages = {}

#         for doc in collection_data:
#             # Skip the 'info' document
#             if doc.id == 'info':
#                 continue
            
#             doc_data = doc.to_dict()
#             phone_number = doc.id  # The document ID is the phone number

#             # Extract the user messages, skipping bot responses
#             user_messages = [
#                 interaction.get('message', '') for interaction in doc_data.get('interactions', []) 
#                 if isinstance(interaction, dict) and 'message' in interaction and 'response' not in interaction
#             ]

#             # Clean the messages by joining them without brackets/quotes
#             cleaned_messages = " ".join(user_messages).replace('[', '').replace(']', '').replace("'", "")
            
#             # Fetch the name (if available) and any additional fields
#             name = doc_data.get('name', '')  # The 'name' field
#             other_fields = {key: value for key, value in doc_data.items() if key not in ['interactions', 'name']}
            
#             # Store all fields dynamically, including 'name', 'comment-body', and others
#             all_messages[phone_number] = {
#                 'name': name,
#                 'comment-body': cleaned_messages,
#                 **other_fields  # Merge any other fields dynamically
#             }
#         return all_messages
#     except Exception as e:
#         print(f"An error occurred: {e}")


def get_all_user_inputs(db, collection_name):
    """ Fetch all user messages (excluding bot responses) across documents in the collection, and any additional fields """
    try:
        collection_data = db.collection(collection_name).stream()
        all_messages = {}

        for doc in collection_data:
            # Skip the 'info' document
            if doc.id == 'info':
                continue
            
            doc_data = doc.to_dict()
            phone_number = doc.id  # The document ID is the phone number

            # Extract the user messages, skipping bot responses
            user_messages = [
                interaction.get('message', '') for interaction in doc_data.get('interactions', []) 
                if isinstance(interaction, dict) and 'message' in interaction and 'response' not in interaction
            ]

            # Clean the messages by joining them without brackets/quotes
            cleaned_messages = " ".join(user_messages).replace('[', '').replace(']', '').replace("'", "")
            
            # Fetch the name (if available) and any additional fields, excluding unwanted fields
            name = doc_data.get('name', '')  # The 'name' field
            other_fields = {key: value for key, value in doc_data.items() 
                            if key not in ['interactions', 'name', 'limit_reached_notified', 'event_id']}
            
            # Store all fields dynamically, including 'name', 'comment-body', and others
            all_messages[phone_number] = {
                'name': name,
                'comment-body': cleaned_messages,
                **other_fields  # Merge any other fields dynamically
            }
        return all_messages
    except Exception as e:
        print(f"An error occurred: {e}")



def generate_dynamic_csv(all_messages):
    """ Generate CSV content dynamically from all fields in user messages """
    output = StringIO()
    all_keys = set()

    # First, find all unique keys across all documents (e.g., 'name', 'comment-body', 'unique_id', etc.)
    for phone_number, doc_data in all_messages.items():
        all_keys.update(doc_data.keys())

    # Write headers dynamically based on the keys found
    writer = csv.writer(output)
    headers = ['comment-id'] + sorted(all_keys)  # Include all unique field names dynamically
    writer.writerow(headers)

    # Write each row with dynamic values
    index = 1
    for phone_number, doc_data in all_messages.items():
        row = [index]  # comment-id
        row += [doc_data.get(key, '') for key in sorted(all_keys)]  # Values for each key (e.g., 'name', 'comment-body', 'unique_id', etc.)
        writer.writerow(row)
        index += 1

    return output.getvalue()  # Return CSV content as a string


def construct_email_body_html(csv_urls):
    email_body = """
    <html>
        <head>
            <style>
                body { 
                    font-family: 'Helvetica Neue', Helvetica, Arial, sans-serif; 
                    margin: 0; padding: 0; 
                    background-color: #f0f3f5; 
                    color: #1c1e21; 
                }
                .container { 
                    max-width: 600px; 
                    margin: 0 auto; 
                    background-color: #ffffff; 
                    padding: 40px; 
                    border-radius: 8px; 
                    box-shadow: 0 4px 20px rgba(0, 0, 0, 0.1); 
                }
                .header { 
                    text-align: center; 
                    padding-bottom: 30px; 
                    border-bottom: 1px solid #e6e6e6; 
                }
                .header img { 
                    max-width: 120px; 
                    margin-bottom: 20px;
                }
                h1 { 
                    font-size: 26px; 
                    color: #1c1e21; 
                    margin-bottom: 20px;
                }
                p { 
                    font-size: 16px; 
                    line-height: 1.6; 
                    color: #4a4a4a; 
                }
                .button { 
                    display: inline-block; 
                    padding: 12px 24px; 
                    margin: 20px 0; 
                    font-size: 16px; 
                    color: #ffffff; 
                    background-color: #007BFF; 
                    text-decoration: none; 
                    border-radius: 5px; 
                    transition: background-color 0.3s ease;
                }
                .button:hover { 
                    background-color: #0056b3; 
                }
                .collection { 
                    text-align: center; 
                    margin: 30px 0; 
                }
                .footer { 
                    margin-top: 50px; 
                    padding-top: 20px; 
                    border-top: 1px solid #e6e6e6; 
                    text-align: center; 
                    font-size: 14px; 
                    color: #999999; 
                }
                .useful-links a { 
                    text-decoration: none; 
                    color: #007BFF; 
                    font-size: 16px; 
                    margin: 0 10px; 
                }
                .unsubscribe { 
                    color: #999999; 
                    text-decoration: none; 
                    font-size: 12px; 
                }
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <img src="https://aoiaiwhatsappdata2.s3.amazonaws.com/AOIlogo.jpg" alt="Company Logo">
                    <h1>Your Requested Data Collections</h1>
                </div>
                <p>Dear Valued Partner,</p>
                <p>We are pleased to provide you with the data collections you requested. Please use the buttons below to download each dataset individually:</p>
    """

    for collection_name, url in csv_urls.items():
        email_body += f"""
                <div class="collection">
                    <h2>{collection_name}.csv</h2>
                    <a href="{url}" class="button">Download {collection_name}</a>
                </div>
        """

    email_body += """
                <p>If you have any questions or need further assistance, please do not hesitate to reach out to our support team.</p>
                <div class="footer">
                    <div class="useful-links">
                        <a href="https://ai.objectives.institute/whitepaper">Whitepaper</a> | 
                        <a href="https://www.wired.com/story/peter-eckersley-ai-objectives-institute/">AOI Legacy</a> | 
                        <a href="https://ai.objectives.institute/projects">Programs</a>
                    </div>
                    <p>&copy; 2024 AOI Emre Turan. All rights reserved.</p>
                    <a href="#" class="unsubscribe">Unsubscribe</a>
                </div>
            </div>
        </body>
    </html>
    """

    return email_body

def lambda_handler(event, context):
    # Uncomment below for local testing
    event = {
        'queryStringParameters': {
            'email': 'emreturan1269@gmail.com',
            'collections': 'AOI_TEST1,AOI_QuestionPro,whatsapp_conversations1'
        }
    }

    try:
        app = get_app()
    except ValueError:
        # Initialize Firebase if app does not exist
        firebase_cred = config.FIREBASE_CREDENTIALS
        cred = credentials.Certificate(firebase_cred)
        app = initialize_app(cred)

    db = firestore.client(app=app)
    s3_client = boto3.client('s3')
    ses_client = boto3.client('ses', region_name='us-east-1')

    # Get email and collections from query parameters
    email_recipient = event['queryStringParameters'].get('email')
    collections_param = event['queryStringParameters'].get('collections', '')
    collection_names = [name.strip() for name in collections_param.split(',') if name.strip()]

    if not email_recipient or not collection_names:
        return {
            'statusCode': 400,
            'body': json.dumps('Email and collections parameters are required')
        }

    csv_urls = {}
    bucket_name = 'aoiaiwhatsappdata2'
    region_name = 'us-east-1'

    # Process each collection in the list
    for collection_name in collection_names:
        all_messages = get_all_user_inputs(db, collection_name)
    
        # Generate CSV content with dynamic fields
        csv_content = generate_dynamic_csv(all_messages)
        
        # Upload CSV to S3
        file_key = f'{collection_name}_user_messages.csv'
        s3_client.put_object(Bucket=bucket_name, Key=file_key, Body=csv_content)
    
        # Generate presigned URL
        url = s3_client.generate_presigned_url('get_object',
                                               Params={'Bucket': bucket_name,
                                                       'Key': file_key},
                                               ExpiresIn=3600)  # URL valid for 1 hour
    
        csv_urls[collection_name] = url

    # Compose email body with download links
    email_body = construct_email_body_html(csv_urls)

    email_sender = 'info@talktothecity.org'

    # Send email with the download links
    response = ses_client.send_email(
        Source=email_sender,
        Destination={'ToAddresses': [email_recipient]},
        Message={
            'Subject': {'Data': "Your Requested Data Collections"},
            'Body': {'Html': {'Data': email_body}}
        }
    )

    return {
        'statusCode': 200,
        'body': json.dumps('Data processed and email sent successfully')
    }


print(lambda_handler(None, None))
