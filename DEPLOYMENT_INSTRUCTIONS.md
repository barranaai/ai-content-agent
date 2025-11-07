# AI Content Agent - Deployment Instructions for Hostinger

## 📦 Deployment Package
**File:** `ai-content-agent-deployment-20251010_145514.tar.gz` (711KB)

## 🎯 What's New in This Update

### New Features
- **Comments Engine System**: Generates 15-20 threaded comments with 6 distinct personas
- **6 Personas**: Person A (Curious), Person B (Skeptic), Person C (Insider), Person D (Amplifier), Person E (Cheerleader), and Barrana
- **Threaded Conversations**: Comments can reply to each other with proper nesting
- **Platform-Specific**: Different tones and timing for LinkedIn, Instagram, Facebook, TikTok
- **Enhanced UI**: Color-coded personas with icons and visual threading

### Updated Files
1. **Backend:**
   - `prompt_library.py` - Added comments-engine integration (253 new lines)
   - `comments-engine.json` - New configuration file (281 lines)
   - `app.py` - Already compatible with new format
   - `Barrana-Merged-Prompt-Library-v3.1.json` - Existing prompt library

2. **Frontend:**
   - `ai-content-agent-ui/build/` - Updated React production build
   - New threaded comment display components
   - Color-coded persona visualization

## 🚀 Deployment Steps

### Step 1: Upload the Deployment Package
```bash
# From your local machine
scp ai-content-agent-deployment-20251010_145514.tar.gz root@srv653791.hstgr.cloud:/tmp/
```

### Step 2: Connect to the Server
```bash
ssh root@srv653791.hstgr.cloud
```

### Step 3: Backup Current Installation
```bash
cd /root/ai-content-agent
tar -czf backup-$(date +%Y%m%d_%H%M%S).tar.gz \
  prompt_library.py \
  app.py \
  Barrana-Merged-Prompt-Library-v3.1.json

# Backup frontend
cd /home/public_html/ai-content-agent/ai-content-agent-ui
tar -czf build-backup-$(date +%Y%m%d_%H%M%S).tar.gz build/
```

### Step 4: Extract New Files
```bash
# Extract backend files
cd /root/ai-content-agent
tar -xzf /tmp/ai-content-agent-deployment-20251010_145514.tar.gz \
  prompt_library.py \
  comments-engine.json \
  app.py \
  Barrana-Merged-Prompt-Library-v3.1.json

# Extract frontend build
cd /home/public_html/ai-content-agent/ai-content-agent-ui
tar -xzf /tmp/ai-content-agent-deployment-20251010_145514.tar.gz \
  --strip-components=2 ai-content-agent-ui/build
```

### Step 5: Verify Files
```bash
cd /root/ai-content-agent
ls -lh prompt_library.py comments-engine.json

cd /home/public_html/ai-content-agent/ai-content-agent-ui/build
ls -lh static/js/main.*.js
```

### Step 6: Restart Flask Backend
```bash
cd /root/ai-content-agent

# Find and kill existing Flask process
ps aux | grep "python.*app.py" | grep -v grep
kill -9 <PID>

# Start Flask in background
nohup python3 app.py > flask.log 2>&1 &

# Verify it's running
sleep 3
curl http://localhost:5050/api/health
```

### Step 7: Reload Nginx
```bash
# Test Nginx configuration
nginx -t

# Reload Nginx (no downtime)
systemctl reload nginx

# Verify Nginx is serving the new build
curl -I http://localhost:5051/ai-content-agent/
```

### Step 8: Test the Deployment
```bash
# Test backend engagement endpoint
curl -X POST http://localhost:5050/api/generate-content \
  -H "Content-Type: application/json" \
  -d '{
    "topic": "AI automation for restaurants",
    "description": "How AI helps restaurants reduce costs",
    "platforms": ["instagram"],
    "prompts": {}
  }' | jq '.content.instagram.engagement.meta'

# Check frontend (from browser)
# Visit: http://191.101.233.56:5051/ai-content-agent/
```

## ✅ Verification Checklist

After deployment, verify:

- [ ] Flask backend is running on port 5050
- [ ] Nginx is serving frontend on port 5051
- [ ] `/api/health` endpoint returns `{"status": "healthy"}`
- [ ] `comments-engine.json` file exists in `/root/ai-content-agent/`
- [ ] Frontend displays new threaded comment format
- [ ] Generate content for Instagram/Facebook/LinkedIn/TikTok shows 15-20 comments
- [ ] Comments show 6 different personas with color coding
- [ ] Threaded replies are properly nested
- [ ] Save functionality includes threaded comments

## 🔄 Rollback Instructions (If Needed)

If something goes wrong, rollback to previous version:

```bash
# Stop Flask
pkill -f "python.*app.py"

# Restore backend files
cd /root/ai-content-agent
tar -xzf backup-YYYYMMDD_HHMMSS.tar.gz

# Restore frontend
cd /home/public_html/ai-content-agent/ai-content-agent-ui
rm -rf build
tar -xzf build-backup-YYYYMMDD_HHMMSS.tar.gz

# Restart services
cd /root/ai-content-agent
nohup python3 app.py > flask.log 2>&1 &
systemctl reload nginx
```

## 📋 Post-Deployment Notes

### Performance Considerations
- The new system generates 15-20 comments (vs previous 5-7)
- Each request may take 30-60 seconds due to GPT-4 generation
- Consider implementing caching for frequently used topics

### Monitoring
- Check Flask logs: `tail -f /root/ai-content-agent/flask.log`
- Check Nginx logs: `tail -f /var/log/nginx/error.log`
- Monitor OpenAI API usage (increased due to more comments)

### Future Enhancements
- Add loading indicators for long generation times
- Implement comment generation retry logic
- Add admin panel to configure comment count range
- Export comments in CSV format with timing delays

## 🆘 Troubleshooting

### Issue: Comments not showing new format
**Solution:** Clear browser cache and hard refresh (Ctrl+Shift+R)

### Issue: "Comments engine not loaded" error
**Solution:** Verify `comments-engine.json` exists in `/root/ai-content-agent/`

### Issue: Only 11 comments instead of 15-20
**Solution:** This is expected if GPT-4 doesn't follow requirements. Check logs for warnings.

### Issue: Flask not starting
**Solution:** Check `flask.log` for errors. Ensure all dependencies are installed: `pip install -r requirements.txt`

## 📞 Support

If issues persist after deployment:
1. Check `/root/ai-content-agent/flask.log` for backend errors
2. Check browser console for frontend errors
3. Verify `comments-engine.json` is valid JSON: `python3 -m json.tool comments-engine.json`
4. Test prompt_library loading: `python3 -c "from prompt_library import BarranaPromptLibrary; lib = BarranaPromptLibrary(); print('OK')"`

---

**Deployment Package Created:** October 10, 2025 - 14:55
**Package Size:** 711KB
**Estimated Deployment Time:** 5-10 minutes

