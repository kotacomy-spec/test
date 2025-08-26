# Google Drive Integration Files

This directory contains files for integrating with Google Drive, particularly for use with Google Colab, and a dashboard for managing books.

## Files

1. `book_downloader_colab.ipynb` - A complete Google Colab notebook for downloading books and uploading them to Google Drive
2. `drive_uploader_colab.ipynb` - A Google Colab notebook focused only on uploading existing downloaded books to Google Drive
3. `drive_uploader_codespaces.py` - A version of the drive uploader designed for GitHub Codespaces
4. `colab_downloader.py` - A Python script for downloading books in Colab environments
5. `book_dashboard.py` - A Streamlit dashboard for managing books with CRUD operations
6. `enhanced_book_dashboard.py` - An enhanced Streamlit dashboard with analytics and visualizations
7. `enhanced_book_dashboard_v2.py` - An enhanced Streamlit dashboard with book collection view and Drive URLs
8. `enhanced_downloader.py` - Enhanced downloader with retry logic
9. `advanced_downloader.py` - Advanced downloader with custom headers and session management
10. `proxy_config.py` - Proxy configuration for downloads
11. `README_CODESPACES.md` - Instructions for using the Codespaces version of the drive uploader
12. `README_COLAB.md` - Instructions for using the Colab notebooks
13. `README_DASHBOARD.md` - Instructions for using the book dashboard
14. `README_ENHANCED_DASHBOARD.md` - Instructions for using the enhanced book dashboard
15. `README_ENHANCED_DASHBOARD_V2.md` - Instructions for using the enhanced book dashboard with Drive URLs
16. `README_DOWNLOADERS.md` - Instructions for using the enhanced downloaders

## Usage

### For Google Colab:
1. Upload the `.ipynb` files to Google Colab
2. Follow the instructions in `README_COLAB.md`

### For GitHub Codespaces:
1. Use `drive_uploader_codespaces.py`
2. Follow the instructions in `README_CODESPACES.md`

### For Dashboard:
1. Install dependencies with `pip install -r requirements_dashboard.txt`
2. Run with `streamlit run enhanced_book_dashboard_v2.py`
3. Follow instructions in `README_ENHANCED_DASHBOARD_V2.md`

### For Downloading Books:
1. Try the existing `scraper.py` and `downloader.py` first
2. If encountering 502 errors, try `enhanced_downloader.py` or `advanced_downloader.py`
3. Configure proxy settings in `proxy_config.py` if needed
4. Follow instructions in `README_DOWNLOADERS.md`

## Authentication

All Google Drive integration requires OAuth credentials:
1. Create a Google Cloud Project
2. Enable the Google Drive API
3. Create OAuth credentials (Desktop application type)
4. Download the credentials as JSON
5. Rename the file to `my_credentials.json`

For Colab notebooks, upload this file when prompted.
For Codespaces, place it in the project directory.

## Usage

### For Google Colab:
1. Upload the `.ipynb` files to Google Colab
2. Follow the instructions in `README_COLAB.md`

### For GitHub Codespaces:
1. Use `drive_uploader_codespaces.py`
2. Follow the instructions in `README_CODESPACES.md`

### For Dashboard:
1. Install dependencies with `pip install -r requirements_dashboard.txt`
2. Run with `streamlit run enhanced_book_dashboard_v2.py`
3. Follow instructions in `README_ENHANCED_DASHBOARD_V2.md`

## Authentication

All Google Drive integration requires OAuth credentials:
1. Create a Google Cloud Project
2. Enable the Google Drive API
3. Create OAuth credentials (Desktop application type)
4. Download the credentials as JSON
5. Rename the file to `my_credentials.json`

For Colab notebooks, upload this file when prompted.
For Codespaces, place it in the project directory.

## Usage

### For Google Colab:
1. Upload the `.ipynb` files to Google Colab
2. Follow the instructions in `README_COLAB.md`

### For GitHub Codespaces:
1. Use `drive_uploader_codespaces.py`
2. Follow the instructions in `README_CODESPACES.md`

### For Dashboard:
1. Install dependencies with `pip install -r requirements_dashboard.txt`
2. Run with `streamlit run enhanced_book_dashboard.py`
3. Follow instructions in `README_ENHANCED_DASHBOARD.md`

## Authentication

All Google Drive integration requires OAuth credentials:
1. Create a Google Cloud Project
2. Enable the Google Drive API
3. Create OAuth credentials (Desktop application type)
4. Download the credentials as JSON
5. Rename the file to `my_credentials.json`

For Colab notebooks, upload this file when prompted.
For Codespaces, place it in the project directory.