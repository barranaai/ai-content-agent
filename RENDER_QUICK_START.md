# 🚀 Quick Start - Deploy to Render in 5 Minutes

## Step 1: Push to GitHub (2 min)

```bash
# If not already a git repo
git init

# Add all files
git add .
git commit -m "Initial commit for Render deployment"

# Create a new repo on GitHub, then:
git remote add origin https://github.com/YOUR_USERNAME/ai-content-agent.git
git push -u origin main
```

## Step 2: Create Render Account (1 min)

1. Go to [render.com](https://render.com)
2. Sign up with GitHub (easiest option)
3. Connect your GitHub account

## Step 3: Deploy with Blueprint (1 min)

1. In Render Dashboard, click **"New +"** → **"Blueprint"**
2. Select your `ai-content-agent` repository
3. Render will read `render.yaml` and create the service automatically
4. Click **"Apply"**

## Step 4: Add Environment Variables (1 min)

After service is created:

1. Click on your service → **"Environment"** tab
2. Add **ONE required variable**:
   - `OPENAI_API_KEY` = `sk-your-key-here` ✅ (check "Secret")
3. Click **"Save Changes"**

**Note:** All other variables have defaults in `render.yaml`

## Step 5: Verify (30 sec)

Once deployment completes (2-3 minutes):

```bash
# Test health endpoint
curl https://ai-content-agent.onrender.com/api/health

# Open in browser
https://ai-content-agent.onrender.com
```

---

## ✅ That's It!

Your AI Content Agent is now live at:
- **URL**: `https://ai-content-agent.onrender.com`
- **API**: `https://ai-content-agent.onrender.com/api/*`
- **Frontend**: `https://ai-content-agent.onrender.com/`

---

## 📝 Optional: Custom Domain

1. Go to service → **"Settings"** → **"Custom Domains"**
2. Add your domain (e.g., `ai.yourdomain.com`)
3. Update DNS as instructed
4. Free SSL certificate included!

---

## 🔧 Optional: Google Sheets Integration

If you want to use Google Sheets for topics:

1. In Render Dashboard → **"Environment"** → **"Secret Files"**
2. Add file: `client_secret.json` (paste your Google OAuth JSON)
3. Add file: `token.pickle` (upload your token file)
4. Redeploy

Or skip it - the app works fine with JSON library only.

---

## 💰 Cost

- **Free Tier**: $0/month (sleeps after 15 min inactivity)
- **Starter**: $7/month (always on, recommended)
- **Standard**: $25/month (more resources)

Start with Free tier for testing!

---

## 🆘 Troubleshooting

### Build Failed?
- Check logs in Render Dashboard → Logs tab
- Ensure `Dockerfile` is in repo root
- Verify all dependencies in `requirements.txt`

### CORS Errors?
- Update `app.py` with your Render URL:
  ```python
  allowed_origins = [
      'https://ai-content-agent.onrender.com',
      # ... other origins
  ]
  ```
- Push changes, Render auto-deploys

### Service Slow?
- Free tier sleeps after inactivity
- First request takes 15-30 seconds (cold start)
- Upgrade to Starter plan ($7/month) for always-on

---

## 📚 Full Documentation

For detailed information, see **RENDER_DEPLOYMENT_GUIDE.md**

---

**Happy Deploying! 🎉**

