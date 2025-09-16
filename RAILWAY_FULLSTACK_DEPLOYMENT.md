# 🚀 Railway Full-Stack Deployment Guide
## Deploy Both Backend & Frontend on Railway

---

## 📋 **Overview**

This guide will help you deploy both your **Python Flask backend** and **React frontend** on Railway as separate services within the same project.

---

## 🎯 **Step 1: Deploy Backend Service**

### **1.1 Create Railway Account**
1. Go to [railway.app](https://railway.app)
2. Sign up with GitHub
3. Authorize Railway to access your repositories

### **1.2 Deploy Backend**
1. **Click "New Project"**
2. **Select "Deploy from GitHub repo"**
3. **Choose your repository:** `ai-content-agent`
4. **Railway will auto-detect:** Python application
5. **Click "Deploy Now"**

### **1.3 Configure Backend Environment Variables**
In your backend service dashboard, go to **Variables** tab and add:

| Variable Name | Value | Required |
|---------------|-------|----------|
| `OPENAI_API_KEY` | `your_actual_openai_key` | ✅ Yes |
| `GOOGLE_SHEETS_TOPICS_ID` | `12qFx-0Si0-g8Hp_yq7sIm7I5gJiACaOaLep04dSYC_U` | ✅ Yes |
| `GOOGLE_SHEETS_PROMPTS_ID` | `1MIS7Nl1AdTy7mjwKaIDCBV820bXZteHvdIxo8WETYnc` | ✅ Yes |
| `USE_JSON_LIBRARY` | `true` | ⚠️ Optional |
| `FALLBACK_TO_SHEETS` | `true` | ⚠️ Optional |
| `FLASK_ENV` | `production` | ⚠️ Optional |

### **1.4 Get Backend URL**
After deployment, copy your backend URL (e.g., `https://ai-content-agent-production.railway.app`)

---

## 🎯 **Step 2: Deploy Frontend Service**

### **2.1 Create Frontend Service**
1. **In the same Railway project**, click **"+ New Service"**
2. **Select "Deploy from GitHub repo"**
3. **Choose the same repository:** `ai-content-agent`
4. **Set Root Directory:** `ai-content-agent-ui`
5. **Click "Deploy Now"**

### **2.2 Configure Frontend Environment Variables**
In your frontend service dashboard, go to **Variables** tab and add:

| Variable Name | Value | Required |
|---------------|-------|----------|
| `REACT_APP_API_URL` | `https://your-backend-url.railway.app` | ✅ Yes |
| `NODE_ENV` | `production` | ⚠️ Optional |

**Important:** Replace `your-backend-url` with your actual backend URL from Step 1.4

### **2.3 Configure Build Settings**
In your frontend service settings:
1. **Build Command:** `npm run build`
2. **Start Command:** `npx serve -s build -l $PORT`
3. **Root Directory:** `ai-content-agent-ui`

---

## 🔧 **Step 3: Update Frontend API Configuration**

### **3.1 Update API Base URL**
Your React app needs to know where to find the backend. Update your frontend code:

```javascript
// In ai-content-agent-ui/src/App.js or similar
const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:5050';
```

### **3.2 Update CORS in Backend**
Your backend is already configured to accept requests from Railway domains, but you can add your specific frontend URL:

```python
# In app.py (already configured)
allowed_origins = [
    'http://localhost:3000', 
    'http://localhost:3001',
    'https://ai-content-agent-ui.vercel.app',
    'https://ai-content-agent-frontend.railway.app',
    # Add your specific Railway frontend URL here
]
```

---

## 🧪 **Step 4: Test Your Deployment**

### **4.1 Test Backend**
1. **Health Check:** `https://your-backend-url.railway.app/api/health`
2. **Topics API:** `https://your-backend-url.railway.app/api/topics`
3. **Platforms API:** `https://your-backend-url.railway.app/api/platforms`

### **4.2 Test Frontend**
1. **Visit your frontend URL:** `https://your-frontend-url.railway.app`
2. **Test content generation** with a sample topic
3. **Verify API calls** are working

### **4.3 Test Full Integration**
1. **Select a topic** from the dropdown
2. **Choose platforms** (LinkedIn, Medium, etc.)
3. **Generate content** and verify it works
4. **Check all 21 platforms** are working

---

## 📊 **Railway Project Structure**

After deployment, your Railway project will have:

```
📁 AI Content Agent Project
├── 🐍 Backend Service (Python/Flask)
│   ├── Port: Auto-assigned by Railway
│   ├── URL: https://ai-content-agent-production.railway.app
│   └── Environment: Production Flask app
│
└── ⚛️ Frontend Service (React)
    ├── Port: Auto-assigned by Railway  
    ├── URL: https://ai-content-agent-frontend.railway.app
    └── Environment: Production React app
```

---

## 💰 **Cost Breakdown**

### **Railway Pricing:**
- **Free Tier:** $5/month after free credits
- **Backend Service:** ~$5-10/month
- **Frontend Service:** ~$5-10/month
- **Total:** ~$10-20/month for both services

### **Cost Optimization:**
- Both services can share the same Railway project
- Railway offers volume discounts
- Monitor usage in Railway dashboard

---

## 🔍 **Monitoring & Maintenance**

### **Railway Dashboard Features:**
- **Real-time logs** for both services
- **Resource usage** (CPU, Memory, Network)
- **Deployment history** and rollbacks
- **Environment variable management**
- **Custom domain** setup (optional)

### **Health Monitoring:**
- **Backend Health:** `https://your-backend-url.railway.app/api/health`
- **System Info:** `https://your-backend-url.railway.app/api/system-info`

---

## 🚨 **Troubleshooting**

### **Common Issues:**

#### **1. Frontend Can't Connect to Backend**
- **Problem:** CORS errors or API calls failing
- **Solution:** 
  - Check `REACT_APP_API_URL` environment variable
  - Verify backend URL is correct
  - Check CORS origins in backend

#### **2. Environment Variables Not Working**
- **Problem:** API keys or URLs not found
- **Solution:**
  - Check Railway Variables tab
  - Ensure exact variable names
  - Redeploy after adding variables

#### **3. Build Failures**
- **Problem:** Frontend build failing
- **Solution:**
  - Check build command: `npm run build`
  - Verify start command: `npx serve -s build -l $PORT`
  - Check Node.js version compatibility

#### **4. Google Sheets Authentication**
- **Problem:** `client_secret.json` not found
- **Solution:**
  - Ensure file is committed to repository
  - Check file path in backend

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

## 🎯 **Next Steps After Deployment**

### **Immediate Actions:**
1. **Test all 21 platforms** with your deployed app
2. **Verify Google Sheets integration** is working
3. **Check content generation quality** across platforms
4. **Monitor resource usage** in Railway dashboard

### **Optional Enhancements:**
1. **Set up custom domains** for both services
2. **Configure monitoring alerts** for downtime
3. **Set up automated backups** for Google Sheets data
4. **Add Redis** for session management if needed
5. **Implement CI/CD** for automatic deployments

---

## 📞 **Support Resources**

- **Railway Docs:** [docs.railway.app](https://docs.railway.app)
- **Railway Discord:** [discord.gg/railway](https://discord.gg/railway)
- **Your Backend Health:** `https://your-backend-url.railway.app/api/health`
- **Your Frontend:** `https://your-frontend-url.railway.app`

---

## 🎉 **Success Checklist**

- ✅ Backend deployed and accessible
- ✅ Frontend deployed and accessible  
- ✅ Environment variables configured
- ✅ API communication working
- ✅ Content generation functional
- ✅ All 21 platforms working
- ✅ Google Sheets integration active
- ✅ Health checks passing

---

**🚀 Congratulations! Your AI Content Agent is now fully deployed on Railway with both backend and frontend services!**
