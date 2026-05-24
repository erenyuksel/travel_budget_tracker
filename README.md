# ✈️ Trip Tracker

A web-based application for planning and tracking travel budgets. Trip Tracker lets users create vacation budgets, distribute spending across categories, and log expenses from a clean browser interface.

This project is intended to:

- Practice the complete software development process from analysis to implementation
- Apply Python programming concepts learned in the module
- Demonstrate interactive user interfaces, data validation, and database processing
- Produce clean, modular, and documented code
- Strengthen practical experience in building structured applications

---

## 📝 Analysis

### Problem

Travelers often struggle to stay within their budget when managing multiple spending categories such as transport, accommodation, food, and activities. Keeping track manually can lead to overspending and poor visibility into where money is going.

### Scenario

Trip Tracker solves this problem by giving users one central place to set a total trip budget, split it across categories by percentage, and log every expense. The app automatically calculates how much has been spent and how much remains, both overall and per category.

### User Stories

- As a user, I want to create a vacation budget with a name, total amount, and currency.
- As a user, I want to allocate my budget across spending categories, such as food, accommodation, transport, and activities.
- As a user, I want to log individual expenses and assign them to a category.
- As a user, I want to see a dashboard showing how much I have spent and what is left.
- As a user, I want to edit or delete budgets and expenses.
- As a user, I want to filter expenses to find specific entries more easily.

### Use Cases

| Use Case | Description |
|---|---|
| Create Vacation | Set trip name, total budget, and currency. |
| Allocate Categories | Define categories and assign percentages that must add up to 100%. |
| Log Expense | Add an expense with amount, category, date, and optional description. |
| View Dashboard | See overall spending progress and a breakdown per category. |
| Filter Expenses | Search and filter expenses by description, date range, and amount. |
| Edit / Delete | Update or remove budgets and expenses. |

---

## ✅ Project Requirements

### 1. Interactive App

The application runs as a web UI built with **NiceGUI**. Users interact through a browser interface to create vacation budgets, add categories, log expenses, and view dashboards without writing code or using a terminal.

### 2. Data Validation

All user input is validated before being saved. Important validations are implemented mainly in `services.py`.

#### Budget amount

```python
if total_budget <= 0:
    raise ValueError("Total budget must be greater than 0.")
```

#### Category percentages must sum to exactly 100

```python
if total_percentage != 100:
    raise ValueError("Category percentages must add up to exactly 100.")
```

#### Expense amount

```python
if amount <= 0:
    raise ValueError("Expense amount must be greater than 0.")
```

The database model also protects the data with a SQLAlchemy constraint:

```python
CheckConstraint("amount > 0", name="check_amount_positive")
```

#### Currency

```python
ALLOWED_CURRENCIES = ["CHF", "EUR", "USD", "GBP", "TRY"]

if currency not in ALLOWED_CURRENCIES:
    raise ValueError(f"Currency must be one of: {', '.join(ALLOWED_CURRENCIES)}.")
```

#### Date format

```python
return date.fromisoformat(str(value))
```

The expected date format is:

```text
YYYY-MM-DD
```

### 3. File / Database Processing

The application uses **SQLite** as its persistent data store through **SQLAlchemy ORM**.

| File | Purpose |
|---|---|
| `travel_budget.db` | SQLite database file created locally when the app runs. |
| `schema.sql` | Raw SQL schema reference for the database structure. |
| `models.py` | SQLAlchemy ORM model classes mapped to database tables. |
| `services.py` | Business logic and database operations. |

Data is read and written through service functions in `services.py`, keeping database logic separated from the UI layer.

---

## ⚙️ Implementation

### Technology Stack

| Tool | Purpose |
|---|---|
| Python 3.x | Core programming language |
| NiceGUI | Web UI framework |
| SQLAlchemy | ORM and database layer |
| SQLite | Persistent local database |
| Pydantic | Optional input validation schemas |
| pytest | Unit and database testing |

---

## 📂 Repository Structure

```text
travel_budget_tracker/
├── app.py                    # App entry point — starts the NiceGUI server
├── app_context.py            # Shared app state, session, and layout reference
├── db.py                     # Database connection and session setup
├── init_db.py                # Creates the database and inserts sample data
├── models.py                 # SQLAlchemy ORM table definitions
├── schemas.py                # Pydantic validation schemas
├── services.py               # Database logic and business rules
├── schema.sql                # Raw SQL schema for reference
├── ui_helpers.py             # Reusable UI components and formatting utilities
├── ui_layout.py              # App header and layout wrappers
├── requirements.txt          # Python dependencies
├── test_unit.py              # Unit tests for validation and service logic
├── test_database.py          # Database and integration-style tests
└── pages/
    ├── __init__.py           # Marks pages as a Python package
    ├── home_page.py          # Vacation overview — lists all budgets
    ├── dashboard_page.py     # Per-budget spending summary
    ├── budget_pages.py       # Create / edit / delete budget forms
    ├── category_pages.py     # Category breakdown, details, and expense filters
    └── expense_pages.py      # Add / edit / delete expense forms
```

The `pages/__init__.py` file makes the `pages` folder importable as a Python package.

---

## 🧩 Main Components

### `app.py`

Starts the NiceGUI application and loads the first page.

### `app_context.py`

Stores shared application objects such as:

- App title
- Database session
- Main UI content container

### `db.py`

Sets up the SQLite database connection, SQLAlchemy engine, session factory, and base model class.

### `models.py`

Defines the database models:

- `Budget`
- `CategoryAllocation`
- `Expense`

### `services.py`

Contains the main business logic and database operations, including:

- Budget creation, update, and deletion
- Category validation
- Expense creation, update, and deletion
- Dashboard calculations
- Category details
- Expense filtering

### `pages/`

Contains the separated NiceGUI UI pages. This modular structure improves readability and reduces Git conflicts during teamwork.

---

## 🗃️ Database Design

The project uses three main database tables.

### 1. `budgets`

Stores the main trip budget.

| Field | Description |
|---|---|
| `id` | Unique budget ID |
| `trip_name` | Name of the vacation/trip |
| `total_budget` | Total available budget |
| `currency` | Currency code such as CHF, EUR, USD |
| `created_at` | Vacation creation/date field |

### 2. `category_allocations`

Stores the budget categories.

| Field | Description |
|---|---|
| `id` | Unique category ID |
| `budget_id` | Linked budget ID |
| `name` | Category name |
| `percentage` | Percentage of total budget |
| `allocated_amount` | Calculated amount for the category |

Each category belongs to one budget.

### 3. `expenses`

Stores all expenses.

| Field | Description |
|---|---|
| `id` | Unique expense ID |
| `budget_id` | Linked budget ID |
| `category_id` | Linked category ID |
| `amount` | Expense amount |
| `description` | Optional expense description |
| `expense_date` | Date of the expense |

Each expense belongs to one budget and one category.

---

## 🚀 How to Run

### 1. Clone the repository

```bash
git clone https://github.com/erenyuksel/travel_budget_tracker.git
cd travel_budget_tracker
```

### 2. Create a virtual environment

#### Windows

```bash
python -m venv .venv
.venv\Scripts\activate
```

#### macOS / Linux

```bash
python3 -m venv .venv
source .venv/bin/activate
```

#### Fish shell on Linux

```bash
python -m venv .venv
source .venv/bin/activate.fish
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

If `pip` does not work, use:

```bash
python -m pip install -r requirements.txt
```

or on macOS/Linux:

```bash
python3 -m pip install -r requirements.txt
```

### 4. Start the application

```bash
python app.py
```

or on macOS/Linux:

```bash
python3 app.py
```

### 5. Open the app in the browser

Usually the app runs at:

```text
http://localhost:8080
```

---

## 🧪 Running the Tests

Run all tests:

```bash
python -m pytest -v
```

Run only unit tests:

```bash
python -m pytest test_unit.py -v
```

Run only database tests:

```bash
python -m pytest test_database.py -v
```

---

## ✅ Test Coverage

### Unit / Service Tests

These tests check:

- Category percentage validation
- Invalid budget amounts
- Invalid expense amounts
- Dashboard calculations
- Total spent calculation
- Remaining budget calculation

### Database / Integration Tests

These tests check:

- Database table creation
- Saving budgets
- Saving predefined categories
- Saving and retrieving expenses
- SQLAlchemy model relationships

---

## 📚 Libraries Used

### NiceGUI

Used to create the browser-based graphical user interface.

### SQLAlchemy

Used for database models, relationships, queries, and database operations.

### SQLite

Used as the local persistent database.

### Pydantic

Used for optional data validation schemas.

### pytest

Used for automated unit and database tests.

---

## 👥 Team & Contributions

### Eren Yüksel

- Database
- Backend

### Shaymaa Zaiter

- Frontend: Core app setup and structure
- UI layout and helpers
- Home and budget pages
- Unit tests
- README file

### Sarah Kühne

- Frontend: Dashboard page, category pages, and expense pages
- Database and integration tests
- PowerPoint presentation

---

## 📌 Current Status

Implemented features:

- SQLite database setup
- SQLAlchemy models
- Service/business logic layer
- NiceGUI user interface
- Modular page-based UI structure
- Budget creation
- Budget editing
- Budget deletion
- Editable vacation date
- Category dashboard
- Category details
- Expense creation
- Expense descriptions
- Editable expense date
- Expense editing
- Expense deletion
- Expense filtering
- Unit tests
- Database tests

---

## 🔮 Future Improvements

Possible future improvements:

- User authentication
- Add Categories
- Multiple users
- Export expenses to CSV
- Charts for spending analytics
- Better mobile responsiveness
- Date picker instead of manual date input
- Deployment to a public server

---

## 📝 License

This project is provided for educational use only as part of the Advanced Programming module at FHNW.

MIT License
