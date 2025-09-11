from http.server import BaseHTTPRequestHandler
import json
import os
import traceback

class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        try:
            # Check environment variables first
            missing_vars = []
            if not os.environ.get('GOOGLE_CLIENT_SECRET'):
                missing_vars.append('GOOGLE_CLIENT_SECRET')
            if not os.environ.get('GOOGLE_TOKEN_PICKLE'):
                missing_vars.append('GOOGLE_TOKEN_PICKLE')
            
            if missing_vars:
                error_msg = f"Missing environment variables: {', '.join(missing_vars)}"
                print(error_msg)
                self.send_response(500)
                self.send_header('Content-type', 'application/json')
                self.send_header('Access-Control-Allow-Origin', '*')
                self.end_headers()
                self.wfile.write(json.dumps({
                    "error": error_msg,
                    "hint": "Please add missing environment variables in Vercel dashboard"
                }).encode())
                return
            
            # Try to import and use Google Sheets service
            from utils import get_google_sheets_service, fetch_topics
            
            print("Creating Google Sheets service...")
            service = get_google_sheets_service()
            print("Google Sheets service created successfully")
            
            topics_sheet_id = '12qFx-0Si0-g8Hp_yq7sIm7I5gJiACaOaLep04dSYC_U'
            print(f"Fetching topics from sheet: {topics_sheet_id}")
            topics = fetch_topics(service, topics_sheet_id)
            print(f"Successfully fetched {len(topics)} topics")
            
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            self.wfile.write(json.dumps(topics).encode())
            
        except Exception as e:
            error_msg = f"Topics API Error: {str(e)}"
            traceback_str = traceback.format_exc()
            print(f"ERROR: {error_msg}")
            print(f"TRACEBACK: {traceback_str}")
            
            self.send_response(500)
            self.send_header('Content-type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            self.wfile.write(json.dumps({
                "error": error_msg,
                "traceback": traceback_str,
                "hint": "Check Vercel environment variables and Google Sheets access"
            }).encode())
