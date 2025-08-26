#!/usr/bin/env python3
"""
Enhanced Book Dashboard - Streamlit application for managing books in the database
"""

import streamlit as st
import psycopg2
import pandas as pd
import config
from datetime import datetime
import plotly.express as px
import plotly.graph_objects as go

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

def get_books_stats():
    """Get statistics about books in the database."""
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        
        # Total books
        cur.execute("SELECT COUNT(*) FROM books")
        total_books = cur.fetchone()[0]
        
        # Books by download status
        cur.execute("SELECT download_status, COUNT(*) FROM books GROUP BY download_status")
        download_stats = cur.fetchall()
        
        # Books with Drive URL
        cur.execute("SELECT COUNT(*) FROM books WHERE drive_download_url IS NOT NULL AND drive_download_url != ''")
        drive_url_count = cur.fetchone()[0]
        
        # Books by file type
        cur.execute("SELECT file_type, COUNT(*) FROM books WHERE file_type IS NOT NULL GROUP BY file_type ORDER BY COUNT(*) DESC LIMIT 10")
        file_type_stats = cur.fetchall()
        
        # Books by year
        cur.execute("SELECT year, COUNT(*) FROM books WHERE year IS NOT NULL GROUP BY year ORDER BY year DESC LIMIT 10")
        year_stats = cur.fetchall()
        
        cur.close()
        conn.close()
        
        return {
            'total_books': total_books,
            'download_stats': download_stats,
            'drive_url_count': drive_url_count,
            'file_type_stats': file_type_stats,
            'year_stats': year_stats
        }
    except Exception as e:
        st.error(f"Error fetching statistics: {e}")
        return None

def get_books_with_drive_urls(limit=20):
    """Get books with Drive URLs for the card view."""
    try:
        conn = get_db_connection()
        df = pd.read_sql_query(
            """SELECT title, author, md5, file_type, year, drive_download_url, downloaded_filename 
               FROM books 
               WHERE drive_download_url IS NOT NULL AND drive_download_url != '' 
               ORDER BY id DESC 
               LIMIT %s""", 
            conn, 
            params=(limit,)
        )
        conn.close()
        return df
    except Exception as e:
        st.error(f"Error fetching books with Drive URLs: {e}")
        return pd.DataFrame()

# Streamlit UI
def main():
    st.set_page_config(
        page_title="Enhanced Book Dashboard",
        page_icon="📚",
        layout="wide"
    )
    
    st.title("📚 Enhanced Book Dashboard")
    st.markdown("Manage your book collection with this dashboard")
    
    # Create tabs for different functionalities
    tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs(["📊 Dashboard", "📚 View Books", "🔍 Search Books", "➕ Add Book", "⚙️ Manage Books", "📖 Book Collection"])
    
    # Tab 1: Dashboard with statistics
    with tab1:
        st.header("Dashboard Statistics")
        stats = get_books_stats()
        
        if stats:
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                st.metric("Total Books", stats['total_books'])
            
            with col2:
                st.metric("Books with Drive URL", stats['drive_url_count'])
            
            with col3:
                download_status_df = pd.DataFrame(stats['download_stats'], columns=['Status', 'Count'])
                fig_download = px.pie(download_status_df, values='Count', names='Status', title='Books by Download Status')
                st.plotly_chart(fig_download, use_container_width=True)
            
            with col4:
                file_type_df = pd.DataFrame(stats['file_type_stats'], columns=['File Type', 'Count'])
                fig_filetype = px.bar(file_type_df, x='File Type', y='Count', title='Top File Types')
                st.plotly_chart(fig_filetype, use_container_width=True)
            
            # Year distribution
            st.subheader("Books by Year")
            year_df = pd.DataFrame(stats['year_stats'], columns=['Year', 'Count'])
            fig_year = px.line(year_df, x='Year', y='Count', title='Books Distribution by Year')
            st.plotly_chart(fig_year, use_container_width=True)
        else:
            st.info("No statistics available.")
    
    # Tab 2: View all books
    with tab2:
        st.header("All Books")
        books_df = get_all_books()
        if not books_df.empty:
            # Filters
            col1, col2, col3 = st.columns(3)
            
            with col1:
                file_types = ['All'] + list(books_df['file_type'].dropna().unique())
                selected_file_type = st.selectbox("Filter by File Type", file_types)
            
            with col2:
                download_statuses = ['All'] + list(books_df['download_status'].dropna().unique())
                selected_status = st.selectbox("Filter by Download Status", download_statuses)
            
            with col3:
                search_term = st.text_input("Search in results")
            
            # Apply filters
            filtered_df = books_df.copy()
            if selected_file_type != 'All':
                filtered_df = filtered_df[filtered_df['file_type'] == selected_file_type]
            if selected_status != 'All':
                filtered_df = filtered_df[filtered_df['download_status'] == selected_status]
            if search_term:
                filtered_df = filtered_df[
                    filtered_df['title'].str.contains(search_term, case=False, na=False) |
                    filtered_df['author'].str.contains(search_term, case=False, na=False) |
                    filtered_df['md5'].str.contains(search_term, case=False, na=False)
                ]
            
            st.dataframe(filtered_df, use_container_width=True, height=600)
            
            # Download button for CSV
            csv = filtered_df.to_csv(index=False)
            st.download_button(
                label="Download Filtered Books as CSV",
                data=csv,
                file_name=f"books_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                mime="text/csv"
            )
        else:
            st.info("No books found in the database.")
    
    # Tab 3: Search books
    with tab3:
        st.header("Search Books")
        query = st.text_input("Enter search term (title, author, or MD5)")
        if query:
            search_results = search_books(query)
            if not search_results.empty:
                st.dataframe(search_results, use_container_width=True)
            else:
                st.info("No books found matching your search.")
    
    # Tab 4: Add new book
    with tab4:
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
    
    # Tab 5: Manage books (edit/delete)
    with tab5:
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
    
    # Tab 6: Book collection with Drive URLs
    with tab6:
        st.header("Book Collection with Drive URLs")
        st.markdown("Books that have been uploaded to Google Drive")
        
        books_with_drive = get_books_with_drive_urls(50)
        
        if not books_with_drive.empty:
            # Search within Drive books
            search_drive = st.text_input("Search in Drive books")
            if search_drive:
                books_with_drive = books_with_drive[
                    books_with_drive['title'].str.contains(search_drive, case=False, na=False) |
                    books_with_drive['author'].str.contains(search_drive, case=False, na=False)
                ]
            
            # Display books as cards
            st.subheader(f"Showing {len(books_with_drive)} books with Drive URLs")
            
            # Group books in rows of 3
            for i in range(0, len(books_with_drive), 3):
                cols = st.columns(3)
                for j in range(3):
                    if i + j < len(books_with_drive):
                        book = books_with_drive.iloc[i + j]
                        with cols[j]:
                            st.markdown(f"### {book['title']}")
                            if book['author']:
                                st.markdown(f"**Author:** {book['author']}")
                            if book['year']:
                                st.markdown(f"**Year:** {book['year']}")
                            if book['file_type']:
                                st.markdown(f"**File Type:** {book['file_type']}")
                            if book['downloaded_filename']:
                                st.markdown(f"**Filename:** {book['downloaded_filename']}")
                            
                            # Drive download button
                            if book['drive_download_url']:
                                st.link_button("Download from Drive", book['drive_download_url'])
                            
                            # MD5 info
                            st.caption(f"MD5: {book['md5']}")
                            st.markdown("---")
        else:
            st.info("No books with Drive URLs found.")

if __name__ == "__main__":
    main()