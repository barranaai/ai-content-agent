import os
from flask import Flask, request, jsonify
from flask_cors import CORS
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
CORS(app)

client = OpenAI()

def handler(request):
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

# For local testing
if __name__ == '__main__':
    app.run(port=5003, debug=True)
