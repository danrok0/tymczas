from sqlalchemy import or_
from src.models import Author, Book

class AuthorRepository:
    def __init__(self, session):
        self.session = session
    
    def add(self, author):
        """Add a new author to the database."""
        self.session.add(author)
        self.session.flush()
        return author
    
    def get_all(self):
        """Get all authors."""
        return self.session.query(Author).all()
    
    def get_by_id(self, author_id):
        """Get author by ID."""
        return self.session.query(Author).get(author_id)
    
    def search_by_name(self, name):
        """Search authors by name (first name or last name)."""
        return self.session.query(Author).filter(
            or_(
                Author.first_name.ilike(f'%{name}%'),
                Author.last_name.ilike(f'%{name}%')
            )
        ).all()
    
    def update(self, author):
        """Update author information."""
        self.session.merge(author)
        return author
    
    def delete(self, author_id):
        """Delete an author if they have no books."""
        author = self.get_by_id(author_id)
        if author and not author.books:
            self.session.delete(author)
            return True
        return False

class BookRepository:
    def __init__(self, session):
        self.session = session
    
    def add(self, book):
        """Add a new book to the database."""
        self.session.add(book)
        self.session.flush()
        return book
    
    def get_all(self):
        """Get all books."""
        return self.session.query(Book).all()
    
    def get_by_id(self, book_id):
        """Get book by ID."""
        return self.session.query(Book).get(book_id)
    
    def search(self, query):
        """Search books by title, author, or publication year."""
        return self.session.query(Book).join(Author).filter(
            or_(
                Book.title.ilike(f'%{query}%'),
                Author.first_name.ilike(f'%{query}%'),
                Author.last_name.ilike(f'%{query}%'),
                Book.publication_year == query if query.isdigit() else False
            )
        ).all()
    
    def get_by_author(self, author_id):
        """Get all books by a specific author."""
        return self.session.query(Book).filter(Book.author_id == author_id).all()
    
    def update(self, book):
        """Update book information."""
        self.session.merge(book)
        return book
    
    def delete(self, book_id):
        """Delete a book."""
        book = self.get_by_id(book_id)
        if book:
            self.session.delete(book)
            return True
        return False
    
    def get_statistics(self):
        """Get library statistics."""
        total_books = self.session.query(Book).count()
        total_authors = self.session.query(Author).count()
        
        oldest_book = self.session.query(Book).order_by(Book.publication_year).first()
        newest_book = self.session.query(Book).order_by(Book.publication_year.desc()).first()
        
        # Get authors with most books
        authors_with_books = self.session.query(
            Author, Book
        ).join(Book).group_by(Author.id).order_by(
            Book.id.desc()
        ).all()
        
        return {
            'total_books': total_books,
            'total_authors': total_authors,
            'oldest_book': oldest_book,
            'newest_book': newest_book,
            'authors_with_books': authors_with_books
        } 