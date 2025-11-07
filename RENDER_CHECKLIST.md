# ✅ Render Deployment Checklist

Use this checklist to ensure a smooth deployment to Render.

## 📋 Pre-Deployment

### Code Preparation
- [ ] All code changes committed to Git
- [ ] Test locally with `python app.py` (backend should start on port 5050)
- [ ] React build exists (`ai-content-agent-ui/build/`) or can be built
- [ ] `.env` file created with `OPENAI_API_KEY` for local testing
- [ ] `.env` file is in `.gitignore` (DO NOT commit to Git)
- [ ] Run `./test-deployment.sh` - all checks pass

### Files Verification
- [ ] `app.py` - Flask application with React serving route
- [ ] `requirements.txt` - All Python dependencies listed
- [ ] `Dockerfile` - Docker configuration exists
- [ ] `render.yaml` - Render Blueprint configuration
- [ ] `ai-content-agent-ui/package.json` - React dependencies
- [ ] `README_RENDER.md` - Deployment documentation
- [ ] `.gitignore` - Excludes sensitive files

### Required Files (Must Exist)
- [ ] `Barrana-Merged-Prompt-Library-v3.1.json`
- [ ] `comments-engine.json`
- [ ] `barrana_rag_corpus.jsonl`
- [ ] `barrana_rag_manifest.json`
- [ ] `prompt_library.py`
- [ ] `validation.py`
- [ ] `seo_manager.py`
- [ ] `rag_system.py`

### Optional Files (For Google Sheets)
- [ ] `client_secret.json` (will upload to Render separately)
- [ ] `token.pickle` (will upload to Render separately)
- [ ] Or set `FALLBACK_TO_SHEETS=false` to disable

---

## 🚀 Deployment Steps

### Step 1: GitHub Setup
- [ ] Create GitHub repository (if not exists)
- [ ] Add remote: `git remote add origin <url>`
- [ ] Push code: `git push -u origin main`
- [ ] Verify all files are on GitHub (check in browser)

### Step 2: Render Account
- [ ] Sign up at [render.com](https://render.com)
- [ ] Connect GitHub account
- [ ] Verify email address

### Step 3: Create Service (Blueprint Method)
- [ ] Go to Render Dashboard
- [ ] Click **"New +"** → **"Blueprint"**
- [ ] Select your `ai-content-agent` repository
- [ ] Review the `render.yaml` configuration
- [ ] Click **"Apply"**
- [ ] Service will be created automatically

### Step 4: Environment Variables
- [ ] Go to service → **"Environment"** tab
- [ ] Add `OPENAI_API_KEY` = `sk-your-actual-key-here`
- [ ] Mark `OPENAI_API_KEY` as **"Secret"** (check the box)
- [ ] Verify other variables have defaults from `render.yaml`:
  - `PORT` = `5050`
  - `FLASK_ENV` = `production`
  - `USE_JSON_LIBRARY` = `true`
  - `FALLBACK_TO_SHEETS` = `true`
- [ ] Click **"Save Changes"**

### Step 5: Google Sheets (Optional)
If using Google Sheets integration:
- [ ] Go to **"Environment"** → **"Secret Files"**
- [ ] Add file: `client_secret.json`
- [ ] Paste Google OAuth JSON content
- [ ] Add file: `token.pickle`
- [ ] Upload token file content
- [ ] Save changes

If NOT using Google Sheets:
- [ ] Set `FALLBACK_TO_SHEETS=false` in environment variables
- [ ] Or simply skip this step (app will log warning but work fine)

### Step 6: Wait for Build
- [ ] Watch **"Logs"** tab for build progress
- [ ] Build takes 3-5 minutes
- [ ] Look for: "Build successful"
- [ ] Look for: "Live" status (green indicator)
- [ ] Note your service URL (e.g., `https://ai-content-agent.onrender.com`)

---

## ✅ Post-Deployment Verification

### Health Checks
```bash
# Replace with your actual Render URL
export RENDER_URL="https://ai-content-agent.onrender.com"

# Test health endpoint
curl $RENDER_URL/api/health
# Should return: {"status": "healthy", ...}

# Test system info
curl $RENDER_URL/api/system-info
# Should return: {"version": "2.0.0", ...}

# Test platforms endpoint
curl $RENDER_URL/api/platforms
# Should return: [{"key": "linkedin", ...}, ...]
```

- [ ] Health endpoint returns `200 OK`
- [ ] System info shows correct version
- [ ] Platforms list has 7+ platforms
- [ ] No error messages in response

### Frontend Verification
- [ ] Open `https://your-app.onrender.com` in browser
- [ ] Page loads without errors (check browser console)
- [ ] UI displays correctly
- [ ] Topics dropdown populated
- [ ] Platforms checkboxes visible
- [ ] "Generate Content" button present

### Full Integration Test
- [ ] Select a topic from dropdown
- [ ] Check 2-3 platforms (e.g., LinkedIn, Instagram)
- [ ] Click **"Generate Content"**
- [ ] Wait 30-60 seconds (GPT-4 is slow)
- [ ] Content appears for each platform
- [ ] Quality metrics shown (word count, CTA, etc.)
- [ ] Engagement comments visible (15-20 comments)
- [ ] Comments show 6 personas (A, B, C, D, E, Barrana)
- [ ] Comments are threaded (replies indented)
- [ ] No error messages

### CORS Configuration
If frontend is on different domain:
- [ ] Update `app.py` → `allowed_origins` with your Render URL
- [ ] Commit and push changes
- [ ] Render auto-redeploys
- [ ] Verify CORS errors are gone

---

## 🔧 Configuration Options

### Custom Domain (Optional)
- [ ] Go to service → **"Settings"** → **"Custom Domains"**
- [ ] Click **"Add Custom Domain"**
- [ ] Enter domain (e.g., `ai.yourdomain.com`)
- [ ] Update DNS records as instructed
- [ ] Wait for SSL certificate (automatic, ~5 minutes)
- [ ] Verify domain works with HTTPS

### Upgrade Plan (Recommended)
- [ ] Go to service → **"Settings"** → **"Plan"**
- [ ] Upgrade from Free to Starter ($7/month)
- [ ] Benefit: No cold starts, always on
- [ ] Free tier sleeps after 15 min inactivity

### Auto-Deploy
- [ ] Go to service → **"Settings"**
- [ ] Verify **"Auto-Deploy"** is enabled (should be by default)
- [ ] Now git push automatically triggers deployment

---

## 📊 Monitoring Setup

### Render Dashboard
- [ ] Bookmark your service dashboard URL
- [ ] Check **"Metrics"** tab (CPU, Memory, Requests)
- [ ] Monitor **"Logs"** tab for errors
- [ ] Set up email alerts (optional)

### Health Monitoring (Optional)
- [ ] Set up external monitoring (e.g., UptimeRobot)
- [ ] Monitor: `https://your-app.onrender.com/api/health`
- [ ] Check interval: Every 5 minutes
- [ ] Alert on failure

---

## 🐛 Troubleshooting Checklist

If something goes wrong:

### Build Fails
- [ ] Check **"Logs"** tab for specific error
- [ ] Verify `Dockerfile` syntax is correct
- [ ] Ensure `requirements.txt` has all dependencies
- [ ] Test Docker build locally: `docker build -t test .`
- [ ] Check that all Python files are pushed to GitHub

### Service Won't Start
- [ ] Verify `OPENAI_API_KEY` is set
- [ ] Check logs for Python import errors
- [ ] Ensure `app.py` uses `PORT` env variable
- [ ] Test locally: `python app.py`

### Health Check Fails
- [ ] Check if Flask is listening on `0.0.0.0:5050`
- [ ] Verify route is defined: `@app.route('/api/health')`
- [ ] Test locally: `curl http://localhost:5050/api/health`

### Frontend 404 Error
- [ ] Verify React build is in Docker image
- [ ] Check `serve_react()` route in `app.py`
- [ ] Ensure `send_from_directory` is imported
- [ ] Check path: `ai-content-agent-ui/build/`

### CORS Errors
- [ ] Add Render URL to `allowed_origins` in `app.py`
- [ ] Format: `'https://your-app.onrender.com'`
- [ ] No trailing slash
- [ ] Redeploy after changing

### Slow Response / Cold Starts
- [ ] Upgrade to Starter plan ($7/month)
- [ ] Or create cron job to ping every 14 minutes
- [ ] Free tier sleeps after 15 min inactivity

### OpenAI API Errors
- [ ] Verify API key is correct (no spaces)
- [ ] Check OpenAI account has credits
- [ ] Verify key is marked as "Secret" in Render
- [ ] Test key locally: `curl https://api.openai.com/v1/models -H "Authorization: Bearer $OPENAI_API_KEY"`

---

## 📝 Maintenance Checklist

### Weekly
- [ ] Check Render dashboard for errors
- [ ] Monitor OpenAI API usage/costs
- [ ] Review application logs
- [ ] Test content generation still works

### Monthly
- [ ] Update dependencies: `pip list --outdated`
- [ ] Check for security updates
- [ ] Review and optimize costs
- [ ] Backup prompt library and configurations

### As Needed
- [ ] Update prompt library
- [ ] Add new platforms
- [ ] Adjust word counts
- [ ] Update SEO keywords

---

## 🎉 Success!

Once all items are checked:
- ✅ Service is deployed and healthy
- ✅ Frontend loads correctly
- ✅ Content generation works
- ✅ Engagement comments appear
- ✅ Monitoring is set up
- ✅ Team has access

**You're live on Render! 🚀**

---

## 📚 Documentation Links

- [RENDER_QUICK_START.md](./RENDER_QUICK_START.md) - 5-minute quick start
- [RENDER_DEPLOYMENT_GUIDE.md](./RENDER_DEPLOYMENT_GUIDE.md) - Comprehensive guide
- [README_RENDER.md](./README_RENDER.md) - Project overview
- [Render Documentation](https://render.com/docs)

---

## 📞 Getting Help

If stuck:
1. Check logs in Render Dashboard → Logs tab
2. Review [RENDER_DEPLOYMENT_GUIDE.md](./RENDER_DEPLOYMENT_GUIDE.md) troubleshooting section
3. Test locally with Docker: `docker build -t test . && docker run -p 5050:5050 test`
4. Contact Render support: [Discord](https://discord.gg/render)
5. Review this checklist - something might be missed

---

**Last Updated:** November 2025  
**Version:** 1.0

