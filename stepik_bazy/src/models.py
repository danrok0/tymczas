from sqlalchemy import Column, Integer, String, ForeignKey, Text
from sqlalchemy.orm import relationship, declarative_base

Base = declarative_base()

class Author(Base):
    __tablename__ = 'authors'
    
    id = Column(Integer, primary_key=True)
    first_name = Column(String(50), nullable=False)
    last_name = Column(String(50), nullable=False)
    birth_year = Column(Integer)
    nationality = Column(String(50))
    
    books = relationship("Book", back_populates="author", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<Author {self.first_name} {self.last_name}>"

class Book(Base):
    __tablename__ = 'books'
    
    id = Column(Integer, primary_key=True)
    title = Column(String(200), nullable=False)
    author_id = Column(Integer, ForeignKey('authors.id'), nullable=False)
    publication_year = Column(Integer)
    genre = Column(String(50))
    pages = Column(Integer)
    description = Column(Text)
    
    author = relationship("Author", back_populates="books")
    
    def __repr__(self):
        return f"<Book {self.title}>" 