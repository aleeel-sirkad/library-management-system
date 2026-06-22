# Library Management System

A complete **Library Management System** built with **Python** and **SQLite**. This project demonstrates object-oriented programming, relational database design, CRUD operations, and a command-line interface suitable for academic submission and portfolio use.

---

## Project Description

The Library Management System allows librarians to manage a catalog of books, register library members, and track book borrowing and returns. Data is persisted in a local SQLite database that is created automatically on first run.

The application is organized into separate modules for database access, data models, business logic, and the user interface, following clean separation of concerns and OOP principles.

---

## Features

### Books
- Add, view, update, and delete books
- Search books by title or author
- Track available quantity per title

### Members
- Add, view, update, and delete members
- Unique email validation per member

### Borrowing
- Borrow books (decrements available quantity)
- Return books (restores quantity, records return date)
- View full borrowing history with book and member details

### Technical Highlights
- Object-oriented design with dedicated service classes
- Input validation and error handling
- Automatic database and table creation
- Interactive CLI menu system
- Unit tests with `unittest`

---

## Installation

### Prerequisites
- Python 3.10 or higher
- No external packages required (standard library only)

### Steps

1. **Clone the repository**
   ```bash
   git clone https://github.com/aleeel-sirkad/library-management-system.git
   cd library-management-system
   ```

2. **(Optional) Create a virtual environment**
   ```bash
   python -m venv venv

   # Windows
   venv\Scripts\activate

   # macOS / Linux
   source venv/bin/activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```
   > This project uses only the Python standard library. The `requirements.txt` file documents compatibility; no packages need to be installed.

---

## Database Schema

The SQLite database file is stored at `database/library.db` and is created automatically when you run the application.

### `books`
| Column            | Type    | Description                    |
|-------------------|---------|--------------------------------|
| `id`              | INTEGER | Primary key (auto-increment)   |
| `title`           | TEXT    | Book title (required)          |
| `author`          | TEXT    | Author name (required)         |
| `publication_year`| INTEGER | Year of publication            |
| `quantity`        | INTEGER | Available copies (≥ 0)         |

### `members`
| Column      | Type    | Description                  |
|-------------|---------|------------------------------|
| `id`        | INTEGER | Primary key (auto-increment) |
| `full_name` | TEXT    | Member's full name           |
| `email`     | TEXT    | Unique email address         |
| `phone`     | TEXT    | Contact phone number         |

### `borrowing_records`
| Column        | Type    | Description                          |
|---------------|---------|--------------------------------------|
| `id`          | INTEGER | Primary key (auto-increment)         |
| `book_id`     | INTEGER | Foreign key → `books.id`             |
| `member_id`   | INTEGER | Foreign key → `members.id`           |
| `borrow_date` | TEXT    | ISO date when book was borrowed      |
| `return_date` | TEXT    | ISO date when book was returned      |
| `status`      | TEXT    | `borrowed` or `returned`             |

Entity relationships:

```
members ──< borrowing_records >── books
```

---

## Project Structure

```
library-management-system/
│
├── main.py              # CLI entry point and menu system
├── database.py          # Database connection and initialization
├── models.py            # Book, Member, BorrowingRecord models
├── services.py          # CRUD and business logic services
├── schema.sql           # SQL table definitions
├── requirements.txt     # Dependencies (standard library only)
├── README.md            # Project documentation
├── tests/
│   └── test_library.py  # Unit tests (15+ test cases)
│
└── database/
    └── library.db       # SQLite database (auto-created)
```

---

## How to Run the Application

From the project root directory:

```bash
python main.py
```

Use the numbered menu to navigate:

| Option | Action                  |
|--------|-------------------------|
| 1–5    | Book management         |
| 6–9    | Member management       |
| 10–12  | Borrowing operations    |
| 0      | Exit                    |

---

## How to Run Tests

From the project root directory:

```bash
python -m unittest discover -s tests -v
```

Or run the test file directly:

```bash
python tests/test_library.py
```

### Test Coverage
Tests cover:
- Book CRUD (add, list, update, delete, search)
- Member CRUD (add, update, delete, duplicate email)
- Borrowing (borrow, return, unavailable book, view records)
- Input validation (email, year, empty search)

---

## Screenshots

> _Add screenshots of the CLI menu and sample operations here before submission._

| Screenshot | Description |
|------------|-------------|
| ![Main Menu](screenshots/main-menu.png) | Main application menu |
| ![View Books](screenshots/view-books.png) | Books listing |
| ![Borrow Book](screenshots/borrow-book.png) | Borrowing workflow |

---

## Author

University Project — Library Management System  
Python · SQLite · OOP · CLI

---

## License

This project is submitted for academic purposes. Feel free to use and modify for learning.
