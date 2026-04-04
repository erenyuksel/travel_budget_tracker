CREATE TABLE budgets (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    trip_name TEXT NOT NULL,
    total_budget REAL NOT NULL CHECK (total_budget > 0),
    currency TEXT NOT NULL DEFAULT 'CHF',
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE category_allocations (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    budget_id INTEGER NOT NULL,
    name TEXT NOT NULL,
    percentage REAL NOT NULL CHECK (percentage >= 0 AND percentage <= 100),
    allocated_amount REAL NOT NULL,
    FOREIGN KEY (budget_id) REFERENCES budgets(id) ON DELETE CASCADE
);

CREATE TABLE expenses (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    budget_id INTEGER NOT NULL,
    category_id INTEGER NOT NULL,
    amount REAL NOT NULL CHECK (amount > 0),
    description TEXT,
    expense_date DATE NOT NULL,
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (budget_id) REFERENCES budgets(id) ON DELETE CASCADE,
    FOREIGN KEY (category_id) REFERENCES category_allocations(id) ON DELETE RESTRICT
);
