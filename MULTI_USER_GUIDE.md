# 👥 Multi-User Deployment Guide

You asked: *"I have a common email ID (allfaculty@srit.org) or they can use their own personal email id. How to do this?"*

Here are the two ways to set this up. **Option 1 is highly recommended** for simplicity.

---

## 🥇 Option 1: Centralized (Common Email) - RECOMMENDED

**Best for:** Simplicity. All reports go to one central Google Drive (e.g., `allfaculty@srit.org`). Faculty don't need to log in.

### How it works:
1.  You run the setup script **ONCE** on the computer/server hosting the app.
2.  You log in with `allfaculty@srit.org`.
3.  The app saves the "Access Token" (`token.pickle`).
4.  **Any faculty member** who opens the app will automatically upload files to `allfaculty@srit.org`'s Drive.

### Setup Steps:
1.  Run `python setup_oauth.py`
2.  Login with **`allfaculty@srit.org`**
3.  Done!
4.  (Optional) If you deploy this to a server, copy the `token.pickle` and `.streamlit/secrets.toml` to the server.

---

## 🥈 Option 2: Decentralized (Personal Emails)

**Best for:** Privacy. Each faculty member uploads to their *own* Google Drive.

### How it works:
1.  You **DELETE** the `token.pickle` file from the app folder.
2.  When Faculty A opens the app, they see "Google Drive not connected".
3.  They click **"🔄 Re-Authenticate"** in the sidebar.
4.  They log in with `facultyA@srit.org`.
5.  Files go to Faculty A's Drive.
6.  When Faculty B uses it, they do the same.

### ⚠️ Critical Limitation:
This **ONLY works if everyone runs the app locally** on their own laptop (`localhost`).
If you host this on a central server (e.g., `http://192.168.1.10:8501`), **Option 2 will NOT work** easily because the "Login with Google" window will open on the *server*, not the faculty's computer.

---

## 🚀 Summary Recommendation

**Use Option 1 (Common Email).**

1.  Login once with `allfaculty@srit.org` using `python setup_oauth.py`.
2.  Share the `token.pickle` file (or keep it on the server).
3.  Everyone can use the app immediately without logging in.
4.  All reports are neatly collected in one place.
