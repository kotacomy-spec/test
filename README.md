# Book Downloader with Google Drive Integration

This project has two separate components:
1. `downloader.py` - Downloads books and stores them locally
2. `drive_uploader.py` - Uploads downloaded books to Google Drive

## Setup

1. Install the basic requirements:
   ```
   pip install -r requirements.txt
   ```

2. To use Google Drive integration:
   - Run `./install_drive_deps.sh` to install Google Drive dependencies

## Usage

1. First, download books:
   ```
   python downloader.py
   ```

2. Then, upload to Google Drive (optional):
   ```
   python drive_uploader.py
   ```

## Google Drive Authentication

### Option 1: Use Your Own OAuth Credentials (Recommended)
1. Follow the instructions in `GOOGLE_OAUTH_SETUP.md` to create your own credentials
2. Download the credentials JSON file and save it as `my_credentials.json` in this directory
3. Run `python drive_uploader.py` and follow the authentication flow

### Option 2: Use Provided Credentials (Limited Access)
The provided credentials may not work if you're not added as a test user.
If you encounter authentication issues, please use Option 1 above.

## Security Notes
- The `token.json` file contains your Google Drive access tokens. Keep it secure.
- The `my_credentials.json` file contains your OAuth client credentials. Do not share it.
- Both files are already in `.gitignore` to prevent accidental commits.