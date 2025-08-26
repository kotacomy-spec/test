# Book Dashboard

A Streamlit dashboard for managing books in the database with CRUD operations.

## Features

- View all books in the database
- Search books by title, author, or MD5
- Add new books to the database
- Edit existing book information
- Delete books from the database
- Download books list as CSV

## Installation

1. Install the required dependencies:
   ```
   pip install -r requirements_dashboard.txt
   ```

2. Make sure your database credentials are set in `config.py`

## Usage

Run the dashboard with:
```
streamlit run book_dashboard.py
```

The dashboard will be available at `http://localhost:8501` by default.

## Functionality

### View Books
- Displays all books in the database in a searchable table
- Allows downloading the full list as CSV

### Search Books
- Search books by title, author, or MD5
- Results displayed in a table

### Add Book
- Form to add new books to the database
- Required fields: Title and MD5
- New books are added with "pending" download status

### Manage Books
- Edit existing book information
- Delete books from the database
- Search for books by MD5 to manage them

## Database Schema

The dashboard works with the following table structure:

```
books table:
- id (integer)
- title (text)
- author (text)
- link (text)
- md5 (text)
- publisher (text)
- cover_image (text)
- language (text)
- file_type (text)
- file_size (text)
- year (text)
- book_type (text)
- download_status (text)
- drive_download_url (text)
- downloaded_filename (text)
```