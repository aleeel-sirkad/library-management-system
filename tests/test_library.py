"""
Unit tests for the Library Management System.

Uses a temporary in-memory-style database for isolated test execution.
"""

import os
import sys
import tempfile
import unittest
from pathlib import Path

# Add project root to path for imports
PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from database import DatabaseManager
from models import Book, Member, ValidationError
from services import BookService, MemberService, BorrowingService, ServiceError


class LibrarySystemTestCase(unittest.TestCase):
    """Base test case that sets up a fresh temporary database."""

    def setUp(self) -> None:
        """Create a temporary database and service instances."""
        self.temp_dir = tempfile.mkdtemp()
        self.db_path = os.path.join(self.temp_dir, "test_library.db")
        schema_path = PROJECT_ROOT / "schema.sql"

        self.db_manager = DatabaseManager(
            db_path=self.db_path, schema_path=str(schema_path)
        )
        self.book_service = BookService(self.db_manager)
        self.member_service = MemberService(self.db_manager)
        self.borrowing_service = BorrowingService(self.db_manager)

    def tearDown(self) -> None:
        """Remove temporary database files."""
        if os.path.exists(self.db_path):
            os.remove(self.db_path)
        os.rmdir(self.temp_dir)

    def _create_sample_book(self, title: str = "Test Book", quantity: int = 3) -> Book:
        """Helper to create and persist a sample book."""
        book = Book(
            title=title,
            author="Test Author",
            publication_year=2020,
            quantity=quantity,
        )
        return self.book_service.add_book(book)

    def _create_sample_member(self, email: str = "test@example.com") -> Member:
        """Helper to create and persist a sample member."""
        member = Member(
            full_name="Jane Doe",
            email=email,
            phone="555-0100",
        )
        return self.member_service.add_member(member)


class TestBookCRUD(LibrarySystemTestCase):
    """Tests for book CRUD operations."""

    def test_add_book(self) -> None:
        """Adding a book should assign an ID and persist data."""
        book = self._create_sample_book()
        self.assertIsNotNone(book.id)
        self.assertEqual(book.title, "Test Book")
        self.assertEqual(book.quantity, 3)

    def test_get_all_books(self) -> None:
        """get_all_books should return all inserted books."""
        self._create_sample_book("Book A")
        self._create_sample_book("Book B")
        books = self.book_service.get_all_books()
        self.assertEqual(len(books), 2)

    def test_update_book(self) -> None:
        """Updating a book should change its stored values."""
        book = self._create_sample_book()
        updated = Book(
            id=book.id,
            title="Updated Title",
            author="New Author",
            publication_year=2021,
            quantity=5,
        )
        result = self.book_service.update_book(updated)
        self.assertEqual(result.title, "Updated Title")
        self.assertEqual(result.quantity, 5)

        fetched = self.book_service.get_book_by_id(book.id)
        self.assertEqual(fetched.title, "Updated Title")

    def test_delete_book(self) -> None:
        """Deleting a book should remove it from the database."""
        book = self._create_sample_book()
        self.book_service.delete_book(book.id)
        self.assertIsNone(self.book_service.get_book_by_id(book.id))

    def test_search_books_by_title(self) -> None:
        """Search should find books matching title."""
        self._create_sample_book("Python Programming")
        self._create_sample_book("Java Basics")
        results = self.book_service.search_books("Python")
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0].title, "Python Programming")

    def test_search_books_by_author(self) -> None:
        """Search should find books matching author name."""
        book = Book(
            title="Some Title",
            author="Charles Dickens",
            publication_year=1859,
            quantity=1,
        )
        self.book_service.add_book(book)
        results = self.book_service.search_books("Dickens")
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0].author, "Charles Dickens")


class TestMemberCRUD(LibrarySystemTestCase):
    """Tests for member CRUD operations."""

    def test_add_member(self) -> None:
        """Adding a member should assign an ID and persist data."""
        member = self._create_sample_member()
        self.assertIsNotNone(member.id)
        self.assertEqual(member.email, "test@example.com")

    def test_update_member(self) -> None:
        """Updating a member should change stored values."""
        member = self._create_sample_member()
        updated = Member(
            id=member.id,
            full_name="John Smith",
            email="john@example.com",
            phone="555-0200",
        )
        result = self.member_service.update_member(updated)
        self.assertEqual(result.full_name, "John Smith")

    def test_delete_member(self) -> None:
        """Deleting a member should remove them from the database."""
        member = self._create_sample_member()
        self.member_service.delete_member(member.id)
        self.assertIsNone(self.member_service.get_member_by_id(member.id))

    def test_duplicate_email_rejected(self) -> None:
        """Adding a member with duplicate email should raise ServiceError."""
        self._create_sample_member("duplicate@example.com")
        with self.assertRaises(ServiceError):
            self._create_sample_member("duplicate@example.com")


class TestBorrowing(LibrarySystemTestCase):
    """Tests for borrowing and returning books."""

    def test_borrow_book(self) -> None:
        """Borrowing should create a record and decrease quantity."""
        book = self._create_sample_book(quantity=2)
        member = self._create_sample_member()

        record = self.borrowing_service.borrow_book(book.id, member.id)
        self.assertIsNotNone(record.id)
        self.assertEqual(record.status, "borrowed")

        updated_book = self.book_service.get_book_by_id(book.id)
        self.assertEqual(updated_book.quantity, 1)

    def test_return_book(self) -> None:
        """Returning should update record status and restore quantity."""
        book = self._create_sample_book(quantity=1)
        member = self._create_sample_member()

        record = self.borrowing_service.borrow_book(book.id, member.id)
        returned = self.borrowing_service.return_book(record.id)

        self.assertEqual(returned.status, "returned")
        self.assertIsNotNone(returned.return_date)

        updated_book = self.book_service.get_book_by_id(book.id)
        self.assertEqual(updated_book.quantity, 1)

    def test_borrow_unavailable_book(self) -> None:
        """Borrowing when quantity is zero should raise ServiceError."""
        book = self._create_sample_book(quantity=0)
        member = self._create_sample_member()

        with self.assertRaises(ServiceError):
            self.borrowing_service.borrow_book(book.id, member.id)

    def test_view_borrowing_records(self) -> None:
        """get_all_records should return joined book and member data."""
        book = self._create_sample_book()
        member = self._create_sample_member()
        self.borrowing_service.borrow_book(book.id, member.id)

        records = self.borrowing_service.get_all_records()
        self.assertEqual(len(records), 1)
        self.assertEqual(records[0]["book_title"], "Test Book")
        self.assertEqual(records[0]["member_name"], "Jane Doe")


class TestValidation(LibrarySystemTestCase):
    """Tests for input validation."""

    def test_invalid_email_raises_validation_error(self) -> None:
        """Invalid email format should be rejected."""
        with self.assertRaises(ValidationError):
            Member(full_name="Test User", email="not-an-email", phone="123")

    def test_invalid_publication_year(self) -> None:
        """Out-of-range publication year should be rejected."""
        with self.assertRaises(ValidationError):
            Book(
                title="Bad Year Book",
                author="Author",
                publication_year=999,
                quantity=1,
            )

    def test_empty_search_query(self) -> None:
        """Empty search query should raise ValidationError."""
        with self.assertRaises(ValidationError):
            self.book_service.search_books("   ")


if __name__ == "__main__":
    unittest.main()
