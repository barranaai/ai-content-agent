import os
import os.path
import pickle
from flask import Flask, request, jsonify
from flask_cors import CORS
from dotenv import load_dotenv
from openai import OpenAI
from google.auth.transport.requests import Request
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

load_dotenv()

print(f"Environment variables loaded: {os.environ.get('OPENAI_API_KEY', 'NOT_FOUND')[:10]}...")

if "OPENAI_API_KEY" not in os.environ or not os.environ["OPENAI_API_KEY"]:
    print("OpenAI API key not found in environment variables")
    # Don't raise exception, let the app start and handle it in the endpoint

client = OpenAI()

SCOPES = ['https://www.googleapis.com/auth/spreadsheets.readonly']

app = Flask(__name__)
CORS(app, origins=['http://localhost:3000', 'http://localhost:3001'])  # Enable CORS for specific origins

def get_google_sheets_service():
    creds = None
    if os.path.exists('token.pickle'):
        with open('token.pickle', 'rb') as token:
            creds = pickle.load(token)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file('client_secret.json', SCOPES)
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
            if len(row) >=2:
                platform = row[0]
                prompt_text = row[1]
                prompts[platform] = prompt_text
    return prompts

@app.route('/api/topics')
def api_get_topics():
    service = get_google_sheets_service()
    topics_sheet_id = '12qFx-0Si0-g8Hp_yq7sIm7I5gJiACaOaLep04dSYC_U'
    topics = fetch_topics(service, topics_sheet_id)
    return jsonify(topics)

@app.route('/api/platform-prompts')
def api_get_prompts():
    service = get_google_sheets_service()
    prompts_sheet_id = '1MIS7Nl1AdTy7mjwKaIDCBV820bXZteHvdIxo8WETYnc'
    prompts = fetch_prompts(service, prompts_sheet_id)
    return jsonify(prompts)

@app.route('/api/generate-content', methods=['POST'])
def api_generate_content():
    try:
        data = request.json
        if not data:
            return jsonify({"error": "No JSON data provided"}), 400
            
        topic = data.get('topic')
        description = data.get('description')
        platforms = data.get('platforms', [])
        prompts = data.get('prompts', {})
        
        print(f"Received request - Topic: {topic}, Platforms: {platforms}")
        
        if not topic or not description or not platforms or not prompts:
            return jsonify({"error": "Missing required data"}), 400

        # Check if OpenAI API key is set
        api_key = os.environ.get("OPENAI_API_KEY")
        print(f"OpenAI API Key present: {bool(api_key)}")
        print(f"API Key value: {api_key[:10] if api_key else 'None'}...")
        
        if not api_key or api_key == "your_openai_api_key_here":
            return jsonify({"error": "OpenAI API key not configured. Please set OPENAI_API_KEY in .env file"}), 500

        results = {}
        for platform in platforms:
            prompt_template = prompts.get(platform)
            if not prompt_template:
                results[platform] = "No prompt template found."
                continue
            full_prompt = prompt_template.replace("{description}", description)
            
            print(f"Generating content for {platform}...")
            response = client.chat.completions.create(
                model="gpt-4",
                messages=[{"role": "user", "content": full_prompt}],
                max_tokens=800,
                temperature=0.7
            )
            results[platform] = response.choices[0].message.content
            
        return jsonify(results)
    except Exception as e:
        print(f"Error in generate-content: {str(e)}")
        return jsonify({"error": f"Internal server error: {str(e)}"}), 500

if __name__ == '__main__':
    app.run(port=5050, debug=True)
