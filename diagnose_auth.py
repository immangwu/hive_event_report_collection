import os
import pickle
import sys
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request

# Force stdout to flush
sys.stdout.reconfigure(line_buffering=True)

print("--- AUTH DIAGNOSTIC ---")

SCOPES = [
    'https://www.googleapis.com/auth/spreadsheets',
    'https://www.googleapis.com/auth/drive'
]

client_secret = 'client_secret.json'
token_file = 'token.pickle'

# 1. Check Client Secret
if os.path.exists(client_secret):
    print(f"✅ Found {client_secret}")
    try:
        # Just try to load it to see if JSON is valid
        flow = InstalledAppFlow.from_client_secrets_file(client_secret, SCOPES)
        print("✅ client_secret.json is valid and loadable.")
    except Exception as e:
        print(f"❌ client_secret.json is INVALID: {e}")
        sys.exit(1)
else:
    print(f"❌ MISSING {client_secret}")
    sys.exit(1)

# 2. Check Token
creds = None
if os.path.exists(token_file):
    print(f"ℹ️ Found {token_file}")
    try:
        with open(token_file, 'rb') as token:
            creds = pickle.load(token)
            print("ℹ️ Loaded token.pickle")
    except Exception as e:
        print(f"⚠️ Error loading token.pickle: {e}")

# 3. Validate/Refresh
if creds and creds.valid:
    print("✅ Credentials are VALID.")
else:
    print("ℹ️ Credentials are invalid or expired.")
    if creds and creds.expired and creds.refresh_token:
        print("ℹ️ Attempting refresh...")
        try:
            creds.refresh(Request())
            print("✅ Refresh SUCCESS.")
        except Exception as e:
            print(f"❌ Refresh FAILED: {e}")
    else:
        print("ℹ️ No refresh token available.")

print("--- DIAGNOSTIC COMPLETE ---")
