# Google Colab Notebooks for Book Downloading and Uploading

This repository contains Google Colab notebooks for downloading books and uploading them to Google Drive.

## Notebooks

1. **book_downloader_colab.ipynb** - A complete solution for both downloading books and uploading them to Google Drive
2. **drive_uploader_colab.ipynb** - A simplified version that focuses only on uploading existing downloaded books to Google Drive

## Setup Instructions

### For book_downloader_colab.ipynb:
1. Open the notebook in Google Colab
2. Update the database credentials in the "Database Configuration" section
3. Run the cells in order, following the instructions in each section

### For drive_uploader_colab.ipynb:
1. Open the notebook in Google Colab
2. Update the database credentials in the "Database Configuration" section
3. Upload your `my_credentials.json` file when prompted
4. Mount your Google Drive when prompted
5. Upload your book files using the file upload cell
6. Run the uploader cell to upload books to Google Drive

## Authentication

Both notebooks require Google OAuth credentials:
1. Create a Google Cloud Project
2. Enable the Google Drive API
3. Create OAuth credentials (Desktop application type)
4. Download the credentials as JSON
5. Rename the file to `my_credentials.json`
6. Upload this file when prompted in the Colab notebook

The notebooks will save authentication tokens to your Google Drive to avoid re-authentication in future sessions.