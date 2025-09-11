from http.server import BaseHTTPRequestHandler
import json
from utils import get_google_sheets_service, fetch_prompts

class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        try:
            service = get_google_sheets_service()
            prompts_sheet_id = '1MIS7Nl1AdTy7mjwKaIDCBV820bXZteHvdIxo8WETYnc'
            prompts = fetch_prompts(service, prompts_sheet_id)
            
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            self.wfile.write(json.dumps(prompts).encode())
        except Exception as e:
            self.send_response(500)
            self.send_header('Content-type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            self.wfile.write(json.dumps({"error": str(e)}).encode())
