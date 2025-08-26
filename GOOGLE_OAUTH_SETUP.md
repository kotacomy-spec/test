# Setting Up Your Own Google OAuth Credentials

To use the Google Drive upload functionality, you need to set up your own OAuth credentials:

## Step 1: Create Google Cloud Project
1. Go to https://console.cloud.google.com/
2. Create a new project or select an existing one

## Step 2: Enable Google Drive API
1. In the Cloud Console, go to "APIs & Services" > "Library"
2. Search for "Google Drive API"
3. Click on it and press "Enable"

## Step 3: Create OAuth Credentials
1. Go to "APIs & Services" > "Credentials"
2. Click "Create Credentials" > "OAuth client ID"
3. Choose "Desktop application" as the application type
4. Give it a name (e.g., "Book Downloader")
5. Click "Create"

## Step 4: Download and Use Credentials
1. Download the JSON file with your credentials
2. Rename it to `my_credentials.json`
3. Place it in the project directory (/workspaces/test/)
4. Run `python drive_uploader.py`

## Step 5: First-time Authentication
1. The first time you run the uploader, it will open a browser window
2. Sign in with your Google account
3. Grant the requested permissions
4. Copy the authorization code and paste it back in the terminal

## Alternative: Manual Credentials Entry
If you prefer not to download the JSON file, you can create `my_credentials.json` manually:

```json
{
  "installed": {
    "client_id": "YOUR_CLIENT_ID",
    "project_id": "YOUR_PROJECT_NAME",
    "auth_uri": "https://accounts.google.com/o/oauth2/auth",
    "token_uri": "https://oauth2.googleapis.com/token",
    "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
    "client_secret": "YOUR_CLIENT_SECRET",
    "redirect_uris": ["urn:ietf:wg:oauth:2.0:oob", "http://localhost"]
  }
}
```

Replace `YOUR_CLIENT_ID` and `YOUR_CLIENT_SECRET` with your actual credentials.