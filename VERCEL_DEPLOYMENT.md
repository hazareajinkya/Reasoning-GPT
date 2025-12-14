# Vercel Frontend Deployment Guide

Complete guide to deploy the Next.js frontend on Vercel.

## Prerequisites

- ✅ Railway backend deployed and working
- ✅ Railway backend URL (e.g., `https://your-app.up.railway.app`)
- ✅ GitHub account
- ✅ Vercel account (free)

---

## Step 1: Sign Up for Vercel

1. Go to https://vercel.com
2. Click **"Sign Up"**
3. Choose **"Continue with GitHub"**
4. Authorize Vercel to access your GitHub account

---

## Step 2: Import Your Repository

1. After signing in, click **"Add New..."** → **"Project"**
2. You'll see a list of your GitHub repositories
3. Find **"Reasoning-GPT"** and click **"Import"**

---

## Step 3: Configure Project Settings

Vercel will auto-detect Next.js, but verify these settings:

### Project Settings:
- **Framework Preset**: Next.js (auto-detected)
- **Root Directory**: `frontend` ⚠️ **IMPORTANT: Set this to `frontend`**
- **Build Command**: `npm run build` (default, should be auto-filled)
- **Output Directory**: `.next` (default, should be auto-filled)
- **Install Command**: `npm install` (default)

### How to Set Root Directory:
1. Click **"Edit"** next to "Root Directory"
2. Type: `frontend`
3. Click **"Continue"**

---

## Step 4: Add Environment Variable

**This is the most important step!**

1. Before deploying, scroll down to **"Environment Variables"** section
2. Click **"Add"** or **"Add Variable"**
3. Add this variable:

```
Variable Name: NEXT_PUBLIC_API_URL
Value: https://your-railway-backend-url.up.railway.app
```

⚠️ **Replace `https://your-railway-backend-url.up.railway.app` with your actual Railway backend URL!**

**How to get your Railway URL:**
1. Go to your Railway project dashboard
2. Click on your service
3. Go to **"Settings"** tab
4. Find **"Public Domain"** or **"Networking"** section
5. Copy the URL (format: `https://your-app-name.up.railway.app`)

**Important Notes:**
- ✅ Use `https://` (not `http://`)
- ✅ Don't add trailing slash (`/`)
- ✅ The variable name must be exactly: `NEXT_PUBLIC_API_URL`
- ✅ In Next.js, environment variables starting with `NEXT_PUBLIC_` are exposed to the browser

---

## Step 5: Deploy

1. Click **"Deploy"** button
2. Wait 1-2 minutes for the build to complete
3. Vercel will show build logs in real-time
4. Once complete, you'll see **"Congratulations! Your project has been deployed"**

---

## Step 6: Get Your Frontend URL

After deployment:

1. Vercel will show your deployment URL
2. Format: `https://reasoning-gpt.vercel.app` (or similar)
3. **Save this URL** - this is your live frontend!

---

## Step 7: Test Your Deployment

1. Open your Vercel URL in a browser
2. Try solving a problem
3. Check browser console (F12) for any errors
4. Verify it connects to your Railway backend

**If you see connection errors:**
- Check that `NEXT_PUBLIC_API_URL` is set correctly in Vercel
- Verify your Railway backend is running (test `/health` endpoint)
- Check CORS settings in backend (should allow all origins by default)

---

## Step 8: Update Backend CORS (If Needed)

Your backend should already allow all origins, but if you want to restrict it:

1. Go to Railway dashboard
2. Add environment variable:
   ```
   CORS_ORIGINS=https://your-vercel-app.vercel.app
   ```
3. Redeploy backend

---

## Troubleshooting

### Problem: Build fails with "Module not found"
**Solution:**
- Verify Root Directory is set to `frontend`
- Check that `package.json` exists in `frontend/` directory
- Ensure all dependencies are in `package.json`

### Problem: "Cannot connect to backend"
**Solution:**
- Verify `NEXT_PUBLIC_API_URL` is set in Vercel environment variables
- Check the URL is correct (no trailing slash, uses https)
- Test Railway backend URL directly: `https://your-backend.railway.app/health`
- Check browser console for specific error messages

### Problem: CORS errors
**Solution:**
- Backend should allow all origins by default
- If restricted, add your Vercel URL to `CORS_ORIGINS` in Railway
- Check backend logs in Railway for CORS errors

### Problem: Build succeeds but app doesn't work
**Solution:**
- Check Vercel deployment logs for runtime errors
- Verify environment variable is set (check in Vercel dashboard)
- Test Railway backend is accessible
- Check browser console for client-side errors

---

## Environment Variables Reference

### Required for Vercel:
```
NEXT_PUBLIC_API_URL=https://your-railway-backend.up.railway.app
```

### Optional (for custom domain):
```
NEXT_PUBLIC_SITE_URL=https://your-custom-domain.com
```

---

## Custom Domain (Optional)

To add a custom domain:

1. Go to Vercel project → **"Settings"** → **"Domains"**
2. Click **"Add Domain"**
3. Enter your domain name
4. Follow DNS configuration instructions
5. Wait for DNS propagation (can take up to 24 hours)

---

## Auto-Deploy

Vercel automatically deploys when you push to GitHub:
- ✅ Push to `main` branch → Production deployment
- ✅ Push to other branches → Preview deployment

**To trigger manual redeploy:**
1. Go to Vercel dashboard
2. Click on your project
3. Go to **"Deployments"** tab
4. Click **"Redeploy"** on latest deployment

---

## Success Checklist

Before marking deployment as complete:

- [ ] Vercel project created and connected to GitHub
- [ ] Root directory set to `frontend`
- [ ] `NEXT_PUBLIC_API_URL` environment variable set with Railway backend URL
- [ ] Build completed successfully
- [ ] Frontend URL is accessible
- [ ] Can solve problems (connects to Railway backend)
- [ ] No errors in browser console
- [ ] No CORS errors

---

## Quick Reference

**Vercel Dashboard**: https://vercel.com/dashboard  
**Your Repository**: https://github.com/hazareajinkya/Reasoning-GPT  
**Railway Backend**: Your Railway URL (from Railway dashboard)

**Frontend URL Format**: `https://reasoning-gpt-xxxxx.vercel.app`  
**Backend URL Format**: `https://your-app-name.up.railway.app`

---

## Next Steps After Deployment

1. ✅ Test the full application flow
2. ✅ Share your Vercel URL with users
3. ⏳ Set up custom domain (optional)
4. ⏳ Add analytics (optional)
5. ⏳ Set up monitoring (optional)

---

**Congratulations!** Your frontend is now live on Vercel! 🎉

