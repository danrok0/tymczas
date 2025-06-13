-- Enable foreign key support
PRAGMA foreign_keys = ON;

-- Create authors table
CREATE TABLE IF NOT EXISTS authors (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    first_name TEXT NOT NULL,
    last_name TEXT NOT NULL,
    birth_year INTEGER CHECK (birth_year > 1000),
    nationality TEXT DEFAULT 'Unknown'
);

-- Create books table
CREATE TABLE IF NOT EXISTS books (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT NOT NULL,
    author_id INTEGER NOT NULL,
    publication_year INTEGER CHECK (publication_year > 1000),
    genre TEXT,
    pages INTEGER CHECK (pages > 0),
    description TEXT,
    FOREIGN KEY (author_id) REFERENCES authors(id) ON DELETE RESTRICT
); 