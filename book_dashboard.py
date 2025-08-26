#!/usr/bin/env python3
"""
Book Dashboard - Streamlit application for managing books in the database
"""

import streamlit as st
import psycopg2
import pandas as pd
import config
from datetime import datetime

# Database connection
def get_db_connection():
    """Create and return a database connection."""
    return psycopg2.connect(
        dbname=config.DB_NAME,
        user=config.DB_USER,
        password=config.DB_PASSWORD,
        host=config.DB_HOST,
        port=config.DB_PORT
    )

# Database operations
def get_all_books():
    """Get all books from the database."""
    try:
        conn = get_db_connection()
        df = pd.read_sql_query("SELECT * FROM books", conn)
        conn.close()
        return df
    except Exception as e:
        st.error(f"Error fetching books: {e}")
        return pd.DataFrame()

def search_books(query):
    """Search books by title, author, or MD5."""
    try:
        conn = get_db_connection()
        df = pd.read_sql_query(
            """SELECT * FROM books 
               WHERE title ILIKE %s OR author ILIKE %s OR md5 ILIKE %s""", 
            conn, 
            params=(f"%{query}%", f"%{query}%", f"%{query}%")
        )
        conn.close()
        return df
    except Exception as e:
        st.error(f"Error searching books: {e}")
        return pd.DataFrame()

def get_book_by_md5(md5):
    """Get a specific book by MD5."""
    try:
        conn = get_db_connection()
        df = pd.read_sql_query("SELECT * FROM books WHERE md5 = %s", conn, params=(md5,))
        conn.close()
        return df.iloc[0] if not df.empty else None
    except Exception as e:
        st.error(f"Error fetching book: {e}")
        return None

def update_book(md5, title, author, publisher, year, language, file_type, book_type):
    """Update book information."""
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute(
            """UPDATE books SET 
               title = %s, author = %s, publisher = %s, year = %s, 
               language = %s, file_type = %s, book_type = %s 
               WHERE md5 = %s""",
            (title, author, publisher, year, language, file_type, book_type, md5)
        )
        conn.commit()
        cur.close()
        conn.close()
        st.success("Book updated successfully!")
        return True
    except Exception as e:
        st.error(f"Error updating book: {e}")
        return False

def delete_book(md5):
    """Delete a book from the database."""
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("DELETE FROM books WHERE md5 = %s", (md5,))
        conn.commit()
        cur.close()
        conn.close()
        st.success("Book deleted successfully!")
        return True
    except Exception as e:
        st.error(f"Error deleting book: {e}")
        return False

def add_book(title, author, md5, publisher, year, language, file_type, book_type):
    """Add a new book to the database."""
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute(
            """INSERT INTO books 
               (title, author, md5, publisher, year, language, file_type, book_type, download_status) 
               VALUES (%s, %s, %s, %s, %s, %s, %s, %s, 'pending')""",
            (title, author, md5, publisher, year, language, file_type, book_type)
        )
        conn.commit()
        cur.close()
        conn.close()
        st.success("Book added successfully!")
        return True
    except Exception as e:
        st.error(f"Error adding book: {e}")
        return False

# Streamlit UI
def main():
    st.set_page_config(
        page_title="Book Dashboard",
        page_icon="📚",
        layout="wide"
    )
    
    st.title("📚 Book Dashboard")
    st.markdown("Manage your book collection with this dashboard")
    
    # Create tabs for different functionalities
    tab1, tab2, tab3, tab4 = st.tabs(["📚 View Books", "🔍 Search Books", "➕ Add Book", "⚙️ Manage Books"])
    
    # Tab 1: View all books
    with tab1:
        st.header("All Books")
        books_df = get_all_books()
        if not books_df.empty:
            st.dataframe(books_df, use_container_width=True)
            
            # Download button for CSV
            csv = books_df.to_csv(index=False)
            st.download_button(
                label="Download Books as CSV",
                data=csv,
                file_name=f"books_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                mime="text/csv"
            )
        else:
            st.info("No books found in the database.")
    
    # Tab 2: Search books
    with tab2:
        st.header("Search Books")
        query = st.text_input("Enter search term (title, author, or MD5)")
        if query:
            search_results = search_books(query)
            if not search_results.empty:
                st.dataframe(search_results, use_container_width=True)
            else:
                st.info("No books found matching your search.")
    
    # Tab 3: Add new book
    with tab3:
        st.header("Add New Book")
        with st.form("add_book_form"):
            col1, col2 = st.columns(2)
            
            with col1:
                title = st.text_input("Title")
                author = st.text_input("Author")
                md5 = st.text_input("MD5")
                publisher = st.text_input("Publisher")
                year = st.text_input("Year")
            
            with col2:
                language = st.text_input("Language")
                file_type = st.text_input("File Type")
                book_type = st.text_input("Book Type")
            
            submitted = st.form_submit_button("Add Book")
            if submitted:
                if title and md5:
                    add_book(title, author, md5, publisher, year, language, file_type, book_type)
                else:
                    st.warning("Title and MD5 are required fields.")
    
    # Tab 4: Manage books (edit/delete)
    with tab4:
        st.header("Manage Books")
        md5_to_manage = st.text_input("Enter MD5 of book to manage")
        
        if md5_to_manage:
            book = get_book_by_md5(md5_to_manage)
            if book is not None:
                st.subheader(f"Manage: {book['title']}")
                
                # Display current information
                st.write("**Current Information:**")
                st.json(book.to_dict())
                
                # Edit form
                st.subheader("Edit Book")
                with st.form(f"edit_book_{md5_to_manage}"):
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        new_title = st.text_input("Title", value=book['title'] or "")
                        new_author = st.text_input("Author", value=book['author'] or "")
                        new_publisher = st.text_input("Publisher", value=book['publisher'] or "")
                        new_year = st.text_input("Year", value=book['year'] or "")
                    
                    with col2:
                        new_language = st.text_input("Language", value=book['language'] or "")
                        new_file_type = st.text_input("File Type", value=book['file_type'] or "")
                        new_book_type = st.text_input("Book Type", value=book['book_type'] or "")
                    
                    update_submitted = st.form_submit_button("Update Book")
                    if update_submitted:
                        update_book(
                            md5_to_manage, new_title, new_author, new_publisher, 
                            new_year, new_language, new_file_type, new_book_type
                        )
                
                # Delete button
                st.subheader("Delete Book")
                st.warning("This action cannot be undone!")
                if st.button("Delete Book", key=f"delete_{md5_to_manage}"):
                    delete_book(md5_to_manage)
            else:
                st.error("Book not found with that MD5.")

if __name__ == "__main__":
    main()