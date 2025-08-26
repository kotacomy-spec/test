#!/usr/bin/env python3
"""
Advanced book downloader with session management and custom headers
"""

import requests
import time
import os
import psycopg2
import config
from urllib.parse import urlparse
from proxy_config import configure_session_with_proxy

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

def create_session():
    """Create a requests session with custom headers."""
    session = requests.Session()
    session.headers.update({
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        'Accept-Language': 'en-US,en;q=0.5',
        'Accept-Encoding': 'gzip, deflate',
        'Connection': 'keep-alive',
        'Upgrade-Insecure-Requests': '1',
    })
    
    # Configure with proxy if needed
    session = configure_session_with_proxy(session)
    
    return session

def download_book_advanced(url, filepath, session=None, timeout=30):
    """Download a book with advanced settings."""
    if session is None:
        session = create_session()
    
    try:
        # First, try to get the headers to check if the URL is accessible
        print(f"Checking URL accessibility: {url}")
        head_response = session.head(url, timeout=timeout)
        print(f"Status code: {head_response.status_code}")
        
        if head_response.status_code >= 400:
            print(f"URL not accessible, trying GET request...")
            # If HEAD fails, try GET
            response = session.get(url, timeout=timeout, stream=True)
        else:
            # If HEAD succeeds, proceed with GET
            response = session.get(url, timeout=timeout, stream=True)
        
        if response.status_code == 200:
            # Get filename from Content-Disposition header if available
            content_disposition = response.headers.get('content-disposition')
            if content_disposition:
                # Extract filename from header
                import re
                fname = re.findall('filename=(.+)', content_disposition)
                if fname:
                    actual_filename = fname[0].strip('"')
                    # Update filepath with actual filename
                    dir_path = os.path.dirname(filepath)
                    filepath = os.path.join(dir_path, actual_filename)
            
            # Create downloads directory if it doesn't exist
            os.makedirs(os.path.dirname(filepath), exist_ok=True)
            
            # Download the file
            with open(filepath, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    f.write(chunk)
            
            print(f"Successfully downloaded to {filepath}")
            return True
        else:
            print(f"Failed to download. Status code: {response.status_code}")
            print(f"Response headers: {response.headers}")
            return False
            
    except requests.exceptions.RequestException as e:
        print(f"Request error: {e}")
        return False
    except Exception as e:
        print(f"Unexpected error: {e}")
        return False

def download_with_advanced_settings(md5, title, file_type, download_url):
    """Download a book with advanced settings and error handling."""
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
    
    # Create a session with custom headers
    session = create_session()
    
    # Try to download
    print(f"Downloading {title} with advanced settings...")
    success = download_book_advanced(download_url, filepath, session)
    
    if success:
        return filename
    else:
        return None

def download_all_books_advanced():
    """Download all books with advanced settings."""
    books = get_books_to_download()
    if not books:
        print("No books to download.")
        return
    
    print(f"Found {len(books)} books to download.")
    
    # Download each book
    for i, book in enumerate(books):
        md5, title, file_type, link = book
        
        print(f"[{i+1}/{len(books)}] Processing {title}...")
        print(f"URL: {link}")
        
        filename = download_with_advanced_settings(md5, title, file_type, link)
        
        if filename:
            update_download_status(md5, filename, success=True)
        else:
            update_download_status(md5, success=False, error_message="Failed with advanced downloader")

if __name__ == "__main__":
    download_all_books_advanced()
