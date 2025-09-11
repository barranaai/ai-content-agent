from http.server import BaseHTTPRequestHandler
import json
import os
import base64

class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        # Check if all required environment variables are present
        env_vars = {
            'GOOGLE_CLIENT_SECRET': 'SET' if os.environ.get('GOOGLE_CLIENT_SECRET') else 'NOT SET',
            'GOOGLE_TOKEN_PICKLE': 'SET' if os.environ.get('GOOGLE_TOKEN_PICKLE') else 'NOT SET',
            'OPENAI_API_KEY': 'SET' if os.environ.get('OPENAI_API_KEY') else 'NOT SET',
            'GOOGLE_SHEETS_TOPICS_ID': 'SET' if os.environ.get('GOOGLE_SHEETS_TOPICS_ID') else 'NOT SET',
            'GOOGLE_SHEETS_PROMPTS_ID': 'SET' if os.environ.get('GOOGLE_SHEETS_PROMPTS_ID') else 'NOT SET'
        }
        
        # Test token.pickle decoding if it exists
        token_test = "NOT SET"
        if os.environ.get('GOOGLE_TOKEN_PICKLE'):
            try:
                token_data = base64.b64decode(os.environ.get('GOOGLE_TOKEN_PICKLE'))
                token_test = f"DECODED SUCCESSFULLY ({len(token_data)} bytes)"
            except Exception as e:
                token_test = f"DECODE ERROR: {str(e)}"
        
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        self.wfile.write(json.dumps({
            "message": "API is working!",
            "environment_variables": env_vars,
            "token_pickle_test": token_test
        }).encode())
