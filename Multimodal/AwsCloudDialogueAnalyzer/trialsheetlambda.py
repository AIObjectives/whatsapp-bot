import json
import boto3
from google.oauth2 import service_account
from googleapiclient.discovery import build
from io import StringIO
import csv

def lambda_handler(event, context):
    # Download service account key from S3
    s3 = boto3.resource('s3')
    BUCKET_NAME = '..'
    KEY = "...json"
    #KEY = "clientsecret.json"

    local_file_name = '/tmp/' + KEY
    s3.Bucket(BUCKET_NAME).download_file(KEY, local_file_name)

    # Set up Google Sheets API client
    scopes = ["https://www.googleapis.com/auth/drive", "https://www.googleapis.com/auth/drive.file", "https://www.googleapis.com/auth/spreadsheets"]
    credentials = service_account.Credentials.from_service_account_file(local_file_name, scopes=scopes)
    service = build('sheets', 'v4', credentials=credentials)

    # Fetch data from the spreadsheet
    spreadsheet_id = '...' ## this is unique for each spreadsheet!
    range_name = 'A1:F'  # Adjust to fetch header row too
    request = service.spreadsheets().values().get(spreadsheetId=spreadsheet_id, range=range_name)
    response = request.execute()
    rows = response.get('values', [])

  
 
    if not rows:
        print("No data found.")
        return {'statusCode': 404, 'body': json.dumps('No data found')}

    # Try to identify the row containing 'Group number' header
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

    print("Header Row found at index:", header_row_index)
    print("Group Number column index:", group_index)

    # Group data by 'Group number'
    grouped_data = {}
    for row in rows[header_row_index + 1:]:  # skip the header row
        if len(row) > group_index:  # check if the row has enough columns
            group_number = row[group_index]
            if group_number not in grouped_data:
                grouped_data[group_number] = []
            if len(row) > 3:  # Ensure there are enough columns to avoid IndexError
                grouped_data[group_number].append(row)

    # Output CSV format for each group to print statements for testing
    for group_number, data in grouped_data.items():
        print(f"Group {group_number}:")
        output = StringIO()
        writer = csv.writer(output)
        writer.writerow(['Name', 'Phone number'])  # Adjust headers as needed
        for item in data:
            # Check each item for sufficient length before accessing
            if len(item) > 3:
                writer.writerow([item[2], item[3]])  # Adjust indexes as per the content of rows
            else:
                writer.writerow(["Data Missing", "Data Missing"])  # Handle missing data
        # Print CSV content for each group
        print(output.getvalue())

print(lambda_handler(None,None))