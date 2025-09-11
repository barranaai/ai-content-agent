import os
import json
from http.server import BaseHTTPRequestHandler
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

client = OpenAI()

class handler(BaseHTTPRequestHandler):
    def do_POST(self):
        try:
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)
            data = json.loads(post_data.decode('utf-8'))
            
            if not data:
                self.send_response(400)
                self.send_header('Content-type', 'application/json')
                self.send_header('Access-Control-Allow-Origin', '*')
                self.end_headers()
                self.wfile.write(json.dumps({"error": "No JSON data provided"}).encode())
                return
                
            topic = data.get('topic')
            description = data.get('description')
            platforms = data.get('platforms', [])
            prompts = data.get('prompts', {})
            
            print(f"Received request - Topic: {topic}, Platforms: {platforms}")
            
            if not topic or not description or not platforms or not prompts:
                self.send_response(400)
                self.send_header('Content-type', 'application/json')
                self.send_header('Access-Control-Allow-Origin', '*')
                self.end_headers()
                self.wfile.write(json.dumps({"error": "Missing required data"}).encode())
                return

            # Check if OpenAI API key is set
            api_key = os.environ.get("OPENAI_API_KEY")
            print(f"OpenAI API Key present: {bool(api_key)}")
            print(f"API Key value: {api_key[:10] if api_key else 'None'}...")
            
            if not api_key or api_key == "your_openai_api_key_here":
                self.send_response(500)
                self.send_header('Content-type', 'application/json')
                self.send_header('Access-Control-Allow-Origin', '*')
                self.end_headers()
                self.wfile.write(json.dumps({"error": "OpenAI API key not configured"}).encode())
                return

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
                
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            self.wfile.write(json.dumps(results).encode())
        except Exception as e:
            print(f"Error in generate-content: {str(e)}")
            self.send_response(500)
            self.send_header('Content-type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            self.wfile.write(json.dumps({"error": f"Internal server error: {str(e)}"}).encode())
