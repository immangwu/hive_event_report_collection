import os
import pickle
import toml
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request

SCOPES = [
    'https://www.googleapis.com/auth/spreadsheets',
    'https://www.googleapis.com/auth/drive',
    'https://www.googleapis.com/auth/drive.file'
]

def setup_oauth():
    print("🔐 Starting One-Time OAuth Setup...")
    
    if not os.path.exists('client_secret.json'):
        print("❌ client_secret.json not found!")
        print("Download it from: https://console.cloud.google.com/apis/credentials")
        return
    
    # Run interactive login
    print("🌐 Opening browser for login...")
    flow = InstalledAppFlow.from_client_secrets_file(
        'client_secret.json', SCOPES)
    
    # Force consent to get refresh token
    creds = flow.run_local_server(
        port=0, 
        prompt='consent', 
        access_type='offline'
    )
    
    if not creds.refresh_token:
        print("❌ No refresh token! Try again and approve all permissions.")
        return
    
    print("✅ Login successful!")
    
    # Save to secrets.toml (for cloud deployment)
    os.makedirs(".streamlit", exist_ok=True)
    secrets_path = ".streamlit/secrets.toml"
    
    current_secrets = {}
    if os.path.exists(secrets_path):
        try:
            current_secrets = toml.load(secrets_path)
        except:
            pass
    
    current_secrets["google_oauth"] = {
        "refresh_token": creds.refresh_token,
        "client_id": creds.client_id,
        "client_secret": creds.client_secret,
        "token_uri": "https://oauth2.googleapis.com/token"
    }
    
    with open(secrets_path, "w") as f:
        toml.dump(current_secrets, f)
    
    # Save to token.pickle (for local use)
    with open('token.pickle', 'wb') as token:
        pickle.dump(creds, token)
    
    print(f"✅ Credentials saved!")
    print(f"   - token.pickle (local)")
    print(f"   - {secrets_path} (cloud)")
    print("\n🎉 Setup complete! Restart your app.")

if __name__ == "__main__":
    setup_oauth()
