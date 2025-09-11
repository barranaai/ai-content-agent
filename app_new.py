import os
import os.path
import pickle
import json
import logging
from datetime import datetime
from flask import Flask, request, jsonify
from flask_cors import CORS
from dotenv import load_dotenv
from openai import OpenAI
from google.auth.transport.requests import Request
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

# Import our new systems
from prompt_library import BarranaPromptLibrary
from validation import ContentValidator
from seo_manager import SEOManager

# Load environment variables
load_dotenv()

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Initialize OpenAI client
client = OpenAI()

# Feature flags
USE_JSON_LIBRARY = os.environ.get('USE_JSON_LIBRARY', 'true').lower() == 'true'
FALLBACK_TO_SHEETS = os.environ.get('FALLBACK_TO_SHEETS', 'true').lower() == 'true'

# Initialize Flask app
app = Flask(__name__)
CORS(app, origins=['http://localhost:3000', 'http://localhost:3001'])

# Initialize new systems
prompt_library = None
validator = None
seo_manager = None

def initialize_new_systems():
    """Initialize the new JSON-based systems"""
    global prompt_library, validator, seo_manager
    
    try:
        if USE_JSON_LIBRARY:
            prompt_library = BarranaPromptLibrary()
            validator = ContentValidator(prompt_library)
            seo_manager = SEOManager(prompt_library)
            logging.info("✅ New JSON-based systems initialized successfully")
            return True
        else:
            logging.info("ℹ️ JSON library disabled via feature flag")
            return False
    except Exception as e:
        logging.error(f"❌ Failed to initialize new systems: {e}")
        if FALLBACK_TO_SHEETS:
            logging.info("🔄 Falling back to Google Sheets system")
            return False
        else:
            raise

# Initialize systems on startup
initialize_new_systems()

# Legacy Google Sheets functions (for backward compatibility)
SCOPES = ['https://www.googleapis.com/auth/spreadsheets.readonly']

def get_google_sheets_service():
    """Legacy Google Sheets service (fallback)"""
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

def fetch_topics_legacy(service, sheet_id):
    """Legacy topics fetching from Google Sheets"""
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

def fetch_prompts_legacy(service, sheet_id):
    """Legacy prompts fetching from Google Sheets"""
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

# New API endpoints using JSON library
@app.route('/api/topics')
def api_get_topics():
    """Get topics - uses JSON library if available, falls back to Google Sheets"""
    try:
        if prompt_library and prompt_library.is_loaded():
            # Use JSON library - return available platforms as topics
            platforms = prompt_library.get_available_platforms()
            topics = []
            for platform in platforms:
                config = prompt_library.get_platform_config(platform)
                topics.append({
                    "topic": platform.title(),
                    "description": f"Generate content for {platform} platform using {config['voice']}"
                })
            
            logging.info(f"✅ Topics loaded from JSON library: {len(topics)} topics")
            return jsonify(topics)
        
        elif FALLBACK_TO_SHEETS:
            # Fallback to Google Sheets
            service = get_google_sheets_service()
            topics_sheet_id = '12qFx-0Si0-g8Hp_yq7sIm7I5gJiACaOaLep04dSYC_U'
            topics = fetch_topics_legacy(service, topics_sheet_id)
            logging.info(f"✅ Topics loaded from Google Sheets: {len(topics)} topics")
            return jsonify(topics)
        
        else:
            return jsonify({"error": "No data source available"}), 500
            
    except Exception as e:
        logging.error(f"❌ Error loading topics: {e}")
        return jsonify({"error": f"Failed to load topics: {str(e)}"}), 500

@app.route('/api/platform-prompts')
def api_get_prompts():
    """Get platform prompts - uses JSON library if available, falls back to Google Sheets"""
    try:
        if prompt_library and prompt_library.is_loaded():
            # Use JSON library - return platform configurations
            platforms = prompt_library.get_available_platforms()
            prompts = {}
            
            for platform in platforms:
                config = prompt_library.get_platform_config(platform)
                prompts[platform] = config['prompt_template']
            
            logging.info(f"✅ Platform prompts loaded from JSON library: {len(prompts)} platforms")
            return jsonify(prompts)
        
        elif FALLBACK_TO_SHEETS:
            # Fallback to Google Sheets
            service = get_google_sheets_service()
            prompts_sheet_id = '1MIS7Nl1AdTy7mjwKaIDCBV820bXZteHvdIxo8WETYnc'
            prompts = fetch_prompts_legacy(service, prompts_sheet_id)
            logging.info(f"✅ Platform prompts loaded from Google Sheets: {len(prompts)} platforms")
            return jsonify(prompts)
        
        else:
            return jsonify({"error": "No data source available"}), 500
            
    except Exception as e:
        logging.error(f"❌ Error loading platform prompts: {e}")
        return jsonify({"error": f"Failed to load platform prompts: {str(e)}"}), 500

@app.route('/api/generate-content', methods=['POST'])
def api_generate_content():
    """Generate content - uses new JSON system with validation and quality control"""
    try:
        data = request.json
        if not data:
            return jsonify({"error": "No JSON data provided"}), 400
        
        # Extract data
        topic = data.get('topic')
        description = data.get('description')
        platforms = data.get('platforms', [])
        prompts = data.get('prompts', {})
        
        logging.info(f"📝 Content generation request - Topic: {topic}, Platforms: {platforms}")
        
        # Validate required data
        if not topic or not description or not platforms:
            return jsonify({"error": "Missing required data: topic, description, or platforms"}), 400
        
        # Check OpenAI API key
        api_key = os.environ.get("OPENAI_API_KEY")
        if not api_key or api_key == "your_openai_api_key_here":
            return jsonify({"error": "OpenAI API key not configured"}), 500
        
        results = {}
        
        # Process each platform
        for platform in platforms:
            try:
                if prompt_library and prompt_library.is_loaded():
                    # Use new JSON-based system
                    result = generate_content_with_json_system(description, platform)
                    results[platform] = result
                else:
                    # Fallback to legacy system
                    result = generate_content_with_legacy_system(description, platform, prompts)
                    results[platform] = result
                    
            except Exception as e:
                logging.error(f"❌ Error generating content for {platform}: {e}")
                results[platform] = f"Error generating content: {str(e)}"
        
        logging.info(f"✅ Content generation completed for {len(results)} platforms")
        return jsonify(results)
        
    except Exception as e:
        logging.error(f"❌ Error in content generation: {e}")
        return jsonify({"error": f"Internal server error: {str(e)}"}), 500

def generate_content_with_json_system(description: str, platform: str) -> str:
    """Generate content using the new JSON-based system"""
    try:
        # Validate input
        input_validation = validator.validate_input(description, platform)
        if not input_validation['valid']:
            raise ValueError(f"Input validation failed: {input_validation['errors']}")
        
        # Get optimized keywords
        keywords = seo_manager.get_platform_optimized_keywords(platform, "general")
        
        # Build prompt
        prompt = prompt_library.build_prompt(
            description=description,
            platform=platform,
            primary_keywords=keywords['primary'],
            secondary_keywords=keywords['secondary']
        )
        
        # Generate content with OpenAI
        response = client.chat.completions.create(
            model="gpt-4",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=800,
            temperature=0.7
        )
        
        content = response.choices[0].message.content
        
        # Validate output
        output_validation = validator.validate_output(content, platform)
        
        # Log validation results
        if not output_validation['valid']:
            logging.warning(f"⚠️ Content validation issues for {platform}: {output_validation['issues']}")
        
        # Return enhanced content with metadata
        enhanced_content = f"{content}\n\n---\n📊 Quality Metrics:\n"
        enhanced_content += f"• Word count: {output_validation['metrics'].get('word_count', 0)}\n"
        enhanced_content += f"• CTA included: {output_validation['metrics'].get('cta_included', False)}\n"
        enhanced_content += f"• Keywords used: {', '.join(keywords['primary'])}\n"
        
        if output_validation['suggestions']:
            enhanced_content += f"• Suggestions: {'; '.join(output_validation['suggestions'])}\n"
        
        return enhanced_content
        
    except Exception as e:
        logging.error(f"❌ JSON system generation failed for {platform}: {e}")
        raise

def generate_content_with_legacy_system(description: str, platform: str, prompts: dict) -> str:
    """Generate content using the legacy Google Sheets system"""
    try:
        prompt_template = prompts.get(platform)
        if not prompt_template:
            return f"No prompt template found for {platform}"
        
        full_prompt = prompt_template.replace("{description}", description)
        
        response = client.chat.completions.create(
            model="gpt-4",
            messages=[{"role": "user", "content": full_prompt}],
            max_tokens=800,
            temperature=0.7
        )
        
        return response.choices[0].message.content
        
    except Exception as e:
        logging.error(f"❌ Legacy system generation failed for {platform}: {e}")
        raise

# Health check endpoint
@app.route('/api/health')
def api_health():
    """Health check endpoint"""
    health_status = {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "systems": {
            "json_library": prompt_library.is_loaded() if prompt_library else False,
            "validator": validator is not None,
            "seo_manager": seo_manager is not None,
            "openai": bool(os.environ.get("OPENAI_API_KEY")),
            "google_sheets": os.path.exists('token.pickle')
        },
        "feature_flags": {
            "use_json_library": USE_JSON_LIBRARY,
            "fallback_to_sheets": FALLBACK_TO_SHEETS
        }
    }
    
    return jsonify(health_status)

# System info endpoint
@app.route('/api/system-info')
def api_system_info():
    """System information endpoint"""
    info = {
        "version": "2.0.0",
        "json_library_version": prompt_library.library.get('version') if prompt_library else None,
        "available_platforms": prompt_library.get_available_platforms() if prompt_library else [],
        "features": {
            "validation": validator is not None,
            "seo_management": seo_manager is not None,
            "keyword_rotation": seo_manager is not None,
            "quality_control": validator is not None
        }
    }
    
    return jsonify(info)

if __name__ == '__main__':
    print("🚀 Starting AI Content Agent v2.0")
    print(f"📊 JSON Library: {'✅ Enabled' if prompt_library else '❌ Disabled'}")
    print(f"🔄 Google Sheets Fallback: {'✅ Enabled' if FALLBACK_TO_SHEETS else '❌ Disabled'}")
    print(f"🔧 Feature Flags: JSON={USE_JSON_LIBRARY}, Fallback={FALLBACK_TO_SHEETS}")
    
    app.run(port=5050, debug=True)
