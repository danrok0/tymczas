from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.exc import SQLAlchemyError
from contextlib import contextmanager
import os
import sqlite3

class DatabaseManager:
    def __init__(self, db_path="data/library.db"):
        # Ensure the data directory exists
        os.makedirs(os.path.dirname(db_path), exist_ok=True)
        
        self.db_path = db_path
        self.engine = create_engine(f'sqlite:///{db_path}')
        self.Session = sessionmaker(bind=self.engine)
    
    def initialize_database(self):
        """Create all tables in the database using schema.sql."""
        # Read and execute schema.sql
        schema_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'sql', 'schema.sql')
        with open(schema_path, 'r') as f:
            schema_sql = f.read()
        
        # Execute schema using sqlite3 directly
        with sqlite3.connect(self.db_path) as conn:
            conn.executescript(schema_sql)
    
    @contextmanager
    def get_session(self):
        """Provide a transactional scope around a series of operations."""
        session = self.Session()
        try:
            yield session
            session.commit()
        except SQLAlchemyError as e:
            session.rollback()
            raise e
        finally:
            session.close()
    
    def add_sample_data(self):
        """Add sample data to the database."""
        from src.models import Author, Book
        
        with self.get_session() as session:
            # Check if we already have data
            if session.query(Author).first():
                return
            
            # Add sample authors
            authors = [
                Author(first_name="Adam", last_name="Mickiewicz", birth_year=1798, nationality="Polish"),
                Author(first_name="Henryk", last_name="Sienkiewicz", birth_year=1846, nationality="Polish"),
                Author(first_name="Czesław", last_name="Miłosz", birth_year=1911, nationality="Polish")
            ]
            
            for author in authors:
                session.add(author)
            
            session.flush()  # Get IDs for authors
            
            # Add sample books
            books = [
                Book(title="Pan Tadeusz", author_id=authors[0].id, publication_year=1834, genre="Epic poem"),
                Book(title="Quo Vadis", author_id=authors[1].id, publication_year=1896, genre="Historical novel"),
                Book(title="Dolina Issy", author_id=authors[2].id, publication_year=1955, genre="Novel")
            ]
            
            for book in books:
                session.add(book) 