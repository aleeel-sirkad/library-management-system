-- Library Management System - Database Schema
-- SQLite tables for books, members, and borrowing records

CREATE TABLE IF NOT EXISTS books (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT NOT NULL,
    author TEXT NOT NULL,
    publication_year INTEGER NOT NULL,
    quantity INTEGER NOT NULL DEFAULT 1 CHECK (quantity >= 0)
);

CREATE TABLE IF NOT EXISTS members (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    full_name TEXT NOT NULL,
    email TEXT NOT NULL UNIQUE,
    phone TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS borrowing_records (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    book_id INTEGER NOT NULL,
    member_id INTEGER NOT NULL,
    borrow_date TEXT NOT NULL,
    return_date TEXT,
    status TEXT NOT NULL DEFAULT 'borrowed' CHECK (status IN ('borrowed', 'returned')),
    FOREIGN KEY (book_id) REFERENCES books (id) ON DELETE CASCADE,
    FOREIGN KEY (member_id) REFERENCES members (id) ON DELETE CASCADE
);

CREATE INDEX IF NOT EXISTS idx_books_title ON books (title);
CREATE INDEX IF NOT EXISTS idx_books_author ON books (author);
CREATE INDEX IF NOT EXISTS idx_borrowing_status ON borrowing_records (status);
