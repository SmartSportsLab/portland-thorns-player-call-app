# Streamlit Cloud Deployment Guide

## Step-by-Step Instructions

### Step 1: Prepare Your Repository
1. Make sure all your code is committed to Git
2. Ensure `requirements.txt` exists in the root directory
3. Ensure `.streamlit/config.toml` exists (optional, for configuration)

### Step 2: Push to GitHub
1. If you haven't already, create a GitHub repository
2. Push your code:
   ```bash
   git add .
   git commit -m "Add Streamlit app for Portland Thorns scouting"
   git push origin main
   ```

### Step 3: Set Up Streamlit Cloud
1. Go to [share.streamlit.io](https://share.streamlit.io)
2. Sign in with your GitHub account
3. Click "New app"
4. Select your repository
5. Set the **Main file path** to: `Scripts/00_Keep/qualitative_capture_app.py`
6. Click "Deploy!"

### Step 4: Configure App Settings (if needed)
- The app will automatically install dependencies from `requirements.txt`
- Streamlit Cloud will provide a public URL (e.g., `https://your-app-name.streamlit.app`)

### Step 5: Share with Your Colleague
- Send them the public URL
- They can access the app from anywhere, no setup required!

## Notes
- Streamlit Cloud is free for public repositories
- The app will auto-redeploy when you push changes to GitHub
- Make sure sensitive data (API keys, passwords) are not hardcoded in the app

