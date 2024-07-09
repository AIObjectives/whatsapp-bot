def fetch_google_sheets_data(service, spreadsheet_id, range_name):
    request = service.spreadsheets().values().get(spreadsheetId=spreadsheet_id, range=range_name)
    response = request.execute()
    return response.get('values', [])
