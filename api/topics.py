from flask import Flask, jsonify
from flask_cors import CORS
from utils import get_google_sheets_service, fetch_topics

app = Flask(__name__)
CORS(app)

def handler(request):
    try:
        service = get_google_sheets_service()
        topics_sheet_id = '12qFx-0Si0-g8Hp_yq7sIm7I5gJiACaOaLep04dSYC_U'
        topics = fetch_topics(service, topics_sheet_id)
        return jsonify(topics)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# For local testing
if __name__ == '__main__':
    app.run(port=5001, debug=True)
