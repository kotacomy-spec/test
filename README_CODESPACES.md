# Google Drive Uploader for Codespaces

This version of the Google Drive uploader is specifically designed to work with GitHub Codespaces.

## Usage

1. Run the script without any arguments:
   ```
   python drive_uploader_codespaces.py
   ```

2. Follow the printed instructions to authorize the application by visiting the provided URL.

3. After authorizing, you'll receive an authorization code. Save this code to a file named `auth_code.txt` in the project directory.

4. Run the script again with the `--use-code` flag:
   ```
   python drive_uploader_codespaces.py --use-code
   ```

This will authenticate using the saved code and upload any downloaded books to Google Drive.