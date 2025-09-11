# 🚀 Vercel Deployment Guide

## Prerequisites
1. GitHub account
2. Vercel account (free)
3. OpenAI API key

## Deployment Steps

### 1. Push to GitHub
```bash
git init
git add .
git commit -m "Initial commit"
git branch -M main
git remote add origin https://github.com/yourusername/ai-content-agent.git
git push -u origin main
```

### 2. Deploy to Vercel
1. Go to [vercel.com](https://vercel.com)
2. Click "New Project"
3. Import your GitHub repository
4. Vercel will auto-detect the configuration

### 3. Set Environment Variables
In Vercel dashboard:
- Go to Project Settings → Environment Variables
- Add: `OPENAI_API_KEY` = your actual OpenAI API key

### 4. Upload Google Sheets Files
You'll need to upload these files to Vercel:
- `client_secret.json` (Google OAuth credentials)
- `token.pickle` (Google Sheets auth token)

### 5. Deploy
Click "Deploy" and wait for deployment to complete!

## File Structure
```
ai-content-agent/
├── api/                    # Serverless functions
│   ├── topics.py          # /api/topics
│   ├── platform-prompts.py # /api/platform-prompts
│   ├── generate-content.py # /api/generate-content
│   └── utils.py           # Shared utilities
├── ai-content-agent-ui/    # React frontend
├── vercel.json            # Vercel configuration
└── requirements.txt       # Python dependencies
```

## URLs After Deployment
- Frontend: `https://your-project.vercel.app`
- API: `https://your-project.vercel.app/api/topics`

## Troubleshooting
- Check Vercel function logs for errors
- Ensure all environment variables are set
- Verify Google Sheets files are uploaded
