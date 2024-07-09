import json
import boto3
from googleapiclient.discovery import build
from firebase_admin import firestore
from google.oauth2 import service_account
import urllib.parse
import config
from firebase_utils import initialize_firebase, get_all_user_inputs
from google_sheets_utils import fetch_google_sheets_data
from s3_utils import upload_csv_to_s3
from email_utils import construct_email_body_html, send_email

def lambda_handler(event, context):
    app = initialize_firebase(config.FIREBASE_CREDENTIALS)
    db = firestore.client(app=app)
    s3_client = boto3.client('s3')
    ses_client = boto3.client('ses', region_name=config.SES_REGION)

    whatsapp_data = get_all_user_inputs(db)
    
    # Download service account key from S3
    local_file_name = '/tmp/' + config.GOOGLE_SHEET_KEY_FILE
    s3_client.download_file(config.BUCKET_NAME, config.GOOGLE_SHEET_KEY_FILE, local_file_name)

    google_credentials = service_account.Credentials.from_service_account_file(local_file_name, scopes=config.SCOPES)
    service = build('sheets', 'v4', credentials=google_credentials)

    rows = fetch_google_sheets_data(service, config.SPREADSHEET_ID, config.RANGE_NAME)

    if not rows:
        print("No data found.")
        return {'statusCode': 404, 'body': json.dumps('No data found')}

    header_row_index, group_index = identify_group_column(rows)

    if group_index == -1:
        print("Group number column not found.")
        return {'statusCode': 404, 'body': json.dumps('Group number column not found')}

    grouped_data = group_data_by_column(rows, header_row_index, group_index)

    urls_dict = {}
    for group_number, data in grouped_data.items():
        csv_content = generate_csv_content(data, whatsapp_data)
        url = upload_csv_to_s3(s3_client, config.S3_BUCKET_NAME, group_number, csv_content)
        urls_dict[f"group_{group_number}.csv"] = url

    email_body = construct_email_body_html(urls_dict)
    send_email(ses_client, config.EMAIL_SENDER, event['queryStringParameters']['email'], "AI Conference WhatsApp Dialogues", email_body)

    return {
        'statusCode': 200,
        'body': json.dumps('Data processed and email sent successfully')
    }

def identify_group_column(rows):
    header_row_index = -1
    group_index = -1
    for index, row in enumerate(rows):
        if 'Group number' in row:
            header_row_index = index
            group_index = row.index('Group number')
            break
    return header_row_index, group_index

def group_data_by_column(rows, header_row_index, group_index):
    grouped_data = {}
    for row in rows[header_row_index + 1:]:
        if len(row) > group_index:
            group_number = row[group_index]
            if group_number not in grouped_data:
                grouped_data[group_number] = []
            grouped_data[group_number].append(row)
    return grouped_data

def generate_csv_content(data, whatsapp_data):
    output = StringIO()
    writer = csv.writer(output)
    writer.writerow(['Comment-ID', 'Interview', 'Comment-Body'])
    for index, item in enumerate(data):
        phone_number = item[3] if len(item) > 3 else "Data Missing"
        messages = " ".join(whatsapp_data.get(phone_number, ["Data Missing"]))  # Retrieve messages or handle missing data
        writer.writerow([index + 1, phone_number, messages])
    return output.getvalue()
