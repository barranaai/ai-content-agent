import os
import os.path
import pickle
import json
import logging
from datetime import datetime
from flask import Flask, request, jsonify, send_from_directory, send_file
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
from rag_system import BarranaRAGSystem

# Load environment variables
load_dotenv()

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Initialize OpenAI client
client = OpenAI()

# Feature flags
USE_JSON_LIBRARY = os.environ.get('USE_JSON_LIBRARY', 'true').lower() == 'true'
FALLBACK_TO_SHEETS = os.environ.get('FALLBACK_TO_SHEETS', 'true').lower() == 'true'

# Initialize Flask app with static folder configuration
app = Flask(__name__, 
            static_folder='ai-content-agent-ui/build',
            static_url_path='')

# CORS configuration for development and production
allowed_origins = [
    'http://localhost:3000', 
    'http://localhost:3001',
    'http://191.101.233.56',
]

# Add Render App Platform URL if available
render_url = os.environ.get('RENDER_EXTERNAL_URL')
if render_url:
    allowed_origins.append(render_url)
    logging.info(f"Added Render URL to CORS: {render_url}")

# Add custom app URL if available (for DigitalOcean or custom domains)
do_app_url = os.environ.get('DO_APP_URL')
if do_app_url:
    allowed_origins.append(f'https://{do_app_url}')

CORS(app, origins=allowed_origins)

# Initialize new systems
prompt_library = None
validator = None
seo_manager = None
rag_system = None

def initialize_new_systems():
    """Initialize the new JSON-based systems"""
    global prompt_library, validator, seo_manager, rag_system
    
    try:
        if USE_JSON_LIBRARY:
            prompt_library = BarranaPromptLibrary()
            validator = ContentValidator(prompt_library)
            seo_manager = SEOManager(prompt_library)
            
            # Initialize RAG system (optional - will gracefully degrade if corpus not available)
            rag_system = None
            try:
                rag_system = BarranaRAGSystem()
                if rag_system.initialize():
                    logging.info("✅ RAG system initialized successfully")
                else:
                    logging.warning("⚠️ RAG system initialization failed - continuing without RAG")
                    rag_system = None
            except Exception as e:
                logging.warning(f"⚠️ RAG system not available: {e} - continuing without RAG")
                rag_system = None
            
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

def get_secret_file_path(filename):
    """Get the correct path for secret files (local or Render's /etc/secrets/)"""
    # Check Render's secret files location first
    render_path = f'/etc/secrets/{filename}'
    if os.path.exists(render_path):
        return render_path
    # Fall back to local path
    local_path = filename
    if os.path.exists(local_path):
        return local_path
    return None

def get_google_sheets_service():
    """Legacy Google Sheets service (fallback)"""
    creds = None
    token_path = get_secret_file_path('token.pickle')
    client_secret_path = get_secret_file_path('client_secret.json')
    
    if not token_path:
        raise Exception("token.pickle not found in any location")
    
    if not client_secret_path:
        raise Exception("client_secret.json not found in any location")
    
    # Load existing credentials
    try:
        with open(token_path, 'rb') as token_file:
            token_data = token_file.read()
            
        # Log first few bytes for debugging
        logging.info(f"🔍 Token file first bytes: {token_data[:10]}")
        logging.info(f"📏 Token file size: {len(token_data)} bytes")
            
        # Try to detect if file is base64 encoded (workaround for Render text upload)
        # Base64 encoded pickle files will start with 'gASV' (base64 of pickle protocol 5)
        # Valid binary pickle files start with \x80\x03, \x80\x04, \x80\x05
        if token_data.startswith(b'gASV') or (not token_data.startswith(b'\x80') and len(token_data) > 100):
            try:
                import base64
                # Remove ALL whitespace/newlines that might have been added by text editor
                token_data_clean = b''.join(token_data.split())
                logging.info(f"🧹 Cleaned base64 data size: {len(token_data_clean)} bytes")
                token_data = base64.b64decode(token_data_clean)
                logging.info(f"🔄 Decoded base64-encoded token.pickle to {len(token_data)} bytes")
            except Exception as decode_err:
                logging.error(f"❌ Failed to decode base64: {decode_err}")
                # Continue with original data
        
        creds = pickle.loads(token_data)
        logging.info(f"✅ Loaded credentials from {token_path}")
    except Exception as e:
        logging.error(f"❌ Failed to load token.pickle: {e}")
        if 'token_data' in locals():
            logging.error(f"📊 File size: {len(token_data)} bytes, first 20 bytes: {token_data[:20]}")
        raise
    
    # Check if credentials are valid
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            try:
                logging.info("🔄 Token expired, attempting to refresh...")
                creds.refresh(Request())
                logging.info("✅ Token refreshed successfully")
                # Note: We can't save the refreshed token in /etc/secrets/ (read-only)
                # You'll need to regenerate token.pickle locally and re-upload to Render when it expires
            except Exception as e:
                logging.error(f"❌ Failed to refresh token: {e}")
                raise Exception(f"Token refresh failed. Please regenerate token.pickle locally and re-upload to Render. Error: {e}")
        else:
            # Token is invalid and can't be refreshed - need manual intervention
            raise Exception("Token is invalid or expired without refresh token. Please regenerate token.pickle locally using google-sheets-connect.py and re-upload to Render.")
    
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

# Default topics fallback (when Google Sheets is not available)
DEFAULT_TOPICS = [
    {"topic": "AI and Automation", "description": "How AI and automation transform business operations"},
    {"topic": "Digital Transformation", "description": "Modernizing business processes with technology"},
    {"topic": "Customer Experience", "description": "Improving customer satisfaction and engagement"},
    {"topic": "Data Analytics", "description": "Using data to drive business decisions"},
    {"topic": "Cloud Computing", "description": "Benefits and strategies for cloud adoption"},
    {"topic": "Cybersecurity", "description": "Protecting business data and systems"},
    {"topic": "Remote Work", "description": "Managing distributed teams effectively"},
    {"topic": "Productivity Tools", "description": "Software and tools that boost team productivity"},
    {"topic": "Marketing Automation", "description": "Automating marketing campaigns and workflows"},
    {"topic": "Business Intelligence", "description": "Turning data into actionable insights"}
]

# New API endpoints using JSON library
@app.route('/api/topics')
def api_get_topics():
    """Get topics - Try Google Sheets, fallback to default topics"""
    try:
        # Try to load from Google Sheets if credentials are available
        token_path = get_secret_file_path('token.pickle')
        client_secret_path = get_secret_file_path('client_secret.json')
        
        if token_path and client_secret_path:
            logging.info(f"🔑 Found credentials - token: {token_path}, client_secret: {client_secret_path}")
            service = get_google_sheets_service()
            topics_sheet_id = '12qFx-0Si0-g8Hp_yq7sIm7I5gJiACaOaLep04dSYC_U'
            topics = fetch_topics_legacy(service, topics_sheet_id)
            logging.info(f"✅ Topics loaded from Google Sheets: {len(topics)} topics")
            return jsonify(topics)
        else:
            # Google Sheets credentials not available, use default topics
            logging.info(f"ℹ️ Google Sheets credentials not found (token: {token_path}, client_secret: {client_secret_path}), using default topics: {len(DEFAULT_TOPICS)} topics")
            return jsonify(DEFAULT_TOPICS)
            
    except Exception as e:
        # If Google Sheets fails, fallback to default topics
        logging.warning(f"⚠️ Failed to load topics from Google Sheets: {e}")
        logging.info(f"🔄 Falling back to default topics: {len(DEFAULT_TOPICS)} topics")
        return jsonify(DEFAULT_TOPICS)

@app.route('/api/platforms')
def api_get_platforms():
    """Get available platforms from JSON library"""
    try:
        if prompt_library and prompt_library.is_loaded():
            platforms = prompt_library.get_available_platforms()
            # Return platforms with their display names
            platform_list = []
            for platform in platforms:
                config = prompt_library.get_platform_config(platform)
                platform_list.append({
                    "key": platform,
                    "name": platform.replace('_', ' ').title().replace('Quick', '').replace('Blog', '').strip(),
                    "voice": config.get('voice', ''),
                    "word_count": config.get('word_count', {})
                })
            
            logging.info(f"✅ Platforms loaded from JSON library: {len(platform_list)} platforms")
            return jsonify(platform_list)
        else:
            return jsonify({"error": "JSON library not available"}), 500
            
    except Exception as e:
        logging.error(f"❌ Error loading platforms: {e}")
        return jsonify({"error": f"Failed to load platforms: {str(e)}"}), 500

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
        metrics = {}
        
        # Process each platform
        for platform in platforms:
            try:
                if prompt_library and prompt_library.is_loaded():
                    # Use new JSON-based system
                    result, platform_metrics, engagement_package = generate_content_with_json_system(description, platform)
                    metrics[platform] = platform_metrics
                    
                    # Always structure the result as an object for consistency
                    results[platform] = {
                        'main_content': result,
                        'engagement': engagement_package if engagement_package else None
                    }
                else:
                    # Fallback to legacy system
                    result = generate_content_with_legacy_system(description, platform, prompts)
                    results[platform] = {
                        'main_content': result,
                        'engagement': None
                    }
                    # Basic metrics for legacy system
                    metrics[platform] = {
                        "word_count": len(result.split()),
                        "cta_included": "cta" in result.lower() or "call to action" in result.lower(),
                        "has_keywords": len(description.split()) > 0
                    }
                    
            except Exception as e:
                logging.error(f"❌ Error generating content for {platform}: {e}")
                results[platform] = {
                    'main_content': f"Error generating content: {str(e)}",
                    'engagement': None
                }
                metrics[platform] = {"error": str(e)}
        
        logging.info(f"✅ Content generation completed for {len(results)} platforms")
        return jsonify({
            "content": results,
            "metrics": metrics
        })
        
    except Exception as e:
        logging.error(f"❌ Error in content generation: {e}")
        return jsonify({"error": f"Internal server error: {str(e)}"}), 500

def generate_content_with_json_system(description: str, platform: str) -> tuple:
    """Generate content using the new JSON-based system"""
    try:
        # Validate input
        input_validation = validator.validate_input(description, platform)
        if not input_validation['valid']:
            raise ValueError(f"Input validation failed: {input_validation['errors']}")
        
        # Get optimized keywords
        keywords = seo_manager.get_platform_optimized_keywords(platform, "general")
        
        # Get RAG context if available
        rag_context = ""
        if rag_system and rag_system.is_loaded:
            try:
                rag_context = rag_system.get_context(description, top_k=3, min_score=0.3)
                if rag_context:
                    logging.info(f"🔍 Retrieved RAG context for {platform}: {len(rag_context)} characters")
                else:
                    logging.info(f"ℹ️ No relevant RAG context found for {platform}")
            except Exception as e:
                logging.warning(f"⚠️ RAG context retrieval failed: {e}")
                rag_context = ""
        
        # Build prompt with optional RAG context
        prompt = prompt_library.build_prompt(
            description=description,
            platform=platform,
            primary_keywords=keywords['primary'],
            secondary_keywords=keywords['secondary'],
            rag_context=rag_context
        )
        
        # Log the prompt being sent (for debugging)
        logging.info(f"🔍 Prompt being sent to OpenAI for {platform}:")
        logging.info(f"📝 Prompt length: {len(prompt)} characters")
        logging.info(f"📝 Prompt preview: {prompt[:500]}...")
        
        # Generate content with OpenAI
        response = client.chat.completions.create(
            model="gpt-4",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=1000,
            temperature=0.7
        )
        
        content = response.choices[0].message.content
        
        # Apply LinkedIn-specific optimizations if applicable
        if platform in ['linkedin', 'linkedin_quick']:
            try:
                optimized_content = prompt_library.apply_linkedin_optimizations(content, description, platform)
                if optimized_content != content:
                    logging.info(f"🔧 Applied LinkedIn optimizations for {platform}")
                    content = optimized_content
            except Exception as e:
                logging.warning(f"⚠️ LinkedIn optimization failed for {platform}: {e}")
                # Continue with original content if optimization fails
        
        # Validate output
        output_validation = validator.validate_output(content, platform)
        
        # Log validation results
        if not output_validation['valid']:
            logging.warning(f"⚠️ Content validation issues for {platform}: {output_validation['issues']}")
        
        # Return all metrics including platform-specific ones
        platform_metrics = output_validation['metrics']
        
        # Generate engagement package for social media platforms
        engagement_package = {}
        if prompt_library.is_engagement_enabled_for_platform(platform):
            try:
                engagement_package = prompt_library.generate_engagement_package(
                    content, platform, description
                )
                # Get comment count from either new format (meta.total_comments) or old format (comments_count)
                comment_count = engagement_package.get('meta', {}).get('total_comments', engagement_package.get('comments_count', 0))
                logging.info(f"✅ Generated engagement package for {platform}: {comment_count} comments")
            except Exception as e:
                logging.warning(f"⚠️ Failed to generate engagement package for {platform}: {e}")
                engagement_package = {}
        
        # Return enhanced content with metadata
        enhanced_content = f"{content}\n\n---\n📊 Quality Metrics:\n"
        enhanced_content += f"• Word count: {platform_metrics['word_count']}\n"
        enhanced_content += f"• CTA included: {platform_metrics['cta_included']}\n"
        enhanced_content += f"• Keywords used: {', '.join(keywords['primary'])}\n"
        
        if output_validation['suggestions']:
            enhanced_content += f"• Suggestions: {'; '.join(output_validation['suggestions'])}\n"
        
        return enhanced_content, platform_metrics, engagement_package
        
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

# Serve React Frontend - must be LAST route (catch-all)
@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def serve_react(path):
    """Serve React frontend for all non-API routes"""
    # API routes should be handled by their specific endpoints above
    if path.startswith('api/'):
        return jsonify({"error": "API endpoint not found"}), 404
    
    # Build directory path
    build_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'ai-content-agent-ui', 'build')
    
    # If it's a file request (has extension) and exists, serve it
    if path and ('.' in path.split('/')[-1]):
        file_path = os.path.join(build_dir, path)
        if os.path.exists(file_path):
            return send_from_directory(build_dir, path)
        else:
            logging.warning(f"Static file not found: {path}")
            return jsonify({"error": "File not found"}), 404
    
    # For all other routes (SPA routing), serve index.html
    return send_from_directory(build_dir, 'index.html')

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
            "google_sheets": get_secret_file_path('token.pickle') is not None
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
        "rag_system": rag_system.get_stats() if rag_system else {"is_loaded": False},
        "features": {
            "validation": validator is not None,
            "seo_management": seo_manager is not None,
            "keyword_rotation": seo_manager is not None,
            "quality_control": validator is not None,
            "rag_enhancement": rag_system is not None and rag_system.is_loaded
        }
    }
    
    return jsonify(info)

# Engagement package endpoint
@app.route('/api/engagement-package', methods=['POST'])
def api_generate_engagement_package():
    """Generate engagement package for a specific platform and content"""
    try:
        data = request.json
        if not data:
            return jsonify({"error": "No JSON data provided"}), 400
        
        # Extract data
        main_content = data.get('main_content')
        platform = data.get('platform')
        description = data.get('description')
        
        if not main_content or not platform or not description:
            return jsonify({"error": "Missing required data: main_content, platform, or description"}), 400
        
        if not prompt_library or not prompt_library.is_loaded():
            return jsonify({"error": "Prompt library not available"}), 500
        
        if not prompt_library.is_engagement_enabled_for_platform(platform):
            return jsonify({"error": f"Engagement system not enabled for platform: {platform}"}), 400
        
        # Generate engagement package
        engagement_package = prompt_library.generate_engagement_package(
            main_content, platform, description
        )
        
        if not engagement_package:
            return jsonify({"error": "Failed to generate engagement package"}), 500
        
        logging.info(f"✅ Generated engagement package for {platform}: {engagement_package.get('comments_count', 0)} comments")
        
        return jsonify({
            "success": True,
            "engagement_package": engagement_package
        })
        
    except Exception as e:
        logging.error(f"❌ Error generating engagement package: {e}")
        return jsonify({"error": f"Internal server error: {str(e)}"}), 500

if __name__ == '__main__':
    print("🚀 Starting AI Content Agent v2.0")
    print(f"📊 JSON Library: {'✅ Enabled' if prompt_library else '❌ Disabled'}")
    print(f"🔄 Google Sheets Fallback: {'✅ Enabled' if FALLBACK_TO_SHEETS else '❌ Disabled'}")
    print(f"🔧 Feature Flags: JSON={USE_JSON_LIBRARY}, Fallback={FALLBACK_TO_SHEETS}")
    
    # Get port from environment variable (DigitalOcean sets this)
    port = int(os.environ.get('PORT', 5050))
    debug = os.environ.get('FLASK_ENV') != 'production'
    
    print(f"🌐 Starting server on port {port}")
    app.run(host='0.0.0.0', port=port, debug=debug)
