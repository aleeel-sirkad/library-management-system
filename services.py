"""
Service layer for the Library Management System.

Provides CRUD operations and business logic for books, members, and borrowing.
"""

import sqlite3
from datetime import date
from typing import List, Optional

from database import DatabaseManager
from models import Book, Member, BorrowingRecord, ValidationError


class ServiceError(Exception):
  """Raised when a service operation fails."""

  pass


class BookService:
  """Handles CRUD operations for books."""

  def __init__(self, db_manager: DatabaseManager):
    self.db_manager = db_manager

  def add_book(self, book: Book) -> Book:
    """Insert a new book into the database."""
    try:
      with self.db_manager.get_connection() as conn:
        cursor = conn.execute(
          """
          INSERT INTO books (title, author, publication_year, quantity)
          VALUES (?, ?, ?, ?)
          """,
          (book.title, book.author, book.publication_year, book.quantity),
        )
        conn.commit()
        book.id = cursor.lastrowid
        return book
    except sqlite3.Error as exc:
      raise ServiceError(f"Failed to add book: {exc}") from exc

  def get_all_books(self) -> List[Book]:
    """Retrieve all books from the database."""
    try:
      with self.db_manager.get_connection() as conn:
        rows = conn.execute(
          "SELECT * FROM books ORDER BY title ASC"
        ).fetchall()
        return [Book.from_row(row) for row in rows]
    except sqlite3.Error as exc:
      raise ServiceError(f"Failed to retrieve books: {exc}") from exc

  def get_book_by_id(self, book_id: int) -> Optional[Book]:
    """Retrieve a single book by its ID."""
    try:
      with self.db_manager.get_connection() as conn:
        row = conn.execute(
          "SELECT * FROM books WHERE id = ?", (book_id,)
        ).fetchone()
        return Book.from_row(row) if row else None
    except sqlite3.Error as exc:
      raise ServiceError(f"Failed to retrieve book: {exc}") from exc

  def update_book(self, book: Book) -> Book:
    """Update an existing book."""
    if book.id is None:
      raise ServiceError("Book ID is required for update.")

    try:
      with self.db_manager.get_connection() as conn:
        cursor = conn.execute(
          """
          UPDATE books
          SET title = ?, author = ?, publication_year = ?, quantity = ?
          WHERE id = ?
          """,
          (
            book.title,
            book.author,
            book.publication_year,
            book.quantity,
            book.id,
          ),
        )
        conn.commit()
        if cursor.rowcount == 0:
          raise ServiceError(f"Book with ID {book.id} not found.")
        return book
    except sqlite3.Error as exc:
      raise ServiceError(f"Failed to update book: {exc}") from exc

  def delete_book(self, book_id: int) -> bool:
    """Delete a book by its ID."""
    try:
      with self.db_manager.get_connection() as conn:
        active_loans = conn.execute(
          """
          SELECT COUNT(*) AS count FROM borrowing_records
          WHERE book_id = ? AND status = 'borrowed'
          """,
          (book_id,),
        ).fetchone()["count"]

        if active_loans > 0:
          raise ServiceError(
            "Cannot delete book with active borrowing records."
          )

        cursor = conn.execute("DELETE FROM books WHERE id = ?", (book_id,))
        conn.commit()
        if cursor.rowcount == 0:
          raise ServiceError(f"Book with ID {book_id} not found.")
        return True
    except sqlite3.Error as exc:
      raise ServiceError(f"Failed to delete book: {exc}") from exc

  def search_books(self, query: str) -> List[Book]:
    """Search books by title or author (case-insensitive partial match)."""
    if not query or not query.strip():
      raise ValidationError("Search query cannot be empty.")

    search_term = f"%{query.strip()}%"
    try:
      with self.db_manager.get_connection() as conn:
        rows = conn.execute(
          """
          SELECT * FROM books
          WHERE title LIKE ? OR author LIKE ?
          ORDER BY title ASC
          """,
          (search_term, search_term),
        ).fetchall()
        return [Book.from_row(row) for row in rows]
    except sqlite3.Error as exc:
      raise ServiceError(f"Failed to search books: {exc}") from exc


class MemberService:
  """Handles CRUD operations for members."""

  def __init__(self, db_manager: DatabaseManager):
    self.db_manager = db_manager

  def add_member(self, member: Member) -> Member:
    """Insert a new member into the database."""
    try:
      with self.db_manager.get_connection() as conn:
        cursor = conn.execute(
          """
          INSERT INTO members (full_name, email, phone)
          VALUES (?, ?, ?)
          """,
          (member.full_name, member.email, member.phone),
        )
        conn.commit()
        member.id = cursor.lastrowid
        return member
    except sqlite3.IntegrityError as exc:
      raise ServiceError("A member with this email already exists.") from exc
    except sqlite3.Error as exc:
      raise ServiceError(f"Failed to add member: {exc}") from exc

  def get_all_members(self) -> List[Member]:
    """Retrieve all members from the database."""
    try:
      with self.db_manager.get_connection() as conn:
        rows = conn.execute(
          "SELECT * FROM members ORDER BY full_name ASC"
        ).fetchall()
        return [Member.from_row(row) for row in rows]
    except sqlite3.Error as exc:
      raise ServiceError(f"Failed to retrieve members: {exc}") from exc

  def get_member_by_id(self, member_id: int) -> Optional[Member]:
    """Retrieve a single member by ID."""
    try:
      with self.db_manager.get_connection() as conn:
        row = conn.execute(
          "SELECT * FROM members WHERE id = ?", (member_id,)
        ).fetchone()
        return Member.from_row(row) if row else None
    except sqlite3.Error as exc:
      raise ServiceError(f"Failed to retrieve member: {exc}") from exc

  def update_member(self, member: Member) -> Member:
    """Update an existing member."""
    if member.id is None:
      raise ServiceError("Member ID is required for update.")

    try:
      with self.db_manager.get_connection() as conn:
        cursor = conn.execute(
          """
          UPDATE members
          SET full_name = ?, email = ?, phone = ?
          WHERE id = ?
          """,
          (member.full_name, member.email, member.phone, member.id),
        )
        conn.commit()
        if cursor.rowcount == 0:
          raise ServiceError(f"Member with ID {member.id} not found.")
        return member
    except sqlite3.IntegrityError as exc:
      raise ServiceError("A member with this email already exists.") from exc
    except sqlite3.Error as exc:
      raise ServiceError(f"Failed to update member: {exc}") from exc

  def delete_member(self, member_id: int) -> bool:
    """Delete a member by ID."""
    try:
      with self.db_manager.get_connection() as conn:
        active_loans = conn.execute(
          """
          SELECT COUNT(*) AS count FROM borrowing_records
          WHERE member_id = ? AND status = 'borrowed'
          """,
          (member_id,),
        ).fetchone()["count"]

        if active_loans > 0:
          raise ServiceError(
            "Cannot delete member with active borrowing records."
          )

        cursor = conn.execute("DELETE FROM members WHERE id = ?", (member_id,))
        conn.commit()
        if cursor.rowcount == 0:
          raise ServiceError(f"Member with ID {member_id} not found.")
        return True
    except sqlite3.Error as exc:
      raise ServiceError(f"Failed to delete member: {exc}") from exc


class BorrowingService:
  """Handles borrowing and returning books."""

  def __init__(self, db_manager: DatabaseManager):
    self.db_manager = db_manager
    self.book_service = BookService(db_manager)
    self.member_service = MemberService(db_manager)

  def borrow_book(self, book_id: int, member_id: int) -> BorrowingRecord:
    """
    Record a book borrowing transaction.

    Decrements available quantity and creates a borrowing record.
    """
    book = self.book_service.get_book_by_id(book_id)
    if book is None:
      raise ServiceError(f"Book with ID {book_id} not found.")

    member = self.member_service.get_member_by_id(member_id)
    if member is None:
      raise ServiceError(f"Member with ID {member_id} not found.")

    if book.quantity <= 0:
      raise ServiceError("No copies of this book are available.")

    borrow_date = date.today().isoformat()
    record = BorrowingRecord(
      book_id=book_id,
      member_id=member_id,
      borrow_date=borrow_date,
      status="borrowed",
    )

    try:
      with self.db_manager.get_connection() as conn:
        conn.execute(
          "UPDATE books SET quantity = quantity - 1 WHERE id = ?",
          (book_id,),
        )
        cursor = conn.execute(
          """
          INSERT INTO borrowing_records
          (book_id, member_id, borrow_date, return_date, status)
          VALUES (?, ?, ?, NULL, 'borrowed')
          """,
          (book_id, member_id, borrow_date),
        )
        conn.commit()
        record.id = cursor.lastrowid
        return record
    except sqlite3.Error as exc:
      raise ServiceError(f"Failed to borrow book: {exc}") from exc

  def return_book(self, record_id: int) -> BorrowingRecord:
    """
    Mark a borrowing record as returned.

    Increments available book quantity and sets return date.
    """
    try:
      with self.db_manager.get_connection() as conn:
        row = conn.execute(
          "SELECT * FROM borrowing_records WHERE id = ?", (record_id,)
        ).fetchone()

        if row is None:
          raise ServiceError(f"Borrowing record with ID {record_id} not found.")

        if row["status"] == "returned":
          raise ServiceError("This book has already been returned.")

        return_date = date.today().isoformat()
        conn.execute(
          """
          UPDATE borrowing_records
          SET return_date = ?, status = 'returned'
          WHERE id = ?
          """,
          (return_date, record_id),
        )
        conn.execute(
          "UPDATE books SET quantity = quantity + 1 WHERE id = ?",
          (row["book_id"],),
        )
        conn.commit()

        updated = conn.execute(
          "SELECT * FROM borrowing_records WHERE id = ?", (record_id,)
        ).fetchone()
        return BorrowingRecord.from_row(updated)
    except sqlite3.Error as exc:
      raise ServiceError(f"Failed to return book: {exc}") from exc

  def get_all_records(self) -> List[dict]:
    """
    Retrieve all borrowing records with book and member details.

    Returns:
        List of dictionaries containing joined record information.
    """
    try:
      with self.db_manager.get_connection() as conn:
        rows = conn.execute(
          """
          SELECT
            br.id,
            br.book_id,
            b.title AS book_title,
            br.member_id,
            m.full_name AS member_name,
            br.borrow_date,
            br.return_date,
            br.status
          FROM borrowing_records br
          JOIN books b ON br.book_id = b.id
          JOIN members m ON br.member_id = m.id
          ORDER BY br.borrow_date DESC
          """
        ).fetchall()
        return [dict(row) for row in rows]
    except sqlite3.Error as exc:
      raise ServiceError(f"Failed to retrieve borrowing records: {exc}") from exc

  def get_active_borrowings(self) -> List[dict]:
    """Retrieve only active (not yet returned) borrowing records."""
    try:
      with self.db_manager.get_connection() as conn:
        rows = conn.execute(
          """
          SELECT
            br.id,
            br.book_id,
            b.title AS book_title,
            br.member_id,
            m.full_name AS member_name,
            br.borrow_date,
            br.return_date,
            br.status
          FROM borrowing_records br
          JOIN books b ON br.book_id = b.id
          JOIN members m ON br.member_id = m.id
          WHERE br.status = 'borrowed'
          ORDER BY br.borrow_date DESC
          """
        ).fetchall()
        return [dict(row) for row in rows]
    except sqlite3.Error as exc:
      raise ServiceError(
        f"Failed to retrieve active borrowings: {exc}"
      ) from exc
