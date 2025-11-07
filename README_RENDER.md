# 🚀 AI Content Agent - Render Deployment

[![Deploy to Render](https://render.com/images/deploy-to-render-button.svg)](https://render.com/deploy)

A powerful AI-powered content generation platform with support for multiple social media platforms (LinkedIn, Twitter, Instagram, Facebook, TikTok, YouTube) and blog content.

## 🎯 What This App Does

- **Multi-Platform Content Generation**: Generate optimized content for 7+ platforms
- **AI-Powered**: Uses GPT-4 for high-quality content generation
- **SEO Optimized**: Built-in keyword optimization and rotation
- **Engagement System**: Generates realistic threaded comments (15-20 per post)
- **Quality Metrics**: Tracks word count, CTA inclusion, keyword usage
- **RAG Enhancement**: Context-aware content using Barrana's knowledge base
- **Google Sheets Integration**: Import topics from spreadsheets (optional)

## 📦 Tech Stack

**Backend:**
- Python 3.11 + Flask
- OpenAI GPT-4 API
- Google Sheets API (optional)

**Frontend:**
- React 19
- Material-UI
- Built with Create React App

**Deployment:**
- Docker containerized
- Render.com platform
- Automatic deployments from Git

## 🚀 Quick Deploy to Render

### 1. Prerequisites
- GitHub account
- Render account (sign up at [render.com](https://render.com))
- OpenAI API key (get one at [platform.openai.com](https://platform.openai.com))

### 2. Deploy Steps

**Option A: Using Blueprint (Recommended)**

1. Push this repo to your GitHub account
2. Go to [Render Dashboard](https://dashboard.render.com)
3. Click **"New +"** → **"Blueprint"**
4. Select your repository
5. Render will read `render.yaml` and set everything up
6. Add environment variable: `OPENAI_API_KEY=sk-your-key-here`
7. Click **"Apply"**
8. Done! 🎉

**Option B: Manual Setup**

1. Push repo to GitHub
2. Go to Render Dashboard → **"New +"** → **"Web Service"**
3. Connect your repository
4. Configure:
   - **Runtime**: Docker
   - **Region**: Choose closest to you
   - **Plan**: Starter ($7/mo) or Free
5. Add environment variables (see below)
6. Click **"Create Web Service"**

### 3. Environment Variables

Add these in Render Dashboard → Your Service → Environment:

| Variable | Value | Required |
|----------|-------|----------|
| `OPENAI_API_KEY` | `sk-...` | ✅ Yes |
| `PORT` | `5050` | No (auto-set) |
| `FLASK_ENV` | `production` | No (default) |
| `USE_JSON_LIBRARY` | `true` | No (default) |
| `FALLBACK_TO_SHEETS` | `true` | No (default) |

### 4. Test Your Deployment

Once deployed (takes 2-3 minutes):

```bash
# Health check
curl https://your-app.onrender.com/api/health

# System info
curl https://your-app.onrender.com/api/system-info

# Open in browser
https://your-app.onrender.com
```

## 📝 Detailed Documentation

- **[RENDER_DEPLOYMENT_GUIDE.md](./RENDER_DEPLOYMENT_GUIDE.md)** - Complete deployment guide with troubleshooting
- **[RENDER_QUICK_START.md](./RENDER_QUICK_START.md)** - 5-minute quick start guide
- **[README.md](./README.md)** - Main project documentation

## 🔧 Local Development

```bash
# Clone repository
git clone https://github.com/YOUR_USERNAME/ai-content-agent.git
cd ai-content-agent

# Setup environment
cp .env.example .env
# Edit .env and add your OPENAI_API_KEY

# Backend
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python app.py

# Frontend (separate terminal)
cd ai-content-agent-ui
npm install
npm start
```

Backend: http://localhost:5050  
Frontend: http://localhost:3000

## 🐳 Docker Deployment

```bash
# Build
docker build -t ai-content-agent .

# Run
docker run -p 5050:5050 \
  -e OPENAI_API_KEY=sk-your-key \
  ai-content-agent

# Access at http://localhost:5050
```

## 🧪 Testing Before Deploy

Run the pre-deployment test script:

```bash
./test-deployment.sh
```

This will check:
- ✅ Required files present
- ✅ Docker build succeeds
- ✅ Health endpoint responds
- ✅ Dependencies installed
- ✅ Git configured
- ✅ Environment variables set

## 📊 Platform Support

| Platform | Content Type | Word Count | Engagement |
|----------|--------------|------------|------------|
| LinkedIn | Professional | 400-700 | ✅ Comments |
| Twitter | Threads | 400-600 | ✅ Comments |
| Instagram | Posts | 300-500 | ✅ Comments |
| Facebook | Posts | 400-600 | ✅ Comments |
| TikTok | Captions | 200-400 | ✅ Comments |
| YouTube | Descriptions | 600-800 | ❌ |
| Blog | Articles | 800-1200 | ❌ |

## 🔒 Security

- ✅ API keys stored as environment variables
- ✅ CORS configured for specific origins
- ✅ Input validation on all endpoints
- ✅ HTTPS enforced (Render provides free SSL)
- ✅ Non-root Docker user
- ✅ Dependencies regularly updated

## 💰 Cost Estimate

**Render Hosting:**
- Free tier: $0/month (sleeps after 15 min)
- Starter: $7/month (recommended)
- Standard: $25/month (high traffic)

**OpenAI API:**
- ~$0.03 per content generation
- ~$0.06 per full platform set (7 platforms)
- Estimated $5-20/month for typical usage

**Total:** ~$12-27/month for Starter plan

## 🐛 Troubleshooting

### Service won't start
- Check logs: Render Dashboard → Logs
- Verify `OPENAI_API_KEY` is set
- Ensure Docker build succeeds

### CORS errors
- Add your Render URL to `allowed_origins` in `app.py`
- Redeploy

### Slow cold starts
- Free tier sleeps after inactivity
- Upgrade to Starter plan ($7/mo)
- Or set up cron job to ping every 14 minutes

### Frontend not loading
- Check that React build is included in Docker image
- Verify `serve_react()` route in `app.py`
- Clear browser cache

See [RENDER_DEPLOYMENT_GUIDE.md](./RENDER_DEPLOYMENT_GUIDE.md) for more troubleshooting.

## 📈 Monitoring

In Render Dashboard you can view:
- CPU and memory usage
- Request logs (live)
- Response times
- Error rates
- Deployment history

## 🔄 CI/CD Workflow

Automatic deployments enabled by default:

```bash
# Make changes
git add .
git commit -m "Update features"
git push origin main

# Render automatically:
# 1. Detects push
# 2. Pulls latest code
# 3. Builds Docker image
# 4. Deploys new version
# 5. Runs health checks
```

## 🌐 Custom Domain

1. Go to Render Dashboard → Your Service → Settings
2. Click **"Custom Domains"**
3. Add domain (e.g., `ai.yourdomain.com`)
4. Update DNS records as shown
5. Free SSL certificate auto-configured

## 📞 Support

- **Render Issues**: [render.com/docs](https://render.com/docs) | [Discord](https://discord.gg/render)
- **App Issues**: Check logs in Render Dashboard
- **API Issues**: Test endpoints with curl/Postman

## 🎉 Success Criteria

After deployment, verify:
- [ ] Service is running (green status in Render)
- [ ] Health endpoint returns 200: `/api/health`
- [ ] Frontend loads in browser
- [ ] Can select topics and platforms
- [ ] Content generation works
- [ ] Engagement comments appear (15-20 threaded)
- [ ] All 7 platforms generate successfully

## 📄 License

This project is private/proprietary. Not for redistribution.

## 🙏 Credits

Built with:
- OpenAI GPT-4
- Flask & React
- Material-UI
- Render.com

---

**Ready to deploy?** See [RENDER_QUICK_START.md](./RENDER_QUICK_START.md) for 5-minute setup!

