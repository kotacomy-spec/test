#!/usr/bin/env python3
"""
Book downloader script for Google Colab.
Downloads books using URLs stored in the database.
"""

import os
import requests
import psycopg2
import config
from urllib.parse import urljoin

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
            """SELECT md5, title, file_type, download_url 
               FROM books 
               WHERE (download_status IS NULL OR download_status != 'success') 
               AND download_url IS NOT NULL"""
        )
        books = cur.fetchall()
        cur.close()
        conn.close()
        return books
    except Exception as error:
        print(f"Error fetching books from database: {error}")
        return []

def download_book(md5, title, file_type, download_url, download_dir="downloads"):
    """Download a book and save it to the downloads directory."""
    try:
        # Create downloads directory if it doesn't exist
        os.makedirs(download_dir, exist_ok=True)
        
        # Generate filename
        filename = f"{title}.{file_type}" if title and file_type else f"{md5}.{file_type}"
        # Sanitize filename
        filename = "".join(c for c in filename if c.isalnum() or c in "._- ").rstrip()
        filepath = os.path.join(download_dir, filename)
        
        # Skip if already downloaded
        if os.path.exists(filepath):
            print(f"File {filename} already exists, skipping download.")
            return filename
        
        # Download the file
        print(f"Downloading {title}...")
        response = requests.get(download_url, stream=True)
        
        if response.status_code == 200:
            with open(filepath, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    f.write(chunk)
            
            print(f"Downloaded {filename} successfully.")
            return filename
        else:
            print(f"Failed to download {title}. Status code: {response.status_code}")
            return None
    except Exception as error:
        print(f"Error downloading {title}: {error}")
        return None

def update_download_status(md5, filename=None, success=True):
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
                "UPDATE books SET download_status = 'failed' WHERE md5 = %s",
                (md5,)
            )
        conn.commit()
        cur.close()
        conn.close()
    except Exception as error:
        print(f"Error updating database for {md5}: {error}")

def download_all_books():
    """Download all books that haven't been downloaded yet."""
    books = get_books_to_download()
    if not books:
        print("No books to download.")
        return
    
    print(f"Found {len(books)} books to download.")
    
    # Download each book
    for book in books:
        md5, title, file_type, download_url = book
        
        filename = download_book(md5, title, file_type, download_url)
        
        if filename:
            update_download_status(md5, filename, success=True)
        else:
            update_download_status(md5, success=False)

if __name__ == "__main__":
    download_all_books()