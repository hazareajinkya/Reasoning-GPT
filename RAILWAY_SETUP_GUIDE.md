# Railway Deployment Setup Guide for AI Assistant

This guide is for an AI assistant (like ChatGPT) to help complete the Railway deployment setup.

## Current Status
- ✅ Railway account created
- ✅ Project created on Railway
- ✅ GitHub repository connected: https://github.com/hazareajinkya/Reasoning-GPT.git
- ⏳ Need to complete: Environment variables, deployment configuration, and testing

---

## Step-by-Step Instructions for AI Assistant

### Step 1: Verify Project Setup
**Action**: Guide the user to verify their Railway project is set up correctly.

**Instructions to give user**:
1. Go to https://railway.app/dashboard
2. Click on your project (should be named "Reasoning-GPT" or similar)
3. Verify you see a service/deployment in the project
4. Check if there's a "Deployments" tab showing build activity

**What to check**:
- Is the project connected to the GitHub repo?
- Is there a service/deployment visible?
- Are there any build logs or errors?

---

### Step 2: Configure Environment Variables
**Action**: Help the user add all required environment variables to Railway.

**Instructions to give user**:
1. In your Railway project, click on the service (the deployment)
2. Go to the **"Variables"** tab
3. Click **"New Variable"** for each of the following:

**Required Variables** (add these one by one):

```
Variable Name: EMBED_API_URL
Value: https://api.openai.com/v1/embeddings
```

```
Variable Name: EMBED_API_KEY
Value: [Ask user for their OpenAI API key for embeddings]
```

```
Variable Name: EMBED_MODEL
Value: text-embedding-3-large
```

```
Variable Name: LLM_API_URL
Value: https://api.openai.com/v1/chat/completions
```

```
Variable Name: LLM_API_KEY
Value: [Ask user for their OpenAI API key for LLM - can be same as EMBED_API_KEY]
```

```
Variable Name: LLM_MODEL
Value: gpt-4o-mini
```

```
Variable Name: PYTHONPATH
Value: /app
```

**Important Notes**:
- Ask the user for their actual OpenAI API keys (they should have them from their local setup)
- Warn them NOT to share keys in public - only enter in Railway dashboard
- If they're using the same OpenAI account, they can use the same key for both EMBED_API_KEY and LLM_API_KEY
- The $PORT variable is automatically provided by Railway - don't add it manually

---

### Step 3: Verify Start Command
**Action**: Ensure the start command is correctly configured.

**Instructions to give user**:
1. In Railway, go to your service
2. Click on **"Settings"** tab
3. Scroll to **"Deploy"** section
4. Check **"Start Command"** field
5. It should be: `cd backend && uvicorn app:app --host 0.0.0.0 --port $PORT`
6. If it's different or empty, update it to the above command

**Alternative**: The `railway.json` file in the repo should auto-configure this, but verify it's correct.

---

### Step 4: Trigger Deployment
**Action**: Ensure the deployment is running or trigger a new one.

**Instructions to give user**:
1. Go to **"Deployments"** tab in Railway
2. If there's no active deployment, click **"Redeploy"** or **"Deploy"**
3. Watch the build logs - it should show:
   - Installing Python dependencies
   - Building the application
   - Starting the server
4. Wait 2-3 minutes for deployment to complete

**What to look for in logs**:
- ✅ "Installing dependencies from requirements.txt"
- ✅ "Starting uvicorn"
- ✅ "Application startup complete"
- ❌ Any errors about missing modules or API keys

---

### Step 5: Get Public URL
**Action**: Help user find and copy their Railway backend URL.

**Instructions to give user**:
1. In Railway, go to your service
2. Click on **"Settings"** tab
3. Scroll to **"Networking"** or **"Domains"** section
4. Find **"Public Domain"** or **"Generate Domain"** button
5. Click **"Generate Domain"** if no domain exists
6. Copy the URL (format: `https://your-app-name.up.railway.app`)
7. Save this URL - it's your backend API endpoint

**Note**: Railway automatically generates a domain, but you may need to click "Generate Domain" first.

---

### Step 6: Test the Backend
**Action**: Verify the backend is working correctly.

**Instructions to give user**:
1. Open a new browser tab
2. Go to: `https://your-railway-url.up.railway.app/health`
   (Replace with your actual Railway URL)
3. You should see a JSON response like:
   ```json
   {
     "status": "ok",
     "items": 31,
     "store_loaded": true,
     ...
   }
   ```

**Alternative test with curl** (if user has terminal access):
```bash
curl https://your-railway-url.up.railway.app/health
```

**What success looks like**:
- ✅ Returns JSON with status "ok"
- ✅ Shows number of items in vector store
- ✅ Shows api_keys_configured: true

**If it fails**:
- Check Railway logs for errors
- Verify environment variables are set correctly
- Check if deployment completed successfully

---

### Step 7: Update CORS (If Needed)
**Action**: Ensure backend allows requests from frontend (will be deployed on Vercel).

**Instructions to give user**:
1. The backend code already has CORS configured to allow all origins (`*`)
2. This is fine for now - it will work with Vercel frontend
3. For production, you can restrict CORS later by setting `CORS_ORIGINS` environment variable

**Optional - Restrict CORS later**:
- Add environment variable: `CORS_ORIGINS=https://your-vercel-app.vercel.app`
- This will only allow requests from your specific frontend domain

---

## Troubleshooting Guide for AI Assistant

### Problem: Build fails with "Module not found"
**Solution**:
- Check that `requirements.txt` exists in the root directory
- Verify all dependencies are listed in requirements.txt
- Check Railway logs for specific missing module
- Guide user to add missing dependency to requirements.txt

### Problem: Service won't start
**Solution**:
- Check start command is correct: `cd backend && uvicorn app:app --host 0.0.0.0 --port $PORT`
- Verify environment variables are set (especially API keys)
- Check logs for specific error messages
- Ensure PYTHONPATH is set to `/app`

### Problem: Health check returns error
**Solution**:
- Check if all environment variables are set
- Verify API keys are correct (not placeholder values)
- Check Railway logs for runtime errors
- Ensure vector store file exists (data/vector_store_dilr.pkl)

### Problem: "API key not set" error
**Solution**:
- Verify EMBED_API_KEY and LLM_API_KEY are set in Railway variables
- Check that variable names match exactly (case-sensitive)
- Ensure values don't have extra spaces or quotes
- Re-deploy after adding variables

### Problem: Deployment stuck or taking too long
**Solution**:
- Check Railway status page for service issues
- Try redeploying the service
- Check if there are resource limits (free tier has limits)
- Review build logs for any hanging processes

---

## Next Steps After Backend is Deployed

Once the backend is working:
1. ✅ Save the Railway backend URL
2. ⏳ Deploy frontend on Vercel (separate guide)
3. ⏳ Connect frontend to backend URL
4. ⏳ Test full application

---

## Quick Reference Commands

**Railway CLI** (optional - if user wants to use CLI):
```bash
# Install Railway CLI
npm i -g @railway/cli

# Login
railway login

# Link project
railway link

# Set variables
railway variables set EMBED_API_KEY=sk-xxx
railway variables set LLM_API_KEY=sk-xxx

# Deploy
railway up
```

**But web dashboard is easier for beginners!**

---

## Checklist for AI Assistant

Before marking deployment as complete, verify:
- [ ] All environment variables are set
- [ ] Start command is configured correctly
- [ ] Deployment completed successfully (green status)
- [ ] Public URL is generated and accessible
- [ ] Health check endpoint returns success
- [ ] User has saved their Railway backend URL
- [ ] No errors in Railway logs

---

## Important Notes for AI Assistant

1. **Never ask user to share API keys in chat** - they should only enter them in Railway dashboard
2. **Railway free tier** has $5 credit/month - warn user about usage limits
3. **Vector store file** (data/vector_store_dilr.pkl) is large - ensure it's committed to Git
4. **Deployment time** - first deployment takes 2-3 minutes, be patient
5. **Auto-deploy** - Railway auto-deploys on Git push, but can manually redeploy

---

## Success Criteria

The backend deployment is successful when:
- ✅ Health endpoint returns 200 OK with status "ok"
- ✅ All environment variables are configured
- ✅ No errors in Railway deployment logs
- ✅ Public URL is accessible
- ✅ User has the backend URL saved for frontend deployment

---

**End of Guide** - Use this to systematically help the user complete Railway deployment.

