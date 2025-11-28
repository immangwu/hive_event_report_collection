import os
import pickle
import io
import sys
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseUpload
from google.auth.transport.requests import Request

# Force stdout to flush
sys.stdout.reconfigure(line_buffering=True)

print("--- STARTING UPLOAD DIAGNOSTIC ---")

# 1. Auth
creds = None
if os.path.exists('token.pickle'):
    with open('token.pickle', 'rb') as token:
        creds = pickle.load(token)

if not creds or not creds.valid:
    if creds and creds.expired and creds.refresh_token:
        creds.refresh(Request())

if not creds:
    print("CRITICAL: No credentials.")
    sys.exit(1)

drive_service = build('drive', 'v3', credentials=creds)

# 2. Create Test Folder
folder_metadata = {
    'name': 'DIAGNOSTIC_UPLOAD_TEST',
    'mimeType': 'application/vnd.google-apps.folder'
}
folder = drive_service.files().create(body=folder_metadata, fields='id').execute()
folder_id = folder.get('id')
print(f"Created Test Folder: {folder_id}")

# 3. Test Upload (BytesIO - Simulating Streamlit)
print("Testing BytesIO Upload...")
try:
    file_content = b"This is a test file content from BytesIO."
    file_obj = io.BytesIO(file_content)
    
    file_metadata = {
        'name': 'test_bytesio.txt',
        'parents': [folder_id]
    }
    
    media = MediaIoBaseUpload(file_obj, mimetype='text/plain', resumable=True)
    file = drive_service.files().create(body=file_metadata, media_body=media, fields='id, webViewLink').execute()
    print(f"BytesIO Upload SUCCESS: {file.get('id')}")
except Exception as e:
    print(f"BytesIO Upload FAILED: {e}")

# 4. Test Upload (File on Disk - Simulating PDF)
print("Testing Disk File Upload...")
try:
    with open("test_disk_file.txt", "w") as f:
        f.write("This is a test file content from Disk.")
        
    with open("test_disk_file.txt", "rb") as f:
        file_metadata = {
            'name': 'test_disk.txt',
            'parents': [folder_id]
        }
        media = MediaIoBaseUpload(f, mimetype='text/plain', resumable=True)
        file = drive_service.files().create(body=file_metadata, media_body=media, fields='id, webViewLink').execute()
        print(f"Disk File Upload SUCCESS: {file.get('id')}")
except Exception as e:
    print(f"Disk File Upload FAILED: {e}")

print("--- DIAGNOSTIC COMPLETE ---")
