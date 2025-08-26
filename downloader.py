import os
import csv
import requests
from bs4 import BeautifulSoup
import concurrent.futures
import config
import threading

csv_lock = threading.Lock()

def update_download_status(md5, status):
    with csv_lock:
        with open('books.csv', 'r+', newline='') as f:
            reader = csv.reader(f)
            lines = list(reader)
            if not lines:
                return

            header = lines[0]
            try:
                md5_index = header.index('md5')
                download_status_index = header.index('download_status')
            except ValueError:
                return

            for line in lines[1:]:
                if len(line) > md5_index and line[md5_index] == md5:
                    while len(line) <= download_status_index:
                        line.append('')
                    line[download_status_index] = status
                    break
            f.seek(0)
            f.truncate()
            writer = csv.writer(f)
            writer.writerows(lines)

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
        
        update_download_status(md5, 'success')


        return f"Saved to {filepath}"

    except requests.exceptions.Timeout:
        return f"Timeout downloading book with MD5 {md5}. Skipping."
    except requests.exceptions.RequestException as e:
        update_download_status(md5, 'failed')
        return f"Error downloading book with MD5 {md5}: {e}"
    except Exception as e:
        update_download_status(md5, 'failed')
        return f"An error occurred for book with MD5 {md5}: {e}"

def download_books_from_csv_concurrently(csv_filepath, download_limit, max_workers):
    """Reads a CSV file of books and downloads them concurrently.

    Args:
        csv_filepath: The path to the CSV file.
        download_limit: The maximum number of books to download.
        max_workers: The maximum number of concurrent downloads.
    """
    # Create a directory to save the downloaded books
    if not os.path.exists('downloads'):
        os.makedirs('downloads')

    with open(csv_filepath, 'r', encoding='utf-8') as csvfile:
        reader = csv.DictReader(csvfile)
        all_books = [row for row in reader if row]

    books_to_download = []
    for row in all_books:
        download_status = row.get('download_status')
        if not download_status or download_status.lower() != 'success':
            books_to_download.append(row)

    books_to_download = books_to_download[:download_limit]

    with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
        future_to_book = {executor.submit(download_book, book_data): book_data for book_data in books_to_download}
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