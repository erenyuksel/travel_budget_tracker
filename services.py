from datetime import date
from sqlalchemy import func

from models import Budget, CategoryAllocation, Expense


DEFAULT_CATEGORIES = [
    "Transport",
    "Food",
    "Accommodation",
    "Leisure / Activities",
]


def create_tables(engine):
    from db import Base
    Base.metadata.create_all(bind=engine)


def validate_category_distribution(categories):
    if not categories:
        raise ValueError("At least one category is required.")

    total_percentage = 0
    category_names = []

    for item in categories:
        total_percentage += float(item["percentage"])
        category_names.append(item["name"].strip())

    total_percentage = round(total_percentage, 2)

    if total_percentage != 100:
        raise ValueError("Category percentages must add up to exactly 100.")

    if len(category_names) != len(set(category_names)):
        raise ValueError("Category names must be unique.")


def create_budget(session, trip_name, total_budget, currency, categories):
    if total_budget <= 0:
        raise ValueError("Total budget must be greater than 0.")

    validate_category_distribution(categories)

    budget = Budget(
        trip_name=trip_name,
        total_budget=total_budget,
        currency=currency,
    )
    session.add(budget)
    session.commit()
    session.refresh(budget)

    for item in categories:
        percentage = float(item["percentage"])
        allocated_amount = round(total_budget * (percentage / 100), 2)

        category = CategoryAllocation(
            budget_id=budget.id,
            name=item["name"].strip(),
            percentage=percentage,
            allocated_amount=allocated_amount,
        )
        session.add(category)

    session.commit()
    return budget


def get_budget(session, budget_id):
    return session.query(Budget).filter(Budget.id == budget_id).first()


def list_budgets(session):
    return session.query(Budget).order_by(Budget.created_at.desc()).all()


def add_expense(session, budget_id, category_id, amount, expense_date, description=None):
    if amount <= 0:
        raise ValueError("Expense amount must be greater than 0.")

    budget = get_budget(session, budget_id)
    if budget is None:
        raise ValueError("Budget not found.")

    category = session.query(CategoryAllocation).filter(CategoryAllocation.id == category_id).first()
    if category is None or category.budget_id != budget_id:
        raise ValueError("Category not found for this budget.")

    expense = Expense(
        budget_id=budget_id,
        category_id=category_id,
        amount=amount,
        description=description,
        expense_date=expense_date,
    )
    session.add(expense)
    session.commit()
    session.refresh(expense)
    return expense


def update_expense(session, expense_id, category_id=None, amount=None, expense_date=None, description=None):
    expense = session.query(Expense).filter(Expense.id == expense_id).first()

    if expense is None:
        raise ValueError("Expense not found.")

    if category_id is not None:
        category = session.query(CategoryAllocation).filter(CategoryAllocation.id == category_id).first()
        if category is None or category.budget_id != expense.budget_id:
            raise ValueError("New category does not belong to the same budget.")
        expense.category_id = category_id

    if amount is not None:
        if amount <= 0:
            raise ValueError("Expense amount must be greater than 0.")
        expense.amount = amount

    if expense_date is not None:
        expense.expense_date = expense_date

    if description is not None:
        expense.description = description

    session.commit()
    session.refresh(expense)
    return expense


def delete_expense(session, expense_id):
    expense = session.query(Expense).filter(Expense.id == expense_id).first()

    if expense is None:
        return False

    session.delete(expense)
    session.commit()
    return True


def get_total_spent(session, budget_id):
    total = session.query(func.sum(Expense.amount)).filter(Expense.budget_id == budget_id).scalar()

    if total is None:
        total = 0

    return round(float(total), 2)


def get_category_spent(session, category_id):
    total = session.query(func.sum(Expense.amount)).filter(Expense.category_id == category_id).scalar()

    if total is None:
        total = 0

    return round(float(total), 2)


def get_dashboard_data(session, budget_id):
    budget = get_budget(session, budget_id)
    if budget is None:
        raise ValueError("Budget not found.")

    total_spent = get_total_spent(session, budget_id)

    category_rows = (
        session.query(CategoryAllocation)
        .filter(CategoryAllocation.budget_id == budget_id)
        .order_by(CategoryAllocation.id)
        .all()
    )

    categories_data = []

    for category in category_rows:
        spent = get_category_spent(session, category.id)

        category_info = {
            "id": category.id,
            "name": category.name,
            "percentage": category.percentage,
            "allocated_amount": round(category.allocated_amount, 2),
            "spent_amount": spent,
            "remaining_amount": round(category.allocated_amount - spent, 2),
        }
        categories_data.append(category_info)

    dashboard_data = {
        "budget_id": budget.id,
        "trip_name": budget.trip_name,
        "currency": budget.currency,
        "created_at": budget.created_at,
        "summary": {
            "total_budget": round(budget.total_budget, 2),
            "total_spent": total_spent,
            "remaining_budget": round(budget.total_budget - total_spent, 2),
        },
        "categories": categories_data,
    }

    return dashboard_data


def get_category_details(session, budget_id, category_id):
    category = session.query(CategoryAllocation).filter(CategoryAllocation.id == category_id).first()

    if category is None or category.budget_id != budget_id:
        raise ValueError("Category not found for this budget.")

    spent = get_category_spent(session, category.id)

    expenses = (
        session.query(Expense)
        .filter(Expense.category_id == category_id)
        .order_by(Expense.expense_date.desc(), Expense.id.desc())
        .all()
    )

    expense_list = []
    for expense in expenses:
        expense_data = {
            "id": expense.id,
            "amount": round(expense.amount, 2),
            "description": expense.description,
            "expense_date": expense.expense_date,
            "category_id": expense.category_id,
        }
        expense_list.append(expense_data)

    category_data = {
        "category": {
            "id": category.id,
            "name": category.name,
            "percentage": category.percentage,
            "allocated_amount": round(category.allocated_amount, 2),
            "spent_amount": spent,
            "remaining_amount": round(category.allocated_amount - spent, 2),
        },
        "expenses": expense_list,
    }

    return category_data


def seed_default_budget(session):
    categories = [
        {"name": "Transport", "percentage": 25},
        {"name": "Food", "percentage": 25},
        {"name": "Accommodation", "percentage": 35},
        {"name": "Leisure / Activities", "percentage": 15},
    ]

    return create_budget(
        session=session,
        trip_name="Sample Trip",
        total_budget=1000,
        currency="CHF",
        categories=categories,
