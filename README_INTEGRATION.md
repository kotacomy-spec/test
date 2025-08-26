# Google Drive Integration Files

This directory contains files for integrating with Google Drive, particularly for use with Google Colab.

## Files

1. `book_downloader_colab.ipynb` - A complete Google Colab notebook for downloading books and uploading them to Google Drive
2. `drive_uploader_colab.ipynb` - A Google Colab notebook focused only on uploading existing books to Google Drive
3. `drive_uploader_colab_fixed.ipynb` - An updated version of the uploader notebook with fixes
4. `drive_uploader_codespaces.py` - A version of the drive uploader designed for GitHub Codespaces
5. `colab_downloader.py` - A Python script for downloading books in Colab environments
6. `README_CODESPACES.md` - Instructions for using the Codespaces version of the drive uploader
7. `README_COLAB.md` - Instructions for using the Colab notebooks

## Usage

### For Google Colab:
1. Upload the `.ipynb` files to Google Colab
2. Follow the instructions in `README_COLAB.md`

### For GitHub Codespaces:
1. Use `drive_uploader_codespaces.py`
2. Follow the instructions in `README_CODESPACES.md`

## Authentication

All Google Drive integration requires OAuth credentials:
1. Create a Google Cloud Project
2. Enable the Google Drive API
3. Create OAuth credentials (Desktop application type)
4. Download the credentials as JSON
5. Rename the file to `my_credentials.json`

For Colab notebooks, upload this file when prompted.
For Codespaces, place it in the project directory.