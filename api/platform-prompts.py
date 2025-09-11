from flask import Flask, jsonify
from flask_cors import CORS
from utils import get_google_sheets_service, fetch_prompts

app = Flask(__name__)
CORS(app)

def handler(request):
    try:
        service = get_google_sheets_service()
        prompts_sheet_id = '1MIS7Nl1AdTy7mjwKaIDCBV820bXZteHvdIxo8WETYnc'
        prompts = fetch_prompts(service, prompts_sheet_id)
        return jsonify(prompts)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# For local testing
if __name__ == '__main__':
    app.run(port=5002, debug=True)
