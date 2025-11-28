import os
import sys
from utils import get_google_services
from config import GOOGLE_SHEET_ID

def get_headers():
    drive_service, sheets_service = get_google_services()
    if not sheets_service:
        print("Failed to authenticate.")
        return

    try:
        # Fetch the first 100 rows
        result = sheets_service.spreadsheets().values().get(
            spreadsheetId=GOOGLE_SHEET_ID, range="Sheet1!A1:Z100"
        ).execute()
        
        rows = result.get('values', [])
        if rows:
            print(f"Found {len(rows)} rows of data.")
            for i, row in enumerate(rows):
                print(f"Row {i+1}: {row}")
        else:
            print("No data found in Sheet1.")
            
    except Exception as e:
        print(f"Error fetching data: {e}")

if __name__ == "__main__":
    get_headers()
