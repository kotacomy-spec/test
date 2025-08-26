import os
import csv
import requests
from bs4 import BeautifulSoup
import concurrent.futures
import config
import threading
import psycopg2

print("Downloader script started")

csv_lock = threading.Lock()

def get_db_connection():
    """Create and return a database connection."""
    return psycopg2.connect(
        dbname=config.DB_NAME,
        user=config.DB_USER,
        password=config.DB_PASSWORD,
        host=config.DB_HOST,
        port=config.DB_PORT
    )

def update_download_status_with_filename(md5, status, filename=None):
    """Update the download status and filename of a book in the database."""
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        if filename:
            cur.execute(
                "UPDATE books SET download_status = %s, downloaded_filename = %s WHERE md5 = %s",
                (status, filename, md5)
            )
        else:
            cur.execute(
                "UPDATE books SET download_status = %s WHERE md5 = %s",
                (status, md5)
            )
        conn.commit()
        cur.close()
        conn.close()
    except (Exception, psycopg2.DatabaseError) as error:
        print(f"Error updating download status for MD5 {md5}: {error}")

def update_download_status(md5, status):
    """Update the download status of a book in the database."""
    update_download_status_with_filename(md5, status)

def download_book(book_data):
    """Downloads a single book.

    Args:
        book_data: A dictionary containing the book's data.

    Returns:
        A message indicating the result of the download.
    """
    md5 = book_data.get('md5')
    if not md5:
        return f"Skipping row due to missing MD5: {book_data}"

    # Set status to pending when download starts
    update_download_status(md5, 'pending')
    
    try:
        # Construct the URL for the download page
        download_page_url = f"https://libgen.li/ads.php?md5={md5}"
        print(f"Fetching download page: {download_page_url}")

        # Get the download page
        response = requests.get(download_page_url, timeout=30)
        response.raise_for_status()
        soup = BeautifulSoup(response.content, 'html.parser')

        # Find the final download link
        get_link = soup.find('a', href=lambda href: href and href.startswith('get.php'))
        if not get_link:
            update_download_status(md5, 'failed')
            return f"Could not find download link for MD5: {md5}"

        final_download_url = f"https://libgen.li/{get_link['href']}"
        print(f"Found download link: {final_download_url}")

        # Download the book
        print(f"Downloading {book_data['title']}...")
        
        # Sanitize the title to create a valid filename
        sanitized_title = "".join(c for c in book_data['title'] if c.isalnum() or c in (' ', '-')).rstrip()
        file_extension = book_data.get('file_type', 'epub').lower()
        filename = f"{sanitized_title}.{file_extension}"
        filepath = os.path.join('downloads', filename)

        with requests.get(final_download_url, timeout=30, stream=True) as r:
            r.raise_for_status()
            with open(filepath, 'wb') as f:
                for chunk in r.iter_content(chunk_size=8192):
                    f.write(chunk)
        
        # Update status to success and save the filename
        update_download_status_with_filename(md5, 'success', filename)

        return f"Saved to {filepath}"

    except requests.exceptions.Timeout:
        update_download_status(md5, 'failed')
        return f"Timeout downloading book with MD5 {md5}. Skipping."
    except requests.exceptions.RequestException as e:
        update_download_status(md5, 'failed')
        return f"Error downloading book with MD5 {md5}: {e}"
    except Exception as e:
        update_download_status(md5, 'failed')
        return f"An error occurred for book with MD5 {md5}: {e}"

def download_books_from_csv_concurrently(csv_filepath, download_limit, max_workers):
    """Reads books from the database and downloads them concurrently.

    Args:
        csv_filepath: The path to the CSV file (no longer used but kept for compatibility).
        download_limit: The maximum number of books to download.
        max_workers: The maximum number of concurrent downloads.
    """
    # Create a directory to save the downloaded books
    if not os.path.exists('downloads'):
        os.makedirs('downloads')

    try:
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute(
            """SELECT title, md5, file_type FROM books 
               WHERE download_status IS NULL 
               LIMIT %s""",
            (download_limit,)
        )
        rows = cur.fetchall()
        cur.close()
        conn.close()
        
        print(f"Found {len(rows)} books to download")
        
        # Convert rows to list of dictionaries
        all_books = [{"title": row[0], "md5": row[1], "file_type": row[2]} for row in rows]
        
        if not all_books:
            print("No books found with NULL download status")
            return
    except (Exception, psycopg2.DatabaseError) as error:
        print(f"Error fetching books from database: {error}")
        return

    with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
        future_to_book = {executor.submit(download_book, book_data): book_data for book_data in all_books}
        for future in concurrent.futures.as_completed(future_to_book):
            book_data = future_to_book[future]
            try:
                result = future.result()
                print(result)
            except Exception as exc:
                print(f'{book_data["title"]} generated an exception: {exc}')

if __name__ == "__main__":
    download_books_from_csv_concurrently(
        'books.csv',
        config.DOWNLOAD_LIMIT,
        config.MAX_CONCURRENT_DOWNLOADS
    )