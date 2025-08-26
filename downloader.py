import os
import csv
import requests
from bs4 import BeautifulSoup
import concurrent.futures
import config

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
        response = requests.get(download_page_url)
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
        book_response = requests.get(final_download_url)
        book_response.raise_for_status()

        # Sanitize the title to create a valid filename
        sanitized_title = "".join(c for c in book_data['title'] if c.isalnum() or c in (' ', '-')).rstrip()
        file_extension = book_data.get('file_type', 'epub').lower()
        filename = f"{sanitized_title}.{file_extension}"
        filepath = os.path.join('downloads', filename)

        # Save the book to a file
        with open(filepath, 'wb') as f:
            f.write(book_response.content)
        return f"Saved to {filepath}"

    except requests.exceptions.RequestException as e:
        return f"Error downloading book with MD5 {md5}: {e}"
    except Exception as e:
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
        books_to_download = [row for i, row in enumerate(reader) if i < download_limit]

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