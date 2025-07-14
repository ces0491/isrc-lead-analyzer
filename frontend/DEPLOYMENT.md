# Prism Analytics Engine - Render Deployment Guide

## Prerequisites

1. **Render Account**: Sign up at [render.com](https://render.com)
2. **GitHub Repository**: Your code should be in a GitHub repository
3. **API Keys**: Gather your API keys for:
   - Spotify Web API (Client ID & Secret)
   - YouTube Data API v3 Key
   - Last.fm API Key (optional)

## Step 1: Fix Build Issues

### Replace Files

1. **Update requirements.txt** with the fixed version (handles lxml compilation issues)
2. **Add runtime.txt** to specify Python 3.11.7
3. **Update render.yaml** with the corrected configuration

### Test Locally First

```bash
# Test the fixed requirements
pip install -r requirements.txt
python wsgi.py
```

## Step 2: Deploy Backend (API)

### Option A: Using render.yaml (Recommended)

1. **Push Changes to GitHub**:
   ```bash
   git add .
   git commit -m "Fix: Update requirements for Render deployment"
   git push origin main
   ```

2. **Create Service on Render**:
   - Go to [Render Dashboard](https://dashboard.render.com)
   - Click "New +" → "Blueprint"
   - Connect your GitHub repository
   - Select the `render.yaml` file

### Option B: Manual Setup

1. **Create PostgreSQL Database**:
   - New + → PostgreSQL
   - Name: `isrc-analyzer-postgres`
   - Plan: Starter (Free)

2. **Create Web Service**:
   - New + → Web Service
   - Connect GitHub repository
   - Settings:
     - **Name**: `isrc-analyzer-api`
     - **Runtime**: Python 3
     - **Build Command**: 
       ```bash
       pip install --upgrade pip setuptools wheel && pip install --no-cache-dir -r requirements.txt
       ```
     - **Start Command**: 
       ```bash
       gunicorn --bind 0.0.0.0:$PORT --workers 2 --timeout 120 wsgi:app
       ```

3. **Configure Environment Variables**:
   ```
   FLASK_ENV=production
   FLASK_DEBUG=false
   DATABASE_URL=<from_database>
   SPOTIFY_CLIENT_ID=<your_spotify_client_id>
   SPOTIFY_CLIENT_SECRET=<your_spotify_client_secret>
   YOUTUBE_API_KEY=<your_youtube_api_key>
   LASTFM_API_KEY=<your_lastfm_api_key>
   SECRET_KEY=<auto_generated>
   CORS_ORIGINS=https://your-frontend-app.onrender.com
   CONTACT_EMAIL=contact@precise.digital
   ```

## Step 3: Deploy Frontend

### Create Static Site

1. **Create New Static Site**:
   - New + → Static Site
   - Connect GitHub repository
   - **Root Directory**: `frontend`
   - **Build Command**: 
     ```bash
     npm ci && REACT_APP_API_BASE_URL=https://isrc-analyzer-api.onrender.com/api npm run build
     ```
   - **Publish Directory**: `build`

2. **Environment Variables**:
   ```
   REACT_APP_API_BASE_URL=https://isrc-analyzer-api.onrender.com/api
   REACT_APP_PRISM_ENVIRONMENT=production
   REACT_APP_VERSION=1.0.0
   REACT_APP_COMPANY_NAME=Precise Digital
   REACT_APP_APP_NAME=Prism Analytics Engine
   ```

## Step 4: Update CORS Configuration

Once your frontend is deployed, update the backend CORS settings:

1. Go to your API service environment variables
2. Update `CORS_ORIGINS` to include your frontend URL:
   ```
   CORS_ORIGINS=https://your-frontend-name.onrender.com,http://localhost:3000
   ```

## Step 5: Database Initialization

The database will auto-initialize on first run via the `wsgi.py` file, but you can manually trigger it if needed:

1. Go to your API service
2. Open the Shell tab
3. Run:
   ```python
   from config.database import init_db
   init_db()
   ```

## Step 6: Test Deployment

### Backend Health Check
```bash
curl https://isrc-analyzer-api.onrender.com/api/status
```

### Frontend Access
Visit your frontend URL and test:
1. Dashboard loads
2. ISRC analysis works
3. System status shows "SYSTEM ONLINE"

## Troubleshooting

### Build Failures

1. **lxml compilation errors**:
   - Use the updated requirements.txt with compatible versions
   - Ensure Python 3.11.7 via runtime.txt

2. **Memory issues during build**:
   - Add to build command: `pip install --no-cache-dir`
   - Use wheels instead of source packages

3. **Database connection issues**:
   - Check DATABASE_URL environment variable
   - Ensure PostgreSQL service is running

### Runtime Issues

1. **CORS errors**:
   - Update CORS_ORIGINS with correct frontend URL
   - Check browser network tab for specific errors

2. **API key issues**:
   - Verify all API keys are set in environment variables
   - Test keys individually via Settings page

3. **500 errors**:
   - Check service logs in Render dashboard
   - Look for Python exceptions in logs

## Post-Deployment Setup

### API Keys Configuration

1. **Spotify API**:
   - Go to [Spotify Developer Dashboard](https://developer.spotify.com/dashboard)
   - Add your backend URL to redirect URIs

2. **YouTube API**:
   - Go to [Google Cloud Console](https://console.cloud.google.com)
   - Enable YouTube Data API v3
   - Add HTTP referrer restrictions if needed

3. **Last.fm API** (Optional):
   - Go to [Last.fm API](https://www.last.fm/api/account/create)
   - No additional configuration needed

### DNS & Custom Domain (Optional)

1. **Custom Domain**:
   - Add custom domain in Render dashboard
   - Update CORS_ORIGINS to include custom domain

2. **SSL Certificate**:
   - Automatically provided by Render
   - Verify HTTPS works for both frontend and backend

## Monitoring & Maintenance

### Health Monitoring

1. **Backend Health**: `https://your-api.onrender.com/api/status`
2. **Database**: Monitor via Render PostgreSQL dashboard
3. **API Usage**: Track via service metrics

### Logs

1. **Backend Logs**: Available in Render service dashboard
2. **Error Tracking**: Consider adding Sentry integration
3. **Performance**: Monitor response times and memory usage

### Scaling

1. **Database**: Upgrade PostgreSQL plan for more storage/connections
2. **API**: Upgrade web service plan for more CPU/memory
3. **Frontend**: Static sites scale automatically

## Security Checklist

- ✅ All API keys stored as environment variables
- ✅ CORS properly configured
- ✅ HTTPS enforced
- ✅ Database credentials secure
- ✅ No sensitive data in frontend code
- ✅ Rate limiting enabled

## Production URLs

After deployment, your URLs will be:
- **Frontend**: `https://your-frontend-name.onrender.com`
- **Backend API**: `https://your-api-name.onrender.com/api`
- **Database**: Internal connection via DATABASE_URL

## Support

If you encounter issues:
1. Check Render service logs
2. Verify environment variables
3. Test API endpoints individually
4. Check GitHub repository for latest updates