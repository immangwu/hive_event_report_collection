# Setting Up Secrets for Deployment

To keep your API keys secure and avoid leaking them on GitHub, this app uses **Streamlit Secrets**.

## 1. Local Development
Create a file named `.streamlit/secrets.toml` in your project directory (if it doesn't exist).
**Note:** This file is already in `.gitignore`, so it won't be committed to GitHub.

Add your keys to `.streamlit/secrets.toml`:

```toml
GEMINI_API_KEY = "YOUR_NEW_API_KEY_HERE"
GOOGLE_SHEET_ID = "13Pkhj_igbp7UsUb2-PWYqYA-_dYNMaQHr-hZveWf2v8"
DRIVE_PARENT_FOLDER_ID = "1eX8HO41TlVScAs4648JyMOl9U-JbjDe1"
```

## 2. Deploying to Streamlit Cloud
When you deploy your app to Streamlit Cloud:

1.  Go to your app's dashboard.
2.  Click on **Settings** -> **Secrets**.
3.  Paste the content of your `secrets.toml` file into the text area.
4.  Save.

Your app will now securely access these keys without them being in your code!
