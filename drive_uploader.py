#!/usr/bin/env python3
"""
Google Drive Uploader for downloaded books.
Uploads books from the downloads folder to Google Drive and updates the database with shareable links.
"""

import os
import psycopg2
import config
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
import json

# If modifying these scopes, make sure they match your service account permissions.
SCOPES = ['https://www.googleapis.com/auth/drive.file']

def get_db_connection():
    """Create and return a database connection."""
    return psycopg2.connect(
        dbname=config.DB_NAME,
        user=config.DB_USER,
        password=config.DB_PASSWORD,
        host=config.DB_HOST,
        port=config.DB_PORT
    )

def authenticate_google_drive():
    """Authenticate and return Google Drive service using OAuth2."""
    creds = None
    # The file token.json stores the user's access and refresh tokens.
    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json', SCOPES)
    
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            # Check if user has provided their own credentials
            if os.path.exists('my_credentials.json'):
                # Use user's own credentials file
                flow = InstalledAppFlow.from_client_secrets_file(
                    'my_credentials.json', SCOPES)
            else:
                print("Error: No credentials file found.")
                print("Please create 'my_credentials.json' with your OAuth credentials.")
                print("See GOOGLE_OAUTH_SETUP.md for instructions.")
                return None
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open('token.json', 'w') as token:
            token.write(creds.to_json())
    
    return build('drive', 'v3', credentials=creds)

def upload_to_google_drive(file_path, filename):
    """Upload a file to Google Drive and return the shareable link."""
    try:
        service = authenticate_google_drive()
        
        # Check if authentication was successful
        if service is None:
            return None
        
        # Upload the file
        media = MediaFileUpload(file_path, resumable=True)
        file_metadata = {'name': filename}
        
        uploaded_file = service.files().create(
            body=file_metadata,
            media_body=media,
            fields='id'
        ).execute()
        
        # Make the file shareable
        permission = {
            'type': 'anyone',
            'role': 'reader'
        }
        service.permissions().create(
            fileId=uploaded_file['id'],
            body=permission
        ).execute()
        
        # Return the shareable link
        return f"https://drive.google.com/file/d/1{uploaded_file['id']}/view?usp=sharing"
    except Exception as e:
        print(f"Error uploading to Google Drive: {e}")
        return None

def update_drive_url_in_db(md5, drive_url):
    """Update the Google Drive URL for a book in the database."""
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute(
            "UPDATE books SET drive_download_url = %s WHERE md5 = %s",
            (drive_url, md5)
        )
        conn.commit()
        cur.close()
        conn.close()
        print(f"Updated Drive URL for MD5 {md5}")
    except (Exception, psycopg2.DatabaseError) as error:
        print(f"Error updating Drive URL for MD5 {md5}: {error}")

def upload_downloaded_books_to_drive():
    """Upload all downloaded books to Google Drive and update database with URLs."""
    # Create downloads directory if it doesn't exist
    if not os.path.exists('downloads'):
        print("Downloads directory not found.")
        return
    
    # Get books with success status from database that have downloaded_filename
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute(
            "SELECT md5, title, file_type, downloaded_filename FROM books WHERE download_status = 'success' AND downloaded_filename IS NOT NULL AND (drive_download_url IS NULL OR drive_download_url = '')"
        )
        books = cur.fetchall()
        cur.close()
        conn.close()
    except (Exception, psycopg2.DatabaseError) as error:
        print(f"Error fetching books from database: {error}")
        return
    
    # Upload each book to Google Drive
    for book in books:
        md5, title, file_type, downloaded_filename = book
        filename = downloaded_filename
        filepath = os.path.join('downloads', filename)
        
        # Check if file exists
        if os.path.exists(filepath):
            print(f"Uploading {filename} to Google Drive...")
            drive_url = upload_to_google_drive(filepath, filename)
            
            if drive_url:
                update_drive_url_in_db(md5, drive_url)
                print(f"Uploaded {filename} to Google Drive: {drive_url}")
            else:
                print(f"Failed to upload {filename} to Google Drive")
        else:
            print(f"File {filename} not found in downloads directory")

if __name__ == "__main__":
    upload_downloaded_books_to_drive()