# Troubleshooting Guide - Frontend Backend Connection

## Current Status Check

### ✅ Backend is Working
- Health endpoint: https://reasoning-gpt-production.up.railway.app/health ✅
- Returns: `{"status": "ok", ...}`
- CORS: Configured correctly ✅

### ⚠️ Issues Found
1. **Vector store not loaded** - `items: 0` (this is OK for now, will fix)
2. **API keys not configured** - Need to set in Railway
3. **404 Error** - Frontend can't reach backend

---

## Fix the 404 Error

### Step 1: Verify Environment Variable in Browser

1. Open your Vercel app: https://reasoning-gpt.vercel.app
2. Open Browser Console (F12 → Console tab)
3. Type this and press Enter:
   ```javascript
   console.log('API URL:', process.env.NEXT_PUBLIC_API_URL)
   ```
4. **What do you see?**
   - If it shows `undefined` → Environment variable not set correctly
   - If it shows `https://reasoning-gpt-production.up.railway.app` → Variable is set ✅
   - If it shows `http://localhost:8000` → Variable not loaded, need to redeploy

### Step 2: Check Network Tab

1. Open Browser Console (F12 → Network tab)
2. Try to solve a problem
3. Look for the request to `/health` or `/solve`
4. **Check:**
   - What URL is it trying to call?
   - What's the status code? (404, 500, CORS error?)
   - What's the error message?

### Step 3: Common Issues & Fixes

#### Issue: Environment Variable Shows `undefined`
**Fix:**
1. Go to Vercel → Your Project → Settings → Environment Variables
2. Verify `NEXT_PUBLIC_API_URL` exists
3. Value should be: `https://reasoning-gpt-production.up.railway.app` (no trailing slash!)
4. Make sure it's enabled for "Production"
5. **Redeploy** (go to Deployments → Latest → Redeploy)

#### Issue: Still using `localhost:8000`
**Fix:**
- Vercel needs to rebuild with the environment variable
- Go to Deployments → Click "Redeploy" on latest deployment
- Wait 1-2 minutes for rebuild

#### Issue: CORS Error
**Fix:**
- Backend CORS is already configured ✅
- If you still see CORS errors, check Railway logs

#### Issue: 404 on `/health`
**Fix:**
- Check the exact URL being called
- Should be: `https://reasoning-gpt-production.up.railway.app/health`
- NOT: `https://reasoning-gpt-production.up.railway.app/health/` (trailing slash)
- NOT: `http://reasoning-gpt-production.up.railway.app/health` (missing https)

---

## Fix Railway Issues

### Set API Keys in Railway

1. Go to Railway dashboard
2. Click on your project
3. Go to **Variables** tab
4. Add these variables:

```
EMBED_API_URL = https://api.openai.com/v1/embeddings
EMBED_API_KEY = sk-your-actual-key-here
EMBED_MODEL = text-embedding-3-large
LLM_API_URL = https://api.openai.com/v1/chat/completions
LLM_API_KEY = sk-your-actual-key-here
LLM_MODEL = gpt-4o-mini
PYTHONPATH = /app
```

5. **Redeploy** Railway service

### Verify Vector Store

The vector store file should be in Railway. If `items: 0`:
1. Check Railway logs for errors loading the vector store
2. The file path should be: `/app/data/vector_store_dilr.pkl`
3. If missing, Railway needs to pull latest code from Git

---

## Quick Test Commands

### Test Backend Health
```bash
curl https://reasoning-gpt-production.up.railway.app/health
```

### Test Backend Solve Endpoint
```bash
curl -X POST https://reasoning-gpt-production.up.railway.app/solve \
  -H "Content-Type: application/json" \
  -d '{"question":"test","top_k":4}'
```

### Test from Browser Console
```javascript
// Test health endpoint
fetch('https://reasoning-gpt-production.up.railway.app/health')
  .then(r => r.json())
  .then(console.log)
  .catch(console.error)
```

---

## What to Report

If still not working, please share:

1. **Browser Console Output:**
   - What does `process.env.NEXT_PUBLIC_API_URL` show?
   - Any error messages?

2. **Network Tab:**
   - What URL is the frontend calling?
   - What's the HTTP status code?
   - What's the error message?

3. **Railway Logs:**
   - Any errors in Railway deployment logs?
   - Is the service running?

4. **Vercel Environment Variables:**
   - Is `NEXT_PUBLIC_API_URL` set?
   - What's the value? (you can mask the domain if needed)

---

## Expected Behavior

✅ **Working:**
- Frontend loads at https://reasoning-gpt.vercel.app
- Console shows: `API URL: https://reasoning-gpt-production.up.railway.app`
- Health check succeeds
- Can solve problems

❌ **Not Working:**
- 404 errors
- CORS errors
- "Cannot connect to backend" messages
- Environment variable shows `undefined`

