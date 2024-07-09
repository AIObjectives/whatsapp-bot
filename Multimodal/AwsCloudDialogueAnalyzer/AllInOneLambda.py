

import json
import boto3
from google.oauth2 import service_account
from googleapiclient.discovery import build
from io import StringIO
import csv
import urllib.parse
from firebase_admin import credentials, firestore, initialize_app, get_app
import config

def lambda_handler(event, context):
    try:
        app = get_app()
    except ValueError:
        # Initialize Firebase if app does not exist
        firebase_cred = config.FIREBASE_CREDENTIALS
        cred = credentials.Certificate(firebase_cred)
        app = initialize_app(cred)

    db = firestore.client(app=app)
    s3_client = boto3.client('s3')
    ses_client = boto3.client('ses', region_name='us-west-1')

    # Fetch user messages from Firestore
    whatsapp_data = get_all_user_inputs(db)

    # Download service account key from S3
    BUCKET_NAME = '##'
    KEY = "##.json"
    local_file_name = '/tmp/' + KEY
    s3_client.download_file(BUCKET_NAME, KEY, local_file_name)

    # Set up Google Sheets API client
    scopes = ["https://www.googleapis.com/auth/drive", "https://www.googleapis.com/auth/drive.file", "https://www.googleapis.com/auth/spreadsheets"]
    google_credentials = service_account.Credentials.from_service_account_file(local_file_name, scopes=scopes)
    service = build('sheets', 'v4', credentials=google_credentials)

    # Fetch data from the spreadsheet
    spreadsheet_id = '##'
    range_name = 'A1:P'  # Adjust to fetch header row too
    request = service.spreadsheets().values().get(spreadsheetId=spreadsheet_id, range=range_name)
    response = request.execute()
    rows = response.get('values', [])

    if not rows:
        print("No data found.")
        return {'statusCode': 404, 'body': json.dumps('No data found')}

    # Identify the row containing 'Group number' header
    header_row_index = -1
    group_index = -1
    for index, row in enumerate(rows):
        if 'Group number' in row:
            header_row_index = index
            group_index = row.index('Group number')
            break

    if group_index == -1:
        print("Group number column not found.")
        return {'statusCode': 404, 'body': json.dumps('Group number column not found')}

    # Group data by 'Group number'
    grouped_data = {}
    for row in rows[header_row_index + 1:]:
        if len(row) > group_index:
            group_number = row[group_index]
            if group_number not in grouped_data:
                grouped_data[group_number] = []
            grouped_data[group_number].append(row)

    # Output CSV format for each group with messages from Firestore
    bucket_name = '##'
    region_name = '##'
    urls_dict = {}
    for group_number, data in grouped_data.items():
        output = StringIO()
        writer = csv.writer(output)
        writer.writerow(['comment-id', 'interview', 'comment-body'])
        for index, item in enumerate(data):
            # phone_number = item[3] if len(item) > 3 else ""
            # messages = " ".join(whatsapp_data.get(phone_number, [""]))  # Retrieve messages or handle missing data
            # writer.writerow([index + 1, phone_number, messages])
            
            name = item[2] if len(item) > 2 else ""  # Retrieve name
            phone_number = item[3] if len(item) > 3 else ""  # Ensure phone number is correctly referenced for fetching messages
            messages = " ".join(whatsapp_data.get(phone_number, [""]))  # Retrieve messages using phone number
            writer.writerow([index + 1, name, messages])  # Write name under 'interview' and messages under 'comment-body'
        
        csv_content = output.getvalue()
        file_key = f"group_{group_number}.csv"
        s3_client.put_object(Bucket=bucket_name, Key=file_key, Body=csv_content)
        encoded_file_key = urllib.parse.quote(file_key, safe='')
        url = f"https://{bucket_name}.s3.{region_name}.amazonaws.com/{encoded_file_key}"
        urls_dict[file_key] = url

    email_body = construct_email_body_html(urls_dict)
    email_sender = '##'
    email_recipient = event['queryStringParameters']['email']
    response = ses_client.send_email(
        Source=email_sender,
        Destination={'ToAddresses': [email_recipient]},
        Message={
            'Subject': {'Data': "AI Conference WhatsApp Dialogues"},
            'Body': {'Html': {'Data': email_body}}
        }
    )

    return {
        'statusCode': 200,
        'body': json.dumps('Data processed and email sent successfully')
    }

def get_all_user_inputs(db):
    """ Retrieve all user messages from Firestore across all documents in the 'whatsapp_conversations' collection """
    try:
        conversations = db.collection('whatsapp_conversations').stream()
        all_messages = {}
        for conversation in conversations:
            doc_data = conversation.to_dict()
            phone_number = conversation.id  # The document ID is the phone number
            user_messages = [interaction['message'] for interaction in doc_data.get('interactions', []) if 'message' in interaction]
            all_messages[phone_number] = user_messages
        return all_messages
    except Exception as e:
        print(f"An error occurred: {e}")

def construct_email_body_html(urls_dict):
    email_body = """
    <html>
        <head>
            <style>
                body { font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; margin: 0; padding: 0; color: #333; background-color: #f4f4f4; }
                .container { max-width: 600px; margin: auto; background: #fff; padding: 20px; border-radius: 5px; box-shadow: 0 0 10px rgba(0, 0, 0, 0.1); }
                h2 { color: #0366d6; text-align: center; }
                .link-title { margin-top: 20px; padding: 10px; background-color: #e9e9e9; border-left: 5px solid #0366d6; font-size: 18px; }
                .graph-link { text-decoration: none; color: #333; font-weight: bold; }
                .graph-link:hover { color: #0366d6; }
                .footer { margin-top: 30px; text-align: center; font-size: 14px; color: #666; }
            </style>
        </head>
        <body>
            <div class='container'>
                <h2>AI Conference WhatsApp Dialogues</h2>
    """
    for file_key, url in urls_dict.items():
        email_body += f"""
                <div class='link-title'>
                    <a href='{url}' class='graph-link' target='_blank'>{file_key.replace('_', ' ').title()}</a>
                </div>
        """
    email_body += """
                <div class='footer'>
                    <p>AOI Emre Turan - All rights reserved © 2024</p>
                </div>
            </div>
        </body>
    </html>
    """
    return email_body
