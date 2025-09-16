# 🚀 AI Content Agent - Railway Deployment Guide

## 📋 **Pre-Deployment Checklist**

### ✅ **Required Files (Already Created)**
- `Procfile` - Tells Railway how to run your app
- `runtime.txt` - Specifies Python version
- `.gitignore` - Excludes unnecessary files
- `requirements.txt` - Python dependencies
- `app.py` - Updated for production deployment

### ✅ **Required Environment Variables**
You'll need to set these in Railway dashboard:

```bash
# OpenAI API Key (Required)
OPENAI_API_KEY=your_openai_api_key_here

# Google Sheets IDs (Required)
GOOGLE_SHEETS_TOPICS_ID=12qFx-0Si0-g8Hp_yq7sIm7I5gJiACaOaLep04dSYC_U
GOOGLE_SHEETS_PROMPTS_ID=1MIS7Nl1AdTy7mjwKaIDCBV820bXZteHvdIxo8WETYnc

# Feature Flags (Optional - defaults shown)
USE_JSON_LIBRARY=true
FALLBACK_TO_SHEETS=true

# Flask Environment (Optional)
FLASK_ENV=production
```

### ✅ **Required Files to Upload**
Make sure these files are in your repository:
- `client_secret.json` (Google OAuth credentials)
- `Barrana-Merged-Prompt-Library-v3.1.json`
- `barrana_rag_corpus.jsonl` (if using RAG system)
- `barrana_rag_manifest.json` (if using RAG system)

---

## 🚀 **Railway Deployment Steps**

### **Step 1: Prepare Your Repository**

1. **Commit all changes:**
   ```bash
   git add .
   git commit -m "Add Railway deployment configuration"
   git push origin main
   ```

2. **Verify files are present:**
   ```bash
   ls -la
   # Should see: Procfile, runtime.txt, .gitignore
   ```

### **Step 2: Create Railway Account**

1. Go to [railway.app](https://railway.app)
2. Sign up with GitHub
3. Authorize Railway to access your repositories

### **Step 3: Deploy Your App**

1. **Click "New Project"**
2. **Select "Deploy from GitHub repo"**
3. **Choose your repository:** `ai-content-agent`
4. **Railway will auto-detect:** Python application
5. **Click "Deploy Now"**

### **Step 4: Configure Environment Variables**

1. **Go to your project dashboard**
2. **Click on your service**
3. **Go to "Variables" tab**
4. **Add each environment variable:**

   | Variable Name | Value | Required |
   |---------------|-------|----------|
   | `OPENAI_API_KEY` | `your_actual_openai_key` | ✅ Yes |
   | `GOOGLE_SHEETS_TOPICS_ID` | `12qFx-0Si0-g8Hp_yq7sIm7I5gJiACaOaLep04dSYC_U` | ✅ Yes |
   | `GOOGLE_SHEETS_PROMPTS_ID` | `1MIS7Nl1AdTy7mjwKaIDCBV820bXZteHvdIxo8WETYnc` | ✅ Yes |
   | `USE_JSON_LIBRARY` | `true` | ⚠️ Optional |
   | `FALLBACK_TO_SHEETS` | `true` | ⚠️ Optional |
   | `FLASK_ENV` | `production` | ⚠️ Optional |

### **Step 5: Deploy Frontend (React App)**

#### **Option A: Deploy to Vercel (Recommended)**

1. **Go to [vercel.com](https://vercel.com)**
2. **Import your repository**
3. **Set build settings:**
   - **Root Directory:** `ai-content-agent-ui`
   - **Build Command:** `npm run build`
   - **Output Directory:** `build`

4. **Add environment variable:**
   - `REACT_APP_API_URL` = `https://your-railway-app-url.railway.app`

5. **Update your React app's API calls:**
   ```javascript
   // In your React components
   const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:5050';
   ```

#### **Option B: Deploy to Railway (Alternative)**

1. **Create new Railway service**
2. **Select "Deploy from GitHub repo"**
3. **Choose same repository**
4. **Set root directory:** `ai-content-agent-ui`
5. **Add environment variable:**
   - `REACT_APP_API_URL` = `https://your-backend-url.railway.app`

---

## 🔧 **Post-Deployment Configuration**

### **Step 1: Test Your Backend**

1. **Get your Railway URL:** `https://your-app-name.railway.app`
2. **Test health endpoint:** `https://your-app-name.railway.app/api/health`
3. **Test topics endpoint:** `https://your-app-name.railway.app/api/topics`

### **Step 2: Update Frontend API URL**

If deploying frontend separately, update the API URL in your React app:

```javascript
// In ai-content-agent-ui/src/App.js or similar
const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:5050';
```

### **Step 3: Test Google Sheets Integration**

1. **Upload `client_secret.json`** to your repository
2. **First API call will generate `token.pickle`** automatically
3. **Verify topics are loading** from Google Sheets

---

## 🚨 **Troubleshooting**

### **Common Issues:**

#### **1. CORS Errors**
- **Problem:** Frontend can't connect to backend
- **Solution:** Update CORS origins in `app.py` with your frontend URL

#### **2. Environment Variables Not Working**
- **Problem:** API keys not found
- **Solution:** Check Railway Variables tab, ensure exact variable names

#### **3. Google Sheets Authentication**
- **Problem:** `client_secret.json` not found
- **Solution:** Ensure file is committed to repository

#### **4. Port Issues**
- **Problem:** App not starting
- **Solution:** Railway sets `PORT` environment variable automatically

### **Debug Commands:**

```bash
# Check Railway logs
railway logs

# Check environment variables
railway variables

# Restart service
railway redeploy
```

---

## 📊 **Monitoring & Maintenance**

### **Health Check Endpoints:**
- **Health:** `https://your-app.railway.app/api/health`
- **System Info:** `https://your-app.railway.app/api/system-info`

### **Railway Dashboard:**
- **Monitor:** CPU, Memory, Network usage
- **Logs:** Real-time application logs
- **Metrics:** Request count, response times

### **Cost Management:**
- **Free Tier:** $5/month after free credits
- **Production:** $5-20/month depending on usage
- **Monitor:** Usage in Railway dashboard

---

## 🎯 **Next Steps After Deployment**

1. **Test all platforms** with your deployed app
2. **Set up custom domain** (optional)
3. **Configure monitoring** and alerts
4. **Set up automated backups** for Google Sheets data
5. **Consider Redis** for session management if needed

---

## 📞 **Support**

- **Railway Docs:** [docs.railway.app](https://docs.railway.app)
- **Railway Discord:** [discord.gg/railway](https://discord.gg/railway)
- **Your App Health:** `https://your-app.railway.app/api/health`

---

**🎉 Congratulations! Your AI Content Agent is now deployed and ready for production use!**