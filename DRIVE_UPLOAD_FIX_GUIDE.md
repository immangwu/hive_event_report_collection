# 🔧 COMPLETE FIX FOR GOOGLE DRIVE UPLOAD ISSUE

## ❌ Current Problem
**Service Accounts CANNOT upload to Personal Google Drive folders!**

Error: "Service Accounts cannot own files in personal Google Drives"

## ✅ Solution Options (Choose ONE)

---

## 🎯 OPTION 1: Use Shared Drive (RECOMMENDED for Institutions)

### Why This Works
- Shared Drives (Team Drives) are designed for Service Accounts
- No quota limitations
- Institutional standard
- No re-authentication needed

### Setup Steps

1. **Create a Shared Drive** (Admin Required)
   - Go to Google Drive (drive.google.com)
   - Click "Shared drives" in left sidebar
   - Click "New" → Create new shared drive
   - Name it: "IIC Event Reports"

2. **Share with Service Account**
   - Open the Shared Drive
   - Click "Manage members"
   - Add email: `iicreport@iicreports.iam.gserviceaccount.com`
   - Set permission: **"Content Manager"** or **"Manager"**
   - Click "Send"

3. **Get Shared Drive Folder ID**
   - Create a folder inside the Shared Drive called "Event Reports"
   - Open the folder
   - Copy ID from URL: `https://drive.google.com/drive/folders/FOLDER_ID_HERE`

4. **Update Your Config**
   ```toml
   # In .streamlit/secrets.toml
   DRIVE_PARENT_FOLDER_ID = "PASTE_SHARED_DRIVE_FOLDER_ID_HERE"
   ```

5. **Done!** Your app will now upload successfully without re-authentication.

---

## 🎯 OPTION 2: Switch to OAuth User Authentication (Personal Drive)

### Why This Works
- Uses YOUR personal Google account
- Can upload to your personal drive
- One-time setup, stores refresh token

### Setup Steps

1. **Download client_secret.json** (if you don't have it)
   - Go to: https://console.cloud.google.com/apis/credentials?project=iicreports
   - Click "CREATE CREDENTIALS" → "OAuth 2.0 Client ID"
   - Application type: **Desktop app**
   - Name: "IIC Report Desktop Auth"
   - Click "Create"
   - Download JSON → Rename to `client_secret.json`
   - Place in your app directory

2. **Run One-Time Authentication Script**
   
   Run the script I created for you:

   ```bash
   python setup_oauth.py
   ```
   - Browser will open
   - Login with your Google account
   - Click "Allow" for all permissions
   - Script will save credentials

3. **Restart your Streamlit app**

---

## 🎯 OPTION 3: Hybrid Approach (Best of Both)

I have updated your `utils.py` to automatically handle this!

It now works like this:
1.  **Tries OAuth (token.pickle)**: If you ran `setup_oauth.py`, it uses this (Best for Personal Drive).
2.  **Tries Secrets**: If deployed to cloud with OAuth secrets.
3.  **Falls back to Service Account**: Works for Sheets, but Drive uploads will fail unless you use a Shared Drive.
4.  **Interactive Fallback**: If allowed, prompts for login.

---

## 📋 Quick Comparison

| Method | Best For | Pros | Cons |
|--------|----------|------|------|
| **Shared Drive** | Institutions | No re-auth, unlimited | Needs admin |
| **OAuth** | Personal use | Easy, personal drive | One-time setup |
| **Hybrid** | Flexibility | Best of both | More complex |

---

## 🚀 Recommended Path (Step-by-Step)

### For Your Institution (BEST):

1. **Ask your IT admin** to create a Shared Drive
2. Share it with: `iicreport@iicreports.iam.gserviceaccount.com`
3. Update `DRIVE_PARENT_FOLDER_ID` with the Shared Drive folder ID
4. **Done!** No more authentication issues

### If You Can't Get Shared Drive:

1. Run `python setup_oauth.py`
2. Login once with your Google account
3. **Done!** Token is saved, no more logins needed

---

## ⚠️ Important Notes

### Service Account Limitations:
- ❌ Cannot upload to personal drives
- ✅ CAN upload to Shared Drives
- ✅ CAN access Google Sheets (even personal)

### OAuth (User Credentials):
- ✅ Can upload to personal drives
- ✅ Can access everything you own
- ⚠️ Requires one-time browser login
- ✅ Refresh token works forever (until revoked)
