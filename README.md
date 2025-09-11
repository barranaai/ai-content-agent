# AI Content Agent

An AI-powered content generation tool that creates platform-specific content from Google Sheets data.

## Features

- **Google Sheets Integration**: Fetches topics and prompts from Google Sheets
- **Multi-Platform Support**: Generates content for LinkedIn, Medium, Substack, Pinterest, Reddit, and Product Hunt
- **AI-Powered**: Uses OpenAI GPT-4 for intelligent content generation
- **Modern UI**: React frontend with Material-UI components

## Local Development

### Prerequisites

1. Python 3.8+
2. Node.js and npm
3. OpenAI API key
4. Google Cloud Console project with Sheets API enabled

### Setup

1. **Clone and setup Python environment**:
   ```bash
   python3 -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt
   ```

2. **Configure environment variables**:
   Create a `.env` file with:
   ```
   OPENAI_API_KEY=your_openai_api_key_here
   GOOGLE_SHEETS_TOPICS_ID=12qFx-0Si0-g8Hp_yq7sIm7I5gJiACaOaLep04dSYC_U
   GOOGLE_SHEETS_PROMPTS_ID=1MIS7Nl1AdTy7mjwKaIDCBV820bXZteHvdIxo8WETYnc
   ```

3. **Setup Google Sheets authentication**:
   - Download `client_secret.json` from Google Cloud Console
   - Run `python google-sheets-connect.py` to generate `token.pickle`

4. **Start the backend**:
   ```bash
   source venv/bin/activate
   python app.py
   ```
   Backend runs on http://localhost:5050

5. **Start the frontend**:
   ```bash
   cd ai-content-agent-ui
   npm install
   npm start
   ```
   Frontend runs on http://localhost:3000

## Usage

1. Select a topic from the dropdown
2. Choose target platforms
3. Click "Generate Content"
4. Review and use the generated content

## Project Structure

```
ai-content-agent/
├── app.py                    # Flask backend
├── google-sheets-connect.py  # Google Sheets connection script
├── requirements.txt          # Python dependencies
├── client_secret.json        # Google OAuth credentials
├── token.pickle             # Google auth token
├── .env                     # Environment variables
└── ai-content-agent-ui/     # React frontend
    ├── package.json         # React dependencies
    └── src/App.js           # Main React component
```

## API Endpoints

- `GET /api/topics` - Fetch topics from Google Sheets
- `GET /api/platform-prompts` - Fetch platform-specific prompts
- `POST /api/generate-content` - Generate AI content
