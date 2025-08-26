
import requests
from bs4 import BeautifulSoup
import csv
import config

def sanitize_text(text):
    """Sanitizes a string by removing non-ASCII characters.

    Args:
        text: The string to sanitize.

    Returns:
        The sanitized string.
    """
    return text.encode('ascii', 'ignore').decode('utf-8').strip()

def scrape_annas_archive(query, max_pages):
    """Scrapes Anna's Archive for a given query for a specified number of pages.

    This function iterates through the search result pages of Anna's Archive,
    extracts book information, and returns it as a list of dictionaries.

    Args:
        query: The search query.
        max_pages: The number of pages to scrape.

    Returns:
        A list of dictionaries, where each dictionary represents a book.
    """
    all_books = []
    for page in range(1, max_pages + 1):
        print(f"Scraping page {page}...")
        url = f"https://annas-archive.org/search?q={query}&page={page}"
        try:
            response = requests.get(url)
            response.raise_for_status()  # Raise an exception for bad status codes
        except requests.exceptions.RequestException as e:
            print(f"Error fetching the URL: {e}")
            continue

        soup = BeautifulSoup(response.content, "html.parser")

        # CSS selector for the container of each book entry
        book_container_selector = "div.flex.pt-3.pb-3"

        for book_element in soup.select(book_container_selector):
            # --- Extracting individual data points from the book element ---

            # Basic Info (Title, Link, MD5)
            title_element = book_element.select_one('a.js-vim-focus')
            title = title_element.get_text(strip=True) if title_element else "N/A"
            link = f"https://annas-archive.org{title_element['href']}" if title_element else "N/A"
            md5 = title_element['href'].replace("/md5/", "") if title_element else "N/A"

            # Author
            author_element = book_element.select_one('a[href*="/search?q="]')
            author = author_element.get_text(strip=True) if author_element else "N/A"

            # Publisher
            publisher_element = book_element.select('a[href*="/search?q="]')
            publisher = publisher_element[1].get_text(strip=True) if len(publisher_element) > 1 else "N/A"

            # Cover Image
            cover_image_element = book_element.select_one('img')
            cover_image = cover_image_element['src'] if cover_image_element else "N/A"

            # Metadata Line
            metadata_element = book_element.select_one('div.text-gray-800')
            metadata_text = metadata_element.get_text(strip=True) if metadata_element else ""

            # Split metadata string to get individual fields
            metadata_parts = [part.strip() for part in metadata_text.split('·')]
            
            language = sanitize_text(metadata_parts[0]) if metadata_parts else "N/A"
            file_type = sanitize_text(metadata_parts[1]) if len(metadata_parts) > 1 else "N/A"
            file_size = sanitize_text(metadata_parts[2]) if len(metadata_parts) > 2 else "N/A"
            year = sanitize_text(metadata_parts[3]) if len(metadata_parts) > 3 else "N/A"
            book_type = sanitize_text(metadata_parts[4]) if len(metadata_parts) > 4 else "N/A"

            # --- Appending the extracted data to the list of all books ---
            all_books.append({
                "title": title,
                "author": author,
                "link": link,
                "md5": md5,
                "publisher": publisher,
                "cover_image": cover_image,
                "language": language,
                "file_type": file_type,
                "file_size": file_size,
                "year": year,
                "book_type": book_type,
            })

    return all_books

if __name__ == "__main__":
    """Main execution block of the script.

    This block is executed when the script is run directly.
    It scrapes the books based on the configuration in config.py
    and saves the data to a CSV file.
    """
    # Scrape the books using the settings from config.py
    scraped_books = scrape_annas_archive(config.SEARCH_QUERY, config.MAX_PAGES)

    if scraped_books:
        # Write the scraped data to a CSV file
        with open('books.csv', 'w', newline='', encoding='utf-8') as csvfile:
            fieldnames = scraped_books[0].keys()
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

            writer.writeheader()
            writer.writerows(scraped_books)
        print(f"Data saved to books.csv. Scraped {len(scraped_books)} books.")
    else:
        print("No books found or an error occurred.")
