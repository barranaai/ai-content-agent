import os
import pickle
import json
from google.auth.transport.requests import Request
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

SCOPES = ['https://www.googleapis.com/auth/spreadsheets.readonly']

def create_client_secret_file():
    """Create client_secret.json from environment variable"""
    client_secret_content = os.environ.get('GOOGLE_CLIENT_SECRET')
    if not client_secret_content:
        raise Exception("GOOGLE_CLIENT_SECRET environment variable not set")
    
    # Write the content to a temporary file
    with open('client_secret.json', 'w') as f:
        f.write(client_secret_content)
    
    return 'client_secret.json'

def get_google_sheets_service():
    creds = None
    
    # Create client_secret.json from environment variable
    client_secret_file = create_client_secret_file()
    
    if os.path.exists('token.pickle'):
        with open('token.pickle', 'rb') as token:
            creds = pickle.load(token)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(client_secret_file, SCOPES)
            creds = flow.run_local_server(port=8080)
        with open('token.pickle', 'wb') as token:
            pickle.dump(creds, token)
    service = build('sheets', 'v4', credentials=creds)
    return service

def fetch_topics(service, sheet_id):
    RANGE_NAME = 'Sheet1!A2:B100'
    result = service.spreadsheets().values().get(spreadsheetId=sheet_id, range=RANGE_NAME).execute()
    values = result.get('values', [])
    topics = []
    if values:
        for row in values:
            topic = row[0] if len(row) > 0 else ""
            description = row[1] if len(row) > 1 else ""
            topics.append({"topic": topic, "description": description})
    return topics

def fetch_prompts(service, sheet_id):
    PROMPTS_RANGE = 'Sheet1!A2:B20'
    result = service.spreadsheets().values().get(spreadsheetId=sheet_id, range=PROMPTS_RANGE).execute()
    values = result.get('values', [])
    prompts = {}
    if values:
        for row in values:
            if len(row) >= 2:
                platform = row[0]
                prompt_text = row[1]
                prompts[platform] = prompt_text
    return prompts
