import os
import pickle
import toml
from google_auth_oauthlib.flow import InstalledAppFlow

# Scopes required
SCOPES = [
    'https://www.googleapis.com/auth/spreadsheets',
    'https://www.googleapis.com/auth/drive'
]

def setup_headless():
    print("--- HEADLESS AUTH SETUP ---")
    print("This script will generate a Refresh Token so users don't have to log in.")
    
    if not os.path.exists('client_secret.json'):
        print("❌ Error: client_secret.json not found!")
        return

    # 1. Run Interactive Login (Force Consent to get Refresh Token)
    print("🚀 Opening browser for ONE-TIME Admin Login...")
    flow = InstalledAppFlow.from_client_secrets_file(
        'client_secret.json', SCOPES)
    
    # prompt='consent' is CRITICAL to get a refresh_token
    creds = flow.run_local_server(port=0, prompt='consent', access_type='offline')
    
    if not creds.refresh_token:
        print("❌ Error: No refresh token returned. Did you approve the app?")
        return

    print("✅ Authentication Successful!")
    print(f"🔑 Refresh Token Acquired: {creds.refresh_token[:10]}...")

    # 2. Prepare Secrets
    secrets_path = ".streamlit/secrets.toml"
    
    # Load existing secrets
    current_secrets = {}
    if os.path.exists(secrets_path):
        try:
            current_secrets = toml.load(secrets_path)
        except Exception as e:
            print(f"⚠️ Could not load existing secrets: {e}")

    # Update with OAuth info
    current_secrets["google_oauth"] = {
        "refresh_token": creds.refresh_token,
        "client_id": creds.client_id,
        "client_secret": creds.client_secret,
        "token_uri": creds.token_uri
    }

    # 3. Save to secrets.toml
    os.makedirs(".streamlit", exist_ok=True)
    with open(secrets_path, "w") as f:
        toml.dump(current_secrets, f)
        
    print(f"✅ Secrets saved to {secrets_path}")
    print("🎉 You can now restart the app. Users will NOT be asked to log in!")

if __name__ == "__main__":
    setup_headless()
