# 🚀 Streamlit Cloud Deployment - Step by Step

## Prerequisites
- GitHub account
- Your code pushed to a GitHub repository

---

## Step 1: Create requirements.txt ✅
**Status:** Already created in the root directory

The file includes:
- streamlit
- pandas
- openpyxl
- weasyprint
- markdown

---

## Step 2: Push Your Code to GitHub

### If you don't have a GitHub repo yet:

1. **Create a new repository on GitHub:**
   - Go to [github.com](https://github.com)
   - Click "New repository"
   - Name it (e.g., `portland-thorns-scouting`)
   - Choose Public or Private
   - **Don't** initialize with README (you already have files)

2. **Push your code:**
   ```bash
   cd "/Users/daniel/Documents/Smart Sports Lab/Football/Sports Data Campus/Portland Thorns/Data/Advanced Search"
   
   # Initialize git if not already done
   git init
   git add .
   git commit -m "Initial commit: Portland Thorns scouting app"
   
   # Add your GitHub repo as remote (replace with your actual repo URL)
   git remote add origin https://github.com/YOUR_USERNAME/YOUR_REPO_NAME.git
   git branch -M main
   git push -u origin main
   ```

### If you already have a GitHub repo:

```bash
cd "/Users/daniel/Documents/Smart Sports Lab/Football/Sports Data Campus/Portland Thorns/Data/Advanced Search"
git add .
git commit -m "Add Streamlit app and requirements"
git push origin main
```

---

## Step 3: Deploy to Streamlit Cloud

1. **Go to Streamlit Cloud:**
   - Visit [share.streamlit.io](https://share.streamlit.io)
   - Sign in with your GitHub account (authorize if prompted)

2. **Create New App:**
   - Click the **"New app"** button
   - You'll see a form with these fields:

3. **Fill in the deployment form:**
   - **Repository:** Select your GitHub repository
   - **Branch:** `main` (or `master` if that's your default branch)
   - **Main file path:** `Scripts/00_Keep/qualitative_capture_app.py`
   - **App URL:** Choose a custom subdomain (e.g., `portland-thorns-scouting`)

4. **Click "Deploy!"**
   - Streamlit Cloud will:
     - Clone your repository
     - Install dependencies from `requirements.txt`
     - Launch your app
     - Provide a public URL

---

## Step 4: Access Your Deployed App

- You'll get a URL like: `https://portland-thorns-scouting.streamlit.app`
- Share this URL with your colleague
- They can access it from anywhere, no setup needed!

---

## Step 5: Auto-Deploy on Updates

- Every time you push changes to GitHub, Streamlit Cloud will automatically redeploy
- You'll see a notification in the Streamlit Cloud dashboard
- The app updates within 1-2 minutes

---

## Troubleshooting

### If deployment fails:
1. Check the logs in Streamlit Cloud dashboard
2. Verify `requirements.txt` has all dependencies
3. Ensure the main file path is correct
4. Check that all file paths in your code are relative (not absolute)

### File Path Issues:
- The app uses absolute paths like `/Users/daniel/...`
- For Streamlit Cloud, you may need to adjust paths to be relative
- Or use environment variables for base paths

---

## Next Steps After Deployment

1. **Test the app** using the provided URL
2. **Share the URL** with your colleague
3. **Monitor usage** in the Streamlit Cloud dashboard
4. **Update as needed** - just push to GitHub!

---

## Important Notes

⚠️ **Data Files:**
- Streamlit Cloud doesn't persist data between deployments
- Your CSV files in `Qualitative_Data/` won't be available unless you:
  - Commit them to GitHub (not recommended for sensitive data)
  - Use a database (PostgreSQL, MySQL, etc.)
  - Use cloud storage (S3, Google Cloud Storage, etc.)

💡 **For Production:**
- Consider moving data storage to a cloud database
- Use environment variables for sensitive configuration
- Set up proper authentication if needed

