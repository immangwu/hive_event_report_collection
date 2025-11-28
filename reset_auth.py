import os
import pickle
import toml
import sys
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build

# Force stdout to flush
sys.stdout.reconfigure(line_buffering=True)

print("--- 🔄 RESETTING AUTHENTICATION FROM SCRATCH ---")

# 1. Configuration
SCOPES = [
    'https://www.googleapis.com/auth/spreadsheets',
    'https://www.googleapis.com/auth/drive'
]
CLIENT_SECRET_FILE = 'client_secret.json'
TOKEN_PICKLE_FILE = 'token.pickle'
SECRETS_FILE = '.streamlit/secrets.toml'

# 2. Pre-check
if not os.path.exists(CLIENT_SECRET_FILE):
    print(f"❌ CRITICAL ERROR: {CLIENT_SECRET_FILE} is missing!")
    print("Please download it from Google Cloud Console and place it in this folder.")
    sys.exit(1)

# 3. Clean Slate - Remove old tokens
if os.path.exists(TOKEN_PICKLE_FILE):
    print(f"🗑️  Deleting old {TOKEN_PICKLE_FILE}...")
    os.remove(TOKEN_PICKLE_FILE)
else:
    print(f"ℹ️  No existing {TOKEN_PICKLE_FILE} found.")

# 4. Perform Fresh Login
print("🚀 Launching Browser for Google Login...")
print("👉 Please select the Google Account you want to use for Drive/Sheets.")
print("👉 If asked, click 'Advanced' -> 'Go to <App Name> (unsafe)' to proceed.")
print("👉 Make sure to check ALL boxes to grant permissions.")

try:
    flow = InstalledAppFlow.from_client_secrets_file(
        CLIENT_SECRET_FILE, SCOPES)
    
    # prompt='consent' forces a new refresh token to be generated
    creds = flow.run_local_server(port=0, prompt='consent', access_type='offline')
    
    print("✅ Login Successful!")
    
except Exception as e:
    print(f"❌ Login Failed: {e}")
    sys.exit(1)

# 5. Save to token.pickle (Local Dev)
print(f"💾 Saving to {TOKEN_PICKLE_FILE}...")
with open(TOKEN_PICKLE_FILE, 'wb') as token:
    pickle.dump(creds, token)

# 6. Save to secrets.toml (Headless / Cloud)
print(f"💾 Saving to {SECRETS_FILE}...")
os.makedirs(".streamlit", exist_ok=True)

current_secrets = {}
if os.path.exists(SECRETS_FILE):
    try:
        current_secrets = toml.load(SECRETS_FILE)
    except Exception as e:
        print(f"⚠️  Warning: Could not load existing secrets: {e}")

# Update with new OAuth info
current_secrets["google_oauth"] = {
    "refresh_token": creds.refresh_token,
    "client_id": creds.client_id,
    "client_secret": creds.client_secret,
    "token_uri": creds.token_uri
}

try:
    with open(SECRETS_FILE, "w") as f:
        toml.dump(current_secrets, f)
    print("✅ Secrets updated successfully.")
except Exception as e:
    print(f"❌ Failed to save secrets.toml: {e}")

# 7. Verify Connection
print("🧪 Verifying Drive Connection...")
try:
    service = build('drive', 'v3', credentials=creds)
    # Try to list 1 file to prove it works
    results = service.files().list(pageSize=1, fields="nextPageToken, files(id, name)").execute()
    items = results.get('files', [])
    print("✅ CONNECTION VERIFIED! Google Drive is accessible.")
    if not items:
        print("   (Drive is empty, but connection works)")
    else:
        print(f"   (Found file: {items[0]['name']})")
        
    print("\n🎉 SETUP COMPLETE! You can now restart your Streamlit app.")
    print("   Run: streamlit run app.py")
    
except Exception as e:
    print(f"❌ Connection Verification Failed: {e}")
