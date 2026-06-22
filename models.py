"""
Data models for the Library Management System.

Defines Book, Member, and BorrowingRecord classes with input validation.
"""

import re
from dataclasses import dataclass
from datetime import datetime
from typing import Optional


class ValidationError(Exception):
  """Raised when model data fails validation."""

  pass


# Simple email pattern for basic validation
EMAIL_PATTERN = re.compile(r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$")


def _validate_non_empty(value: str, field_name: str) -> str:
  """Ensure a string field is not empty after stripping whitespace."""
  cleaned = value.strip()
  if not cleaned:
    raise ValidationError(f"{field_name} cannot be empty.")
  return cleaned


def _validate_email(email: str) -> str:
  """Validate email format."""
  cleaned = _validate_non_empty(email, "Email")
  if not EMAIL_PATTERN.match(cleaned):
    raise ValidationError("Invalid email format.")
  return cleaned.lower()


def _validate_year(year: int) -> int:
  """Validate publication year is within a reasonable range."""
  current_year = datetime.now().year
  if year < 1000 or year > current_year:
    raise ValidationError(
      f"Publication year must be between 1000 and {current_year}."
    )
  return year


def _validate_quantity(quantity: int) -> int:
  """Validate book quantity is non-negative."""
  if quantity < 0:
    raise ValidationError("Quantity cannot be negative.")
  return quantity


@dataclass
class Book:
  """Represents a book in the library catalog."""

  title: str
  author: str
  publication_year: int
  quantity: int = 1
  id: Optional[int] = None

  def __post_init__(self) -> None:
    """Validate book fields after initialization."""
    self.title = _validate_non_empty(self.title, "Title")
    self.author = _validate_non_empty(self.author, "Author")
    self.publication_year = _validate_year(int(self.publication_year))
    self.quantity = _validate_quantity(int(self.quantity))

  def to_dict(self) -> dict:
    """Convert the book to a dictionary."""
    return {
      "id": self.id,
      "title": self.title,
      "author": self.author,
      "publication_year": self.publication_year,
      "quantity": self.quantity,
    }

  @classmethod
  def from_row(cls, row) -> "Book":
    """Create a Book instance from a database row."""
    return cls(
      id=row["id"],
      title=row["title"],
      author=row["author"],
      publication_year=row["publication_year"],
      quantity=row["quantity"],
    )


@dataclass
class Member:
  """Represents a library member."""

  full_name: str
  email: str
  phone: str
  id: Optional[int] = None

  def __post_init__(self) -> None:
    """Validate member fields after initialization."""
    self.full_name = _validate_non_empty(self.full_name, "Full name")
    self.email = _validate_email(self.email)
    self.phone = _validate_non_empty(self.phone, "Phone")

  def to_dict(self) -> dict:
    """Convert the member to a dictionary."""
    return {
      "id": self.id,
      "full_name": self.full_name,
      "email": self.email,
      "phone": self.phone,
    }

  @classmethod
  def from_row(cls, row) -> "Member":
    """Create a Member instance from a database row."""
    return cls(
      id=row["id"],
      full_name=row["full_name"],
      email=row["email"],
      phone=row["phone"],
    )


@dataclass
class BorrowingRecord:
  """Represents a book borrowing transaction."""

  book_id: int
  member_id: int
  borrow_date: str
  status: str = "borrowed"
  return_date: Optional[str] = None
  id: Optional[int] = None

  VALID_STATUSES = ("borrowed", "returned")

  def __post_init__(self) -> None:
    """Validate borrowing record fields after initialization."""
    if self.book_id is None or int(self.book_id) <= 0:
      raise ValidationError("A valid book ID is required.")
    if self.member_id is None or int(self.member_id) <= 0:
      raise ValidationError("A valid member ID is required.")
    self.book_id = int(self.book_id)
    self.member_id = int(self.member_id)
    self.borrow_date = _validate_non_empty(self.borrow_date, "Borrow date")
    self.status = self.status.strip().lower()
    if self.status not in self.VALID_STATUSES:
      raise ValidationError(
        f"Status must be one of: {', '.join(self.VALID_STATUSES)}."
      )
    if self.return_date is not None:
      self.return_date = self.return_date.strip() or None

  def to_dict(self) -> dict:
    """Convert the borrowing record to a dictionary."""
    return {
      "id": self.id,
      "book_id": self.book_id,
      "member_id": self.member_id,
      "borrow_date": self.borrow_date,
      "return_date": self.return_date,
      "status": self.status,
    }

  @classmethod
  def from_row(cls, row) -> "BorrowingRecord":
    """Create a BorrowingRecord instance from a database row."""
    return cls(
      id=row["id"],
      book_id=row["book_id"],
      member_id=row["member_id"],
      borrow_date=row["borrow_date"],
      return_date=row["return_date"],
      status=row["status"],
    )
