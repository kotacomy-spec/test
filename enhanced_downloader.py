#!/usr/bin/env python3
"""
Enhanced book downloader with better error handling and retry logic
"""

import requests
import time
import os
from urllib.parse import urlparse
import config
import psycopg2
from downloader import download_book

def get_db_connection():
    """Create and return a database connection."""
    return psycopg2.connect(
        dbname=config.DB_NAME,
        user=config.DB_USER,
        password=config.DB_PASSWORD,
        host=config.DB_HOST,
        port=config.DB_PORT
    )

def get_books_to_download():
    """Get books that need to be downloaded."""
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute(
            """SELECT md5, title, file_type, link 
               FROM books 
               WHERE (download_status IS NULL OR download_status = 'pending') 
               AND link IS NOT NULL"""
        )
        books = cur.fetchall()
        cur.close()
        conn.close()
        return books
    except Exception as error:
        print(f"Error fetching books from database: {error}")
        return []

def update_download_status(md5, filename=None, success=True, error_message=None):
    """Update the download status in the database."""
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        if success and filename:
            cur.execute(
                """UPDATE books 
                   SET downloaded_filename = %s, download_status = 'success' 
                   WHERE md5 = %s""",
                (filename, md5)
            )
        else:
            cur.execute(
                "UPDATE books SET download_status = 'failed', error_message = %s WHERE md5 = %s",
                (error_message, md5)
            )
        conn.commit()
        cur.close()
        conn.close()
    except Exception as error:
        print(f"Error updating database for {md5}: {error}")

def download_with_retry(md5, title, file_type, download_url, max_retries=3):
    """Download a book with retry logic and better error handling."""
    # Create downloads directory if it doesn't exist
    os.makedirs('downloads', exist_ok=True)
    
    # Generate filename
    filename = f"{title}.{file_type}" if title and file_type else f"{md5}.{file_type}"
    # Sanitize filename
    filename = "".join(c for c in filename if c.isalnum() or c in "._- ").rstrip()
    filepath = os.path.join('downloads', filename)
    
    # Skip if already downloaded
    if os.path.exists(filepath):
        print(f"File {filename} already exists, skipping download.")
        return filename
    
    # Try to download with retry logic
    for attempt in range(max_retries):
        try:
            print(f"Downloading {title} (attempt {attempt + 1}/{max_retries})...")
            
            # Use the existing download_book function which may have better handling
            result = download_book(download_url, filepath)
            
            if result:
                print(f"Downloaded {filename} successfully.")
                return filename
            else:
                print(f"Failed to download {title} on attempt {attempt + 1}")
                
        except Exception as e:
            print(f"Error downloading {title} on attempt {attempt + 1}: {e}")
            if attempt < max_retries - 1:
                print("Waiting 5 seconds before retry...")
                time.sleep(5)
    
    return None

def download_all_books():
    """Download all books that haven't been downloaded yet."""
    books = get_books_to_download()
    if not books:
        print("No books to download.")
        return
    
    print(f"Found {len(books)} books to download.")
    
    # Download each book
    for i, book in enumerate(books):
        md5, title, file_type, link = book
        
        print(f"\n[{i+1}/{len(books)}] Processing {title}...")
        
        filename = download_with_retry(md5, title, file_type, link)
        
        if filename:
            update_download_status(md5, filename, success=True)
        else:
            update_download_status(md5, success=False, error_message="Failed after retries")

if __name__ == "__main__":
    download_all_books()
