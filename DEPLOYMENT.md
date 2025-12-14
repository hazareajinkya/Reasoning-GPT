# Deployment Guide

This guide will help you deploy Reasoning GPT to free hosting platforms.

## 🎯 Recommended Setup

- **Frontend**: Vercel (Free tier, perfect for Next.js)
- **Backend**: Railway (Free $5 credit/month) or Render (Free tier with sleep)

---

## 📋 Prerequisites

1. GitHub account (✅ You already have this!)
2. Vercel account (free): https://vercel.com/signup
3. Railway account (free): https://railway.app/signup
4. Your OpenAI API keys (keep them safe!)

---

## 🚀 Step 1: Deploy Backend (Railway)

### Option A: Railway (Recommended)

1. **Go to Railway**: https://railway.app
2. **Sign up** with GitHub
3. **Create New Project** → "Deploy from GitHub repo"
4. **Select your repo**: `hazareajinkya/Reasoning-GPT`
5. **Configure Service**:
   - **Root Directory**: Leave empty (or set to `/`)
   - **Start Command**: `cd backend && uvicorn app:app --host 0.0.0.0 --port $PORT`
   - **Python Version**: 3.11 or 3.12

6. **Set Environment Variables** (in Railway dashboard):
   ```
   EMBED_API_URL=https://api.openai.com/v1/embeddings
   EMBED_API_KEY=sk-your-actual-key-here
   EMBED_MODEL=text-embedding-3-large
   LLM_API_URL=https://api.openai.com/v1/chat/completions
   LLM_API_KEY=sk-your-actual-key-here
   LLM_MODEL=gpt-4o-mini
   PYTHONPATH=/app
   ```

7. **Add requirements.txt** (Railway auto-detects Python projects)
   - Railway will automatically install dependencies from `requirements.txt`

8. **Deploy**:
   - Railway will build and deploy automatically
   - Wait for deployment to complete (~2-3 minutes)
   - **Copy your backend URL** (e.g., `https://your-app.railway.app`)

### Option B: Render (Alternative)

1. **Go to Render**: https://render.com
2. **Sign up** with GitHub
3. **New** → **Web Service**
4. **Connect GitHub repo**: `hazareajinkya/Reasoning-GPT`
5. **Settings**:
   - **Name**: `reasoning-gpt-backend`
   - **Environment**: Python 3
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `cd backend && uvicorn app:app --host 0.0.0.0 --port $PORT`

6. **Environment Variables** (same as Railway above)

7. **Deploy** and copy your backend URL

---

## 🎨 Step 2: Deploy Frontend (Vercel)

1. **Go to Vercel**: https://vercel.com
2. **Sign up** with GitHub
3. **Add New Project** → **Import Git Repository**
4. **Select**: `hazareajinkya/Reasoning-GPT`
5. **Configure Project**:
   - **Framework Preset**: Next.js (auto-detected)
   - **Root Directory**: `frontend`
   - **Build Command**: `npm run build` (default)
   - **Output Directory**: `.next` (default)

6. **Environment Variables** (in Vercel dashboard):
   ```
   NEXT_PUBLIC_API_URL=https://your-backend-url.railway.app
   ```
   ⚠️ **Important**: Replace `your-backend-url.railway.app` with your actual Railway backend URL

7. **Deploy**:
   - Vercel will build and deploy automatically
   - Wait for deployment (~1-2 minutes)
   - **Copy your frontend URL** (e.g., `https://reasoning-gpt.vercel.app`)

---

## 🔧 Step 3: Update Frontend to Use Backend URL

After deploying, you need to update the frontend to use your production backend URL.

### Option 1: Update via Vercel Environment Variables

1. Go to Vercel dashboard → Your project → Settings → Environment Variables
2. Add: `NEXT_PUBLIC_API_URL=https://your-backend.railway.app`
3. Redeploy (Vercel will auto-redeploy)

### Option 2: Update Code (if needed)

If your frontend code uses `localhost:8000`, update it to use the environment variable:

```typescript
// In frontend/app/page.tsx or wherever you make API calls
const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';
```

---

## 🔒 Security Checklist

✅ **API Keys Secured**:
- ✅ Removed from `start_backend.sh`
- ✅ Removed from `test_api_simple.py`
- ✅ Added to `.gitignore`
- ✅ Using environment variables only

✅ **Environment Variables**:
- ✅ Set in Railway/Render dashboard (backend)
- ✅ Set in Vercel dashboard (frontend)
- ✅ Never commit `.env` files

---

## 🧪 Testing Your Deployment

1. **Test Backend**:
   ```bash
   curl https://your-backend.railway.app/health
   ```

2. **Test Frontend**:
   - Visit your Vercel URL
   - Try solving a problem
   - Check browser console for errors

---

## 💰 Cost Estimates

### Free Tier Limits:

**Vercel**:
- ✅ Unlimited deployments
- ✅ 100GB bandwidth/month
- ✅ Perfect for frontend hosting

**Railway**:
- ✅ $5 free credit/month
- ✅ ~$0.01-0.02 per solution
- ✅ ~250-500 solutions/month free

**Render**:
- ✅ Free tier (sleeps after 15 min inactivity)
- ✅ Wakes up on first request (~30s delay)
- ✅ Good for low-traffic apps

---

## 🐛 Troubleshooting

### Backend Issues:

1. **"Module not found"**:
   - Check `requirements.txt` includes all dependencies
   - Railway/Render installs from `requirements.txt`

2. **"Port not found"**:
   - Use `$PORT` environment variable (Railway/Render provides this)
   - Command: `uvicorn app:app --host 0.0.0.0 --port $PORT`

3. **"API key not set"**:
   - Double-check environment variables in Railway/Render dashboard
   - Make sure variable names match exactly (case-sensitive)

### Frontend Issues:

1. **"Cannot connect to backend"**:
   - Check `NEXT_PUBLIC_API_URL` in Vercel environment variables
   - Make sure backend URL is correct (no trailing slash)
   - Check CORS settings in backend (should allow your Vercel domain)

2. **CORS Errors**:
   - Update `backend/app.py` CORS settings to include your Vercel domain:
   ```python
   allow_origins=[
       "http://localhost:3000",
       "https://your-app.vercel.app",  # Add your Vercel URL
   ]
   ```

---

## 📝 Next Steps

1. ✅ Deploy backend to Railway
2. ✅ Deploy frontend to Vercel
3. ✅ Update CORS settings in backend
4. ✅ Test the full application
5. 🎉 Share your app with users!

---

## 🔗 Useful Links

- **Railway Docs**: https://docs.railway.app
- **Vercel Docs**: https://vercel.com/docs
- **Render Docs**: https://render.com/docs
- **Your GitHub Repo**: https://github.com/hazareajinkya/Reasoning-GPT

---

## 💡 Pro Tips

1. **Monitor Costs**: Check Railway/Render usage dashboard regularly
2. **Set Up Alerts**: Configure spending limits if available
3. **Use Cheaper Models**: Consider Groq/DeepSeek for lower costs
4. **Rate Limiting**: Add rate limiting to prevent abuse (future enhancement)
5. **Custom Domain**: Add custom domain in Vercel for professional look

---

**Need Help?** Check the troubleshooting section or open an issue on GitHub!

