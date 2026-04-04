# Travel Budget Tracker 

It follows the project document:
- one travel budget
- category percentage allocation
- expense tracking
- dashboard totals
- category details

## Stack
- Python
- SQLite
- SQLAlchemy ORM
- Pydantic (optional)

## Files
- `db.py` -> database connection and session
- `models.py` -> tables
- `services.py` -> database logic
- `schemas.py` -> optional validation models
- `schema.sql` -> raw SQL schema
- `example_usage.py` -> example test script
- `init_db.py` -> create DB and sample data

## Main tables
1. `budgets`
2. `category_allocations`
3. `expenses`

## What the user enters
- total travel budget
- percentage for each category
- expense amount
- expense category
- optional description
- date

## What the system calculates
- allocated amount for each category
- total spent
- remaining budget
- category spent and remaining amount

## Main rules
- total budget must be greater than 0
- expense amount must be greater than 0
- category percentages must add up to 100
- each expense belongs to one budget and one category

## Install
```bash
pip install -r requirements.txt
```

## Run example
```bash
python example_usage.py
```

## Note for backend teammate
The backend teammate (Sara) should call the functions in `services.py`.
That is easier and cleaner than writing raw SQL in every route.

Useful functions:
- `create_budget(...)`
- `add_expense(...)`
- `update_expense(...)`
- `delete_expense(...)`
- `get_dashboard_data(...)`
- `get_category_details(...)`
