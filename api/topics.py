from http.server import BaseHTTPRequestHandler
import json
from utils import get_google_sheets_service, fetch_topics

class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        try:
            service = get_google_sheets_service()
            topics_sheet_id = '12qFx-0Si0-g8Hp_yq7sIm7I5gJiACaOaLep04dSYC_U'
            topics = fetch_topics(service, topics_sheet_id)
            
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            self.wfile.write(json.dumps(topics).encode())
        except Exception as e:
            self.send_response(500)
            self.send_header('Content-type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            self.wfile.write(json.dumps({"error": str(e)}).encode())
