#!/usr/bin/env python3
"""
Test script for database operations
"""

import psycopg2
import config
import pandas as pd

def get_db_connection():
    """Create and return a database connection."""
    return psycopg2.connect(
        dbname=config.DB_NAME,
        user=config.DB_USER,
        password=config.DB_PASSWORD,
        host=config.DB_HOST,
        port=config.DB_PORT
    )

def test_connection():
    """Test the database connection."""
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("SELECT version();")
        version = cur.fetchone()
        cur.close()
        conn.close()
        print("Database connection successful!")
        print(f"PostgreSQL version: {version[0]}")
        return True
    except Exception as e:
        print(f"Database connection failed: {e}")
        return False

def get_books_count():
    """Get the total number of books in the database."""
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("SELECT COUNT(*) FROM books;")
        count = cur.fetchone()[0]
        cur.close()
        conn.close()
        return count
    except Exception as e:
        print(f"Error getting books count: {e}")
        return 0

def get_sample_books(limit=5):
    """Get a sample of books from the database."""
    try:
        conn = get_db_connection()
        df = pd.read_sql_query(f"SELECT * FROM books LIMIT {limit};", conn)
        conn.close()
        return df
    except Exception as e:
        print(f"Error fetching sample books: {e}")
        return pd.DataFrame()

def main():
    print("=== Book Database Test ===")
    
    # Test connection
    if test_connection():
        # Get books count
        count = get_books_count()
        print(f"\nTotal books in database: {count}")
        
        # Get sample books
        print("\nSample books:")
        sample_books = get_sample_books()
        if not sample_books.empty:
            print(sample_books.to_string())
        else:
            print("No books found or error occurred.")

if __name__ == "__main__":
    main()