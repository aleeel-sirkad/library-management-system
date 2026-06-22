"""
Main entry point for the Library Management System CLI.

Provides an interactive menu for managing books, members, and borrowing records.
"""

import sys
from pathlib import Path

# Ensure project root is on the path when running as a script
sys.path.insert(0, str(Path(__file__).parent))

from database import DatabaseManager, DatabaseError
from models import Book, Member, ValidationError
from services import BookService, MemberService, BorrowingService, ServiceError


def prompt_int(message: str, allow_empty: bool = False) -> int | None:
    """
    Read and validate an integer from user input.

    Args:
        message: Prompt text displayed to the user.
        allow_empty: If True, empty input returns None.

    Returns:
        Validated integer or None when allow_empty is True.
    """
    while True:
        value = input(message).strip()
        if allow_empty and not value:
            return None
        try:
            return int(value)
        except ValueError:
            print("Invalid input. Please enter a valid number.")


def prompt_text(message: str, allow_empty: bool = False) -> str | None:
    """Read and validate non-empty text from user input."""
    while True:
        value = input(message).strip()
        if value or allow_empty:
            return value if value else None
        print("This field cannot be empty.")


def print_header(title: str) -> None:
    """Print a formatted section header."""
    print("\n" + "=" * 50)
    print(f"  {title}")
    print("=" * 50)


def print_books(books: list[Book]) -> None:
    """Display a list of books in a formatted table."""
    if not books:
        print("\nNo books found.")
        return

    print(
        f"\n{'ID':<5} {'Title':<25} {'Author':<20} "
        f"{'Year':<6} {'Qty':<5}"
    )
    print("-" * 65)
    for book in books:
        title = book.title[:24]
        author = book.author[:19]
        print(
            f"{book.id:<5} {title:<25} {author:<20} "
            f"{book.publication_year:<6} {book.quantity:<5}"
        )


def print_members(members: list[Member]) -> None:
    """Display a list of members in a formatted table."""
    if not members:
        print("\nNo members found.")
        return

    print(f"\n{'ID':<5} {'Name':<25} {'Email':<30} {'Phone':<15}")
    print("-" * 80)
    for member in members:
        name = member.full_name[:24]
        email = member.email[:29]
        print(
            f"{member.id:<5} {name:<25} {email:<30} {member.phone:<15}"
        )


def print_borrowing_records(records: list[dict]) -> None:
    """Display borrowing records in a formatted table."""
    if not records:
        print("\nNo borrowing records found.")
        return

    print(
        f"\n{'ID':<5} {'Book':<22} {'Member':<20} "
        f"{'Borrowed':<12} {'Returned':<12} {'Status':<10}"
    )
    print("-" * 90)
    for record in records:
        book_title = record["book_title"][:21]
        member_name = record["member_name"][:19]
        returned = record["return_date"] or "-"
        print(
            f"{record['id']:<5} {book_title:<22} {member_name:<20} "
            f"{record['borrow_date']:<12} {returned:<12} {record['status']:<10}"
        )


def handle_error(exc: Exception) -> None:
    """Display a user-friendly error message."""
    print(f"\nError: {exc}")


class LibraryCLI:
    """Command-line interface for the Library Management System."""

    def __init__(self):
        """Initialize services and database connection."""
        self.db_manager = DatabaseManager()
        self.book_service = BookService(self.db_manager)
        self.member_service = MemberService(self.db_manager)
        self.borrowing_service = BorrowingService(self.db_manager)

    def add_book(self) -> None:
        """Prompt user for book details and add to the catalog."""
        print_header("Add New Book")
        try:
            title = prompt_text("Title: ")
            author = prompt_text("Author: ")
            year = prompt_int("Publication year: ")
            quantity = prompt_int("Quantity: ")

            book = Book(
                title=title,
                author=author,
                publication_year=year,
                quantity=quantity,
            )
            created = self.book_service.add_book(book)
            print(f"\nBook added successfully with ID {created.id}.")
        except (ValidationError, ServiceError) as exc:
            handle_error(exc)

    def view_books(self) -> None:
        """Display all books in the catalog."""
        print_header("All Books")
        try:
            books = self.book_service.get_all_books()
            print_books(books)
        except ServiceError as exc:
            handle_error(exc)

    def update_book(self) -> None:
        """Update an existing book's details."""
        print_header("Update Book")
        try:
            book_id = prompt_int("Enter book ID to update: ")
            existing = self.book_service.get_book_by_id(book_id)
            if existing is None:
                print(f"\nBook with ID {book_id} not found.")
                return

            print(f"\nCurrent: {existing.title} by {existing.author}")
            title = prompt_text(
                f"New title [{existing.title}]: ", allow_empty=True
            ) or existing.title
            author = prompt_text(
                f"New author [{existing.author}]: ", allow_empty=True
            ) or existing.author
            year_input = input(
                f"New year [{existing.publication_year}]: "
            ).strip()
            year = int(year_input) if year_input else existing.publication_year
            qty_input = input(f"New quantity [{existing.quantity}]: ").strip()
            quantity = int(qty_input) if qty_input else existing.quantity

            updated = Book(
                id=book_id,
                title=title,
                author=author,
                publication_year=year,
                quantity=quantity,
            )
            self.book_service.update_book(updated)
            print("\nBook updated successfully.")
        except (ValidationError, ServiceError, ValueError) as exc:
            handle_error(exc)

    def delete_book(self) -> None:
        """Delete a book from the catalog."""
        print_header("Delete Book")
        try:
            book_id = prompt_int("Enter book ID to delete: ")
            confirm = prompt_text("Are you sure? (yes/no): ").lower()
            if confirm == "yes":
                self.book_service.delete_book(book_id)
                print("\nBook deleted successfully.")
            else:
                print("\nDeletion cancelled.")
        except ServiceError as exc:
            handle_error(exc)

    def search_books(self) -> None:
        """Search books by title or author."""
        print_header("Search Books")
        try:
            query = prompt_text("Enter title or author to search: ")
            results = self.book_service.search_books(query)
            print(f"\nFound {len(results)} result(s):")
            print_books(results)
        except (ValidationError, ServiceError) as exc:
            handle_error(exc)

    def add_member(self) -> None:
        """Prompt user for member details and register them."""
        print_header("Add New Member")
        try:
            full_name = prompt_text("Full name: ")
            email = prompt_text("Email: ")
            phone = prompt_text("Phone: ")

            member = Member(full_name=full_name, email=email, phone=phone)
            created = self.member_service.add_member(member)
            print(f"\nMember added successfully with ID {created.id}.")
        except (ValidationError, ServiceError) as exc:
            handle_error(exc)

    def view_members(self) -> None:
        """Display all registered members."""
        print_header("All Members")
        try:
            members = self.member_service.get_all_members()
            print_members(members)
        except ServiceError as exc:
            handle_error(exc)

    def update_member(self) -> None:
        """Update an existing member's details."""
        print_header("Update Member")
        try:
            member_id = prompt_int("Enter member ID to update: ")
            existing = self.member_service.get_member_by_id(member_id)
            if existing is None:
                print(f"\nMember with ID {member_id} not found.")
                return

            print(f"\nCurrent: {existing.full_name} ({existing.email})")
            full_name = prompt_text(
                f"New name [{existing.full_name}]: ", allow_empty=True
            ) or existing.full_name
            email = prompt_text(
                f"New email [{existing.email}]: ", allow_empty=True
            ) or existing.email
            phone = prompt_text(
                f"New phone [{existing.phone}]: ", allow_empty=True
            ) or existing.phone

            updated = Member(
                id=member_id,
                full_name=full_name,
                email=email,
                phone=phone,
            )
            self.member_service.update_member(updated)
            print("\nMember updated successfully.")
        except (ValidationError, ServiceError) as exc:
            handle_error(exc)

    def delete_member(self) -> None:
        """Remove a member from the system."""
        print_header("Delete Member")
        try:
            member_id = prompt_int("Enter member ID to delete: ")
            confirm = prompt_text("Are you sure? (yes/no): ").lower()
            if confirm == "yes":
                self.member_service.delete_member(member_id)
                print("\nMember deleted successfully.")
            else:
                print("\nDeletion cancelled.")
        except ServiceError as exc:
            handle_error(exc)

    def borrow_book(self) -> None:
        """Record a book borrowing transaction."""
        print_header("Borrow Book")
        try:
            book_id = prompt_int("Enter book ID: ")
            member_id = prompt_int("Enter member ID: ")
            record = self.borrowing_service.borrow_book(book_id, member_id)
            print(
                f"\nBook borrowed successfully. Record ID: {record.id}"
            )
        except ServiceError as exc:
            handle_error(exc)

    def return_book(self) -> None:
        """Process a book return."""
        print_header("Return Book")
        try:
            print("\nActive borrowings:")
            active = self.borrowing_service.get_active_borrowings()
            print_borrowing_records(active)

            record_id = prompt_int("\nEnter borrowing record ID to return: ")
            record = self.borrowing_service.return_book(record_id)
            print(
                f"\nBook returned successfully on {record.return_date}."
            )
        except ServiceError as exc:
            handle_error(exc)

    def view_borrowing_records(self) -> None:
        """Display all borrowing records."""
        print_header("Borrowing Records")
        try:
            records = self.borrowing_service.get_all_records()
            print_borrowing_records(records)
        except ServiceError as exc:
            handle_error(exc)

    def display_main_menu(self) -> None:
        """Print the main application menu."""
        print_header("Library Management System")
        print("  BOOKS")
        print("    1.  Add Book")
        print("    2.  View Books")
        print("    3.  Update Book")
        print("    4.  Delete Book")
        print("    5.  Search Books")
        print("  MEMBERS")
        print("    6.  Add Member")
        print("    7.  View Members")
        print("    8.  Update Member")
        print("    9.  Delete Member")
        print("  BORROWING")
        print("    10. Borrow Book")
        print("    11. Return Book")
        print("    12. View Borrowing Records")
        print("  0.  Exit")

    def run(self) -> None:
        """Run the main application loop."""
        actions = {
            "1": self.add_book,
            "2": self.view_books,
            "3": self.update_book,
            "4": self.delete_book,
            "5": self.search_books,
            "6": self.add_member,
            "7": self.view_members,
            "8": self.update_member,
            "9": self.delete_member,
            "10": self.borrow_book,
            "11": self.return_book,
            "12": self.view_borrowing_records,
        }

        print("\nWelcome to the Library Management System!")
        while True:
            self.display_main_menu()
            choice = input("\nEnter your choice: ").strip()

            if choice == "0":
                print("\nThank you for using the Library Management System. Goodbye!")
                break

            action = actions.get(choice)
            if action:
                action()
            else:
                print("\nInvalid choice. Please try again.")

            input("\nPress Enter to continue...")


def main() -> None:
    """Application entry point with top-level error handling."""
    try:
        cli = LibraryCLI()
        cli.run()
    except DatabaseError as exc:
        print(f"Database error: {exc}")
        sys.exit(1)
    except KeyboardInterrupt:
        print("\n\nApplication interrupted. Goodbye!")
        sys.exit(0)
    except EOFError:
        print("\n\nNo interactive input available. Run this app in a terminal:")
        print('  python main.py')
        sys.exit(0)


if __name__ == "__main__":
    main()
