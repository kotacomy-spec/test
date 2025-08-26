import os
import csv
import requests
from bs4 import BeautifulSoup
import concurrent.futures
import threading
import psycopg2
from google.colab import drive
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseUpload
from io import BytesIO
from google.colab import auth
import logging
import time

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')


# Re-authenticate for API access if needed (though authenticate_user() was called previously)
# auth.authenticate_user() # Not needed again if already authenticated

print("Downloader script started")
logging.info("Downloader script started")


csv_lock = threading.Lock()

def get_db_connection():
    """Create and return a database connection."""
    try:
        conn = psycopg2.connect(
            dbname=DB_NAME,
            user=DB_USER,
            password=DB_PASSWORD,
            host=DB_HOST,
            port=DB_PORT
        )
        logging.info("Database connection successful")
        return conn
    except (Exception, psycopg2.DatabaseError) as error:
        logging.error(f"Error connecting to the database: {error}")
        return None


def update_download_status_with_filename(md5, status, filename=None, drive_link=None):
    """Update the download status, filename, and Google Drive link of a book in the database."""
    try:
        conn = get_db_connection()
        if conn:
            cur = conn.cursor()
            if filename and drive_link:
                cur.execute(
                    "UPDATE books SET download_status = %s, downloaded_filename = %s, drive_link = %s WHERE md5 = %s",
                    (status, filename, drive_link, md5)
                )
                logging.info(f"Updated status for MD5 {md5} to {status}, filename: {filename}, drive_link: {drive_link}")
            elif filename:
                 cur.execute(
                    "UPDATE books SET download_status = %s, downloaded_filename = %s WHERE md5 = %s",
                    (status, filename, md5)
                )
                 logging.info(f"Updated status for MD5 {md5} to {status}, filename: {filename}")
            else:
                cur.execute(
                    "UPDATE books SET download_status = %s WHERE md5 = %s",
                    (status, md5)
                )
                logging.info(f"Updated status for MD5 {md5} to {status}")
            conn.commit()
            cur.close()
            conn.close()
    except (Exception, psycopg2.DatabaseError) as error:
        logging.error(f"Error updating download status for MD5 {md5}: {error}")


def update_download_status(md5, status):
    """Update the download status of a book in the database."""
    update_download_status_with_filename(md5, status)


def download_book(book_data):
    """Downloads a single book, uploads it to Google Drive, and updates the database.

    Args:
        book_data: A dictionary containing the book's data.

    Returns:
        A message indicating the result of the download and upload.
    """
    md5 = book_data.get('md5')
    title = book_data.get('title', 'Unknown Title')
    if not md5:
        logging.warning(f"Skipping row due to missing MD5: {book_data}")
        return f"Skipping row due to missing MD5: {book_data}"

    update_download_status(md5, 'pending')
    logging.info(f"Starting download for '{title}' (MD5: {md5})")

    retries = 3
    for attempt in range(retries):
        try:
            download_page_url = f"https://libgen.li/ads.php?md5={md5}"
            logging.info(f"Attempt {attempt + 1} of {retries}: Fetching download page: {download_page_url}")

            response = requests.get(download_page_url, timeout=5)
            response.raise_for_status()
            soup = BeautifulSoup(response.content, 'html.parser')

            get_link = soup.find('a', href=lambda href: href and href.startswith('get.php'))
            if not get_link:
                if attempt < retries - 1:
                    logging.warning(f"Attempt {attempt + 1} failed: Could not find download link for '{title}' (MD5: {md5}). Retrying in 30 seconds...")
                    time.sleep(5) # Increased sleep time
                    continue
                else:
                    update_download_status(md5, 'failed')
                    logging.error(f"Failed after {retries} attempts: Could not find download link for '{title}' (MD5: {md5})")
                    return f"Could not find download link for MD5: {md5}"

            final_download_url = f"https://libgen.li/{get_link['href']}"
            logging.info(f"Attempt {attempt + 1} of {retries}: Found download link: {final_download_url}")

            logging.info(f"Attempt {attempt + 1} of {retries}: Downloading '{title}'...")

            sanitized_title = "".join(c for c in book_data['title'] if c.isalnum() or c in (' ', '-')).rstrip()
            file_extension = book_data.get('file_type', 'epub').lower()
            filename = f"{sanitized_title}.{file_extension}"

            with requests.get(final_download_url, timeout=60, stream=True) as r:
                r.raise_for_status()
                file_content = BytesIO(r.content) # Create BytesIO from content
            logging.info(f"Attempt {attempt + 1} of {retries}: Successfully downloaded '{title}'")


            # Build Google Drive service
            drive_service = build('drive', 'v3')
            logging.info("Google Drive service built successfully")


            # Define Google Drive folder ID (replace with your actual folder ID)
            # You can create a folder named "DownloadedBooks" in your Drive and get its ID
            # For this example, let's assume a folder ID or create one if it doesn't exist.
            # A robust implementation would find or create the folder dynamically.
            drive_folder_name = "DownloadedBooks"
            drive_folder_id = None

            # Try to find the folder
            logging.info(f"Searching for Google Drive folder: '{drive_folder_name}'")
            results = drive_service.files().list(
                q=f"mimeType='application/vnd.google-apps.folder' and name='{drive_folder_name}' and trashed=false",
                spaces='drive',
                fields='files(id)').execute()
            items = results.get('files', [])
            if items:
                drive_folder_id = items[0]['id']
                logging.info(f"Found existing folder: '{drive_folder_name}' with ID: {drive_folder_id}")
            else:
                 # Create the folder if it doesn't exist
                logging.info(f"Folder '{drive_folder_name}' not found, creating...")
                file_metadata = {
                    'name': drive_folder_name,
                    'mimeType': 'application/vnd.google-apps.folder'
                }
                folder = drive_service.files().create(body=file_metadata, fields='id').execute()
                drive_folder_id = folder.get('id')
                logging.info(f"Created new folder: '{drive_folder_name}' with ID: {drive_folder_id}")


            # File metadata for Google Drive
            file_metadata = {
                'name': filename,
                'parents': [drive_folder_id] if drive_folder_id else [] # Upload to the folder
            }

            # Media object for upload
            media = MediaIoBaseUpload(file_content, mimetype=r.headers['Content-Type'], resumable=True)

            logging.info(f"Uploading '{filename}' to Google Drive folder ID: {drive_folder_id}")

            # Upload the file
            uploaded_file = drive_service.files().create(
                body=file_metadata,
                media_body=media,
                fields='id,webViewLink,parents').execute()

            drive_link = uploaded_file.get('webViewLink')
            logging.info(f"Uploaded file ID: {uploaded_file.get('id')}, Shareable Link: {drive_link}")


            update_download_status_with_filename(md5, 'success', filename, drive_link)
            logging.info(f"Successfully downloaded, uploaded, and updated database for '{title}' (MD5: {md5})")

            return f"Successfully downloaded, uploaded to Drive, and updated database for MD5: {md5}"

        except requests.exceptions.Timeout:
            logging.warning(f"Attempt {attempt + 1} failed: Timeout downloading book '{title}' with MD5 {md5}.")
            if attempt < retries - 1:
                logging.info("Retrying in 30 seconds...") # Increased sleep time
                time.sleep(5)
            else:
                update_download_status(md5, 'failed')
                logging.error(f"Failed after {retries} attempts: Timeout downloading book '{title}' with MD5 {md5}. Skipping.")
                return f"Timeout downloading book with MD5 {md5}. Skipping."
        except requests.exceptions.RequestException as e:
            logging.warning(f"Attempt {attempt + 1} failed: Error downloading book '{title}' with MD5 {md5}: {e}")
            if attempt < retries - 1:
                logging.info("Retrying in 30 seconds...") # Increased sleep time
                time.sleep(5)
            else:
                update_download_status(md5, 'failed')
                logging.error(f"Failed after {retries} attempts: Error downloading book '{title}' with MD5 {md5}: {e}")
                return f"Error downloading book with MD5 {md5}: {e}"
        except Exception as e:
            logging.warning(f"Attempt {attempt + 1} failed: An error occurred for book '{title}' with MD5 {md5}: {e}")
            if attempt < retries - 1:
                logging.info("Retrying in 30 seconds...") # Increased sleep time
                time.sleep(5)
            else:
                update_download_status(md5, 'failed')
                logging.error(f"Failed after {retries} attempts: An error occurred for book '{title}' with MD5 {md5}: {e}")
                return f"An error occurred for book with MD5 {md5}: {e}"

    # This part should not be reached if retries are exhausted and errors persist
    return f"Failed to download book with MD5: {md5} after {retries} attempts."


def download_books_from_csv_concurrently(csv_filepath, download_limit, max_workers):
    """Reads books from the database and downloads them concurrently.

    Args:
        csv_filepath: The path to the CSV file (no longer used but kept for compatibility).
        download_limit: The maximum number of books to download.
        max_workers: The maximum number of concurrent downloads.
    """

    try:
        conn = get_db_connection()
        if conn:
            cur = conn.cursor()
            # This SQL query selects title, md5, and file_type from the 'books' table
            # where the download_status is NULL and limits the results to the download_limit.
            logging.info(f"Fetching up to {download_limit} books with NULL status from database")
            cur.execute(
                """SELECT title, md5, file_type FROM books
                   WHERE download_status IS NULL
                   LIMIT %s""",
                (download_limit,)
            )
            rows = cur.fetchall()
            cur.close()
            conn.close()

            logging.info(f"Found {len(rows)} books to download")

            # Convert rows to list of dictionaries
            all_books = [{"title": row[0], "md5": row[1], "file_type": row[2]} for row in rows]

            if not all_books:
                logging.info("No books found with NULL download status. Exiting.")
                print("No books found with NULL download status. Exiting.")
                return
        else:
            logging.error("Could not establish database connection. Exiting.")
            print("Could not establish database connection. Exiting.")
            return


    except (Exception, psycopg2.DatabaseError) as error:
        logging.error(f"Error fetching books from database: {error}")
        return

    # Use a flag to track if any downloads were initiated
    downloads_initiated = False
    if all_books:
        downloads_initiated = True
        logging.info(f"Starting concurrent downloads with {max_workers} workers")
        with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
            future_to_book = {executor.submit(download_book, book_data): book_data for book_data in all_books}
            for future in concurrent.futures.as_completed(future_to_book):
                book_data = future_to_book[future]
                try:
                    result = future.result()
                    # The download_book function already logs the result, no need to print here
                    pass
                except Exception as exc:
                    logging.error(f'{book_data.get("title", "Unknown Title")} generated an unhandled exception: {exc}')
                    print(f'{book_data.get("title", "Unknown Title")} generated an unhandled exception: {exc}')


    if not downloads_initiated:
        logging.info("No books processed by the downloader.")
        print("No new books to download. Exiting.")


if __name__ == "__main__":
    download_books_from_csv_concurrently(
        'books.csv',
        DOWNLOAD_LIMIT,
        MAX_CONCURRENT_DOWNLOADS
    )