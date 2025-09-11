import os
import os.path
import pickle
import openai
from google.auth.transport.requests import Request
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()  # take environment variables from .env file


# Load OpenAI API key from environment variable for security
if "OPENAI_API_KEY" not in os.environ or not os.environ["OPENAI_API_KEY"]:
    raise Exception("OpenAI API key not found in environment variables. Please set OPENAI_API_KEY in .env")
client = OpenAI()

SCOPES = ['https://www.googleapis.com/auth/spreadsheets.readonly']

def fetch_topics(service, sheet_id):
    RANGE_NAME = 'Sheet1!A2:B100'  # Your topics/descriptions range
    result = service.spreadsheets().values().get(
        spreadsheetId=sheet_id,
        range=RANGE_NAME
    ).execute()
    values = result.get('values', [])
    topics = []
    if not values:
        print("No topics/descriptions found.")
    else:
        for row in values:
            topic = row[0] if len(row) > 0 else ""
            description = row[1] if len(row) > 1 else ""
            topics.append({"topic": topic, "description": description})
    return topics

def fetch_prompts(service, sheet_id):
    PROMPTS_RANGE = 'Sheet1!A2:B20'  # Adjust as needed
    result = service.spreadsheets().values().get(
        spreadsheetId=sheet_id,
        range=PROMPTS_RANGE
    ).execute()
    values = result.get('values', [])
    prompts = {}
    if not values:
        print("No platform prompts found.")
    else:
        for row in values:
            if len(row) >= 2:
                platform = row[0]
                prompt_text = row[1]
                prompts[platform] = prompt_text
            else:
                print(f"Skipped incomplete row: {row}")
    return prompts

def generate_content(prompt_text):
    response = client.chat.completions.create(
        model="gpt-4",
        messages=[{"role": "user", "content": prompt_text}],
        max_tokens=800,
        temperature=0.7
    )
    return response.choices[0].message.content

def main():
    creds = None
    if os.path.exists('token.pickle'):
        with open('token.pickle', 'rb') as token:
            creds = pickle.load(token)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'client_secret.json', SCOPES)
            creds = flow.run_local_server(port=8080)
        with open('token.pickle', 'wb') as token:
            pickle.dump(creds, token)

    service = build('sheets', 'v4', credentials=creds)

    topics_sheet_id = '12qFx-0Si0-g8Hp_yq7sIm7I5gJiACaOaLep04dSYC_U'
    prompts_sheet_id = '1MIS7Nl1AdTy7mjwKaIDCBV820bXZteHvdIxo8WETYnc'

    topics = fetch_topics(service, topics_sheet_id)
    print("Fetched topics and descriptions:\n")
    for i, item in enumerate(topics, start=1):
        print(f"{i}. Topic: {item['topic']}\n   Description: {item['description']}\n")

    prompts = fetch_prompts(service, prompts_sheet_id)
    print("\nPlatform prompts loaded:\n")
    for platform, prompt in prompts.items():
        print(f"{platform}: {prompt}\n")

    print("\n=== Generating AI Content ===\n")
    for item in topics:
        topic = item["topic"]
        description = item["description"]
        print(f"--- Topic: {topic} ---\n")
        for platform, prompt_template in prompts.items():
            full_prompt = prompt_template.replace("{description}", description)
            print(f"Platform: {platform}")
            generated_text = generate_content(full_prompt)
            print(generated_text)
            print("="*80)

if __name__ == '__main__':
    main()
