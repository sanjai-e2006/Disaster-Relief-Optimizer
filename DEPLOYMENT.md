# 🚀 Deployment Guide - Disaster Relief Optimizer

## 📌 Quick Deployment to Streamlit Community Cloud (FREE)

### Step 1: Push to GitHub

1. **Create a GitHub account** (if you don't have one): https://github.com/join

2. **Create a new repository** on GitHub:
   - Go to: https://github.com/new
   - Repository name: `disaster-relief-optimizer`
   - Description: `AI-powered disaster relief resource allocation system`
   - Make it **Public**
   - Don't initialize with README (we already have one)
   - Click **Create repository**

3. **Push your code to GitHub**:
   ```powershell
   cd "d:\project\AI project\disaster-relief-optimizer"
   git remote add origin https://github.com/YOUR_USERNAME/disaster-relief-optimizer.git
   git branch -M main
   git push -u origin main
   ```

### Step 2: Deploy to Streamlit Cloud

1. **Go to Streamlit Cloud**: https://share.streamlit.io/

2. **Sign in with GitHub** (use same account as Step 1)

3. **Click "New app"**

4. **Fill in the deployment form**:
   - **Repository**: Select `YOUR_USERNAME/disaster-relief-optimizer`
   - **Branch**: `main`
   - **Main file path**: `dashboard_working.py`
   - **App URL**: Choose a custom URL (e.g., `disaster-relief-optimizer`)

5. **Add Secrets** (if using real Supabase):
   - Click "Advanced settings"
   - Add your Supabase credentials:
     ```toml
     SUPABASE_URL = "your-supabase-url"
     SUPABASE_KEY = "your-supabase-key"
     ```

6. **Click "Deploy!"**

7. **Wait 2-3 minutes** for deployment to complete

8. **Your app will be live at**: `https://YOUR_APP_NAME.streamlit.app`

---

## 🌐 Alternative Deployment Options

### Option 2: Deploy to Heroku

1. **Install Heroku CLI**: https://devcenter.heroku.com/articles/heroku-cli

2. **Create required files**:

   **Procfile**:
   ```
   web: sh setup.sh && streamlit run dashboard_working.py
   ```

   **setup.sh**:
   ```bash
   mkdir -p ~/.streamlit/
   echo "\
   [server]\n\
   headless = true\n\
   port = $PORT\n\
   enableCORS = false\n\
   \n\
   " > ~/.streamlit/config.toml
   ```

3. **Deploy**:
   ```bash
   heroku login
   heroku create your-app-name
   git push heroku main
   heroku open
   ```

### Option 3: Deploy to Railway.app

1. Go to: https://railway.app/
2. Sign in with GitHub
3. Click "New Project" → "Deploy from GitHub repo"
4. Select your repository
5. Railway will auto-detect Streamlit
6. Click "Deploy"

### Option 4: Deploy to Render.com

1. Go to: https://render.com/
2. Sign up/Login
3. Click "New +" → "Web Service"
4. Connect your GitHub repository
5. Configure:
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `streamlit run dashboard_working.py --server.port $PORT --server.address 0.0.0.0`
6. Click "Create Web Service"

---

## 🔐 Environment Variables Setup

For production deployment with real Supabase:

1. **In Streamlit Cloud**:
   - Go to App settings → Secrets
   - Add:
     ```toml
     SUPABASE_URL = "your-url"
     SUPABASE_KEY = "your-key"
     ```

2. **In code** (already configured in `src/auth.py`):
   - The app uses `os.getenv()` to read environment variables
   - Falls back to demo mode if not provided

---

## 📊 Post-Deployment Checklist

- [ ] App loads without errors
- [ ] Authentication system works
- [ ] Can make predictions
- [ ] Resource allocation displays correctly
- [ ] Inventory management functional
- [ ] Analytics page loads
- [ ] All navigation buttons work
- [ ] Demo accounts work
- [ ] Supabase connection (if configured)

---

## 🐛 Troubleshooting

### Common Issues:

**1. App won't start**
   - Check `requirements.txt` has correct versions
   - Verify `dashboard_working.py` is the main file
   - Check logs in Streamlit Cloud dashboard

**2. Authentication not working**
   - Verify Supabase credentials in secrets
   - Check demo mode is enabled as fallback
   - Review `src/auth.py` configuration

**3. Data not loading**
   - Ensure `data/disaster_data.csv` is committed to Git
   - Check file paths are relative, not absolute
   - Verify data directory exists

**4. Port errors**
   - Streamlit Cloud handles ports automatically
   - For self-hosting, use `--server.port $PORT`

---

## 🎉 Success!

Your Disaster Relief Optimizer is now deployed and accessible worldwide!

**Next Steps:**
- Share your app URL
- Monitor usage in Streamlit Cloud dashboard
- Add custom domain (paid feature)
- Enable authentication for production users
- Collect user feedback

---

## 📧 Support

- **Streamlit Docs**: https://docs.streamlit.io/streamlit-community-cloud
- **Streamlit Forum**: https://discuss.streamlit.io/
- **GitHub Issues**: Open issues in your repository

---

**Built with ❤️ for humanitarian aid**
