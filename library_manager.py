# library_manager_streamlit.py
import streamlit as st
import json
import os
from datetime import datetime

class LibraryManager:
    def __init__(self):
        self.filename = "library.txt"
        # Initialize the library in session state if it doesn't exist
        if 'library' not in st.session_state:
            st.session_state.library = []
            self.load_library()

    def add_book(self, title, author, year, genre, read_status):
        """Add a new book to the library."""
        book = {
            "title": title,
            "author": author,
            "year": year,
            "genre": genre,
            "read": read_status
        }
        
        st.session_state.library.append(book)
        self.save_library()
        return True

    def remove_book(self, index):
        """Remove a book from the library by index."""
        if 0 <= index < len(st.session_state.library):
            st.session_state.library.pop(index)
            self.save_library()
            return True
        return False

    def search_book(self, search_term, search_by):
        """Search for a book by title or author."""
        search_term = search_term.lower()
        if search_by == "Title":
            return [book for book in st.session_state.library if search_term in book["title"].lower()]
        else:  # Author
            return [book for book in st.session_state.library if search_term in book["author"].lower()]

    def get_statistics(self):
        """Get statistics about the library."""
        total_books = len(st.session_state.library)
        read_books = sum(1 for book in st.session_state.library if book["read"])
        percentage_read = (read_books / total_books) * 100 if total_books > 0 else 0
        
        return {
            "total_books": total_books,
            "read_books": read_books,
            "percentage_read": percentage_read
        }

    def save_library(self):
        """Save the library to a file."""
        with open(self.filename, 'w') as file:
            json.dump(st.session_state.library, file)

    def load_library(self):
        """Load the library from a file."""
        if os.path.exists(self.filename):
            try:
                with open(self.filename, 'r') as file:
                    st.session_state.library = json.load(file)
            except json.JSONDecodeError:
                st.error("Error loading library file. Starting with an empty library.")
        else:
            st.info("No existing library file found. Starting with an empty library.")

def main():
    st.set_page_config(page_title="Personal Library Manager", page_icon="📚")
    
    st.title("📚 Personal Library Manager")
    
    manager = LibraryManager()
    
    # Sidebar for navigation
    st.sidebar.title("Navigation")
    page = st.sidebar.radio("Go to", ["View Library", "Add Book", "Search Books", "Statistics"])
    
    # View Library page
    if page == "View Library":
        st.header("Your Library")
        
        if not st.session_state.library:
            st.info("Your library is empty! Add some books to get started.")
        else:
            for i, book in enumerate(st.session_state.library):
                col1, col2, col3 = st.columns([3, 1, 1])
                read_status = "Read" if book["read"] else "Unread"
                
                with col1:
                    st.write(f"**{book['title']}** by {book['author']} ({book['year']})")
                    st.write(f"Genre: {book['genre']} | Status: {read_status}")
                
                with col3:
                    if st.button("Remove", key=f"remove_{i}"):
                        if manager.remove_book(i):
                            st.success("Book removed successfully!")
                            st.rerun()
                
                st.divider()
    
    # Add Book page
    elif page == "Add Book":
        st.header("Add a New Book")
        
        with st.form("add_book_form"):
            title = st.text_input("Book Title")
            author = st.text_input("Author")
            year = st.number_input("Publication Year", min_value=1, max_value=datetime.now().year, value=2023)
            genre = st.text_input("Genre")
            read_status = st.checkbox("Have you read this book?")
            
            submitted = st.form_submit_button("Add Book")
            
            if submitted:
                if title and author:
                    if manager.add_book(title, author, year, genre, read_status):
                        st.success(f"'{title}' added to your library!")
                else:
                    st.error("Title and author are required!")
    
    # Search Books page
    elif page == "Search Books":
        st.header("Search for Books")
        
        search_by = st.radio("Search by:", ["Title", "Author"])
        search_term = st.text_input(f"Enter {search_by.lower()} to search:")
        
        if search_term:
            results = manager.search_book(search_term, search_by)
            
            if results:
                st.subheader(f"Found {len(results)} matching books:")
                
                for i, book in enumerate(results):
                    read_status = "Read" if book["read"] else "Unread"
                    st.write(f"**{book['title']}** by {book['author']} ({book['year']}) - {book['genre']} - {read_status}")
                    st.divider()
            else:
                st.info(f"No books found matching '{search_term}'")
    
    # Statistics page
    elif page == "Statistics":
        st.header("Library Statistics")
        
        stats = manager.get_statistics()
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.metric("Total Books", stats["total_books"])
        
        with col2:
            st.metric("Books Read", f"{stats['read_books']} ({stats['percentage_read']:.1f}%)")
        
        # Add a simple chart
        if stats["total_books"] > 0:
            st.subheader("Reading Status")
            
            # Create data for the chart
            read_count = stats["read_books"]
            unread_count = stats["total_books"] - read_count
            
            # Create a bar chart
            import matplotlib.pyplot as plt
            
            fig, ax = plt.subplots()
            ax.bar(["Read", "Unread"], [read_count, unread_count], color=["green", "orange"])
            ax.set_ylabel("Number of Books")
            st.pyplot(fig)

if __name__ == "__main__":
    main()