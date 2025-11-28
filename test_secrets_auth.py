import streamlit as st
import toml
import os
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request

print("--- TESTING SECRETS AUTH ---")

secrets_path = ".streamlit/secrets.toml"
if not os.path.exists(secrets_path):
    print(f"❌ {secrets_path} does not exist.")
    exit(1)

try:
    secrets = toml.load(secrets_path)
    if "google_oauth" not in secrets:
        print("❌ 'google_oauth' section missing in secrets.toml")
        exit(1)
        
    print("✅ Found 'google_oauth' in secrets.")
    oauth_secrets = secrets["google_oauth"]
    
    creds = Credentials(
        token=None,
        refresh_token=oauth_secrets["refresh_token"],
        client_id=oauth_secrets["client_id"],
        client_secret=oauth_secrets["client_secret"],
        token_uri=oauth_secrets["token_uri"]
    )
    
    print("ℹ️ Attempting to refresh token...")
    creds.refresh(Request())
    
    if creds.valid:
        print("✅ SUCCESS! Credentials refreshed and valid.")
    else:
        print("❌ Credentials invalid after refresh.")

except Exception as e:
    print(f"❌ Error: {e}")
