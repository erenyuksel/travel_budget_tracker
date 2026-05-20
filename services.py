from datetime import date
from sqlalchemy import func

from models import Budget, CategoryAllocation, Expense


DEFAULT_CATEGORIES = [
    "Transport",
    "Food",
    "Accommodation",
    "Leisure / Activities",
]

ALLOWED_CURRENCIES = ["CHF", "EUR", "USD", "GBP", "TRY"]


def create_tables(engine):
    from db import Base
    Base.metadata.create_all(bind=engine)


def _to_float(value, field_name):
    try:
        return float(value)
    except (TypeError, ValueError):
        raise ValueError(f"{field_name} must be a number.")


def _validate_currency(currency):
    currency = str(currency).strip().upper()

    if not currency:
        raise ValueError("Currency cannot be empty.")

    if currency not in ALLOWED_CURRENCIES:
        raise ValueError(
            f"Currency must be one of: {', '.join(ALLOWED_CURRENCIES)}."
        )

    return currency


def _normalize_date(value):
    if value is None:
        return None

    if isinstance(value, date):
        return value

    try:
        return date.fromisoformat(str(value))
    except (TypeError, ValueError):
        raise ValueError("Expense date must be a valid date in YYYY-MM-DD format.")


def validate_category_distribution(categories):
    if not categories:
        raise ValueError("At least one category is required.")

    total_percentage = 0.0
    category_names = []

    for item in categories:
        name = str(item.get("name", "")).strip()

        if not name:
            raise ValueError("Category name cannot be empty.")

        percentage = _to_float(item.get("percentage"), "Category percentage")

        if percentage < 0:
            raise ValueError("Category percentage cannot be negative.")

        total_percentage += percentage
        category_names.append(name.lower())

    total_percentage = round(total_percentage, 2)

    if total_percentage != 100:
        raise ValueError("Category percentages must add up to exactly 100.")

    if len(category_names) != len(set(category_names)):
        raise ValueError("Category names must be unique.")


def create_budget(session, trip_name, total_budget, currency, categories):
    trip_name = str(trip_name).strip()
    currency = _validate_currency(currency)
    total_budget = _to_float(total_budget, "Total budget")

    if not trip_name:
        raise ValueError("Trip name cannot be empty.")

    if total_budget <= 0:
        raise ValueError("Total budget must be greater than 0.")

    validate_category_distribution(categories)

    try:
        budget = Budget(
            trip_name=trip_name,
            total_budget=total_budget,
            currency=currency,
        )
        session.add(budget)
        session.flush()

        for item in categories:
            percentage = _to_float(item["percentage"], "Category percentage")
            allocated_amount = round(total_budget * (percentage / 100), 2)

            category = CategoryAllocation(
                budget_id=budget.id,
                name=item["name"].strip(),
                percentage=percentage,
                allocated_amount=allocated_amount,
            )
            session.add(category)

        session.commit()
        session.refresh(budget)
        return budget

    except Exception:
        session.rollback()
        raise


def get_budget(session, budget_id):
    return session.query(Budget).filter(Budget.id == budget_id).first()


def list_budgets(session):
    return session.query(Budget).order_by(Budget.created_at.desc()).all()


def get_expense(session, expense_id):
    return session.query(Expense).filter(Expense.id == expense_id).first()


def list_expenses_for_budget(session, budget_id):
    budget = get_budget(session, budget_id)

    if budget is None:
        raise ValueError("Budget not found.")

    categories = (
        session.query(CategoryAllocation)
        .filter(CategoryAllocation.budget_id == budget_id)
        .all()
    )

    category_names_by_id = {
        category.id: category.name
        for category in categories
    }

    expenses = (
        session.query(Expense)
        .filter(Expense.budget_id == budget_id)
        .order_by(Expense.expense_date.desc(), Expense.id.desc())
        .all()
    )

    expense_list = []

    for expense in expenses:
        expense_list.append(
            {
                "id": expense.id,
                "budget_id": expense.budget_id,
                "category_id": expense.category_id,
                "category_name": category_names_by_id.get(expense.category_id),
                "amount": round(expense.amount, 2),
                "description": expense.description,
                "expense_date": expense.expense_date,
            }
        )

    return expense_list


def search_expenses(
    session,
    budget_id,
    search_text=None,
    category_id=None,
    start_date=None,
    end_date=None,
    min_amount=None,
    max_amount=None,
):
    budget = get_budget(session, budget_id)

    if budget is None:
        raise ValueError("Budget not found.")

    query = session.query(Expense).filter(Expense.budget_id == budget_id)

    if search_text:
        query = query.filter(
            Expense.description.ilike(f"%{str(search_text).strip()}%")
        )

    if category_id is not None:
        category = (
            session.query(CategoryAllocation)
            .filter(CategoryAllocation.id == category_id)
            .first()
        )

        if category is None or category.budget_id != budget_id:
            raise ValueError("Category not found for this budget.")

        query = query.filter(Expense.category_id == category_id)

    if start_date is not None:
        start_date = _normalize_date(start_date)
        query = query.filter(Expense.expense_date >= start_date)

    if end_date is not None:
        end_date = _normalize_date(end_date)
        query = query.filter(Expense.expense_date <= end_date)

    if min_amount is not None:
        min_amount = _to_float(min_amount, "Minimum amount")
        query = query.filter(Expense.amount >= min_amount)

    if max_amount is not None:
        max_amount = _to_float(max_amount, "Maximum amount")
        query = query.filter(Expense.amount <= max_amount)

    expenses = (
        query
        .order_by(Expense.expense_date.desc(), Expense.id.desc())
        .all()
    )

    category_rows = (
        session.query(CategoryAllocation)
        .filter(CategoryAllocation.budget_id == budget_id)
        .all()
    )

    category_names_by_id = {
        category.id: category.name
        for category in category_rows
    }

    results = []

    for expense in expenses:
        results.append(
            {
                "id": expense.id,
                "budget_id": expense.budget_id,
                "category_id": expense.category_id,
                "category_name": category_names_by_id.get(expense.category_id),
                "amount": round(expense.amount, 2),
                "description": expense.description,
                "expense_date": expense.expense_date,
            }
        )

    return results


def update_budget(
    session,
    budget_id,
    trip_name=None,
    total_budget=None,
    currency=None,
    categories=None,
):
    budget = get_budget(session, budget_id)

    if budget is None:
        raise ValueError("Budget not found.")

    try:
        total_budget_was_changed = False

        if trip_name is not None:
            trip_name = str(trip_name).strip()

            if not trip_name:
                raise ValueError("Trip name cannot be empty.")

            budget.trip_name = trip_name

        if total_budget is not None:
            total_budget = _to_float(total_budget, "Total budget")

            if total_budget <= 0:
                raise ValueError("Total budget must be greater than 0.")

            budget.total_budget = total_budget
            total_budget_was_changed = True

        if currency is not None:
            budget.currency = _validate_currency(currency)

        existing_categories = (
            session.query(CategoryAllocation)
            .filter(CategoryAllocation.budget_id == budget_id)
            .order_by(CategoryAllocation.id)
            .all()
        )

        if categories is not None:
            validate_category_distribution(categories)

            existing_by_id = {
                category.id: category
                for category in existing_categories
            }

            received_ids = set()
            prepared_categories = []

            for item in categories:
                if "id" not in item:
                    raise ValueError("Category ID is required when updating categories.")

                try:
                    category_id = int(item["id"])
                except (TypeError, ValueError):
                    raise ValueError("Category ID must be a valid number.")

                if category_id in received_ids:
                    raise ValueError("Duplicate category ID received.")

                if category_id not in existing_by_id:
                    raise ValueError("Category not found for this budget.")

                received_ids.add(category_id)
                prepared_categories.append((category_id, item))

            existing_ids = set(existing_by_id.keys())

            if received_ids != existing_ids:
                raise ValueError(
                    "You must send all existing categories when updating percentages."
                )

            for category_id, item in prepared_categories:
                category = existing_by_id[category_id]
                percentage = _to_float(item["percentage"], "Category percentage")

                category.name = item["name"].strip()
                category.percentage = percentage
                category.allocated_amount = round(
                    budget.total_budget * (percentage / 100),
                    2,
                )

        elif total_budget_was_changed:
            for category in existing_categories:
                category.allocated_amount = round(
                    budget.total_budget * (category.percentage / 100),
                    2,
                )

        session.commit()
        session.refresh(budget)
        return budget

    except Exception:
        session.rollback()
        raise


def update_budget_categories(session, budget_id, categories):
    return update_budget(
        session=session,
        budget_id=budget_id,
        categories=categories,
    )


def delete_budget(session, budget_id):
    budget = get_budget(session, budget_id)

    if budget is None:
        return False

    try:
        session.query(Expense).filter(
            Expense.budget_id == budget_id
        ).delete(synchronize_session=False)

        session.query(CategoryAllocation).filter(
            CategoryAllocation.budget_id == budget_id
        ).delete(synchronize_session=False)

        session.delete(budget)
        session.commit()
        return True

    except Exception:
        session.rollback()
        raise


def add_expense(session, budget_id, category_id, amount, expense_date, description=None):
    amount = _to_float(amount, "Expense amount")
    expense_date = _normalize_date(expense_date)

    if amount <= 0:
        raise ValueError("Expense amount must be greater than 0.")

    budget = get_budget(session, budget_id)
    if budget is None:
        raise ValueError("Budget not found.")

    category = (
        session.query(CategoryAllocation)
        .filter(CategoryAllocation.id == category_id)
        .first()
    )
    if category is None or category.budget_id != budget_id:
        raise ValueError("Category not found for this budget.")

    try:
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

    except Exception:
        session.rollback()
        raise


def update_expense(session, expense_id, category_id=None, amount=None, expense_date=None, description=None):
    expense = get_expense(session, expense_id)

    if expense is None:
        raise ValueError("Expense not found.")

    try:
        if category_id is not None:
            category = (
                session.query(CategoryAllocation)
                .filter(CategoryAllocation.id == category_id)
                .first()
            )

            if category is None or category.budget_id != expense.budget_id:
                raise ValueError("New category does not belong to the same budget.")

            expense.category_id = category_id

        if amount is not None:
            amount = _to_float(amount, "Expense amount")

            if amount <= 0:
                raise ValueError("Expense amount must be greater than 0.")

            expense.amount = amount

        if expense_date is not None:
            expense.expense_date = _normalize_date(expense_date)

        if description is not None:
            expense.description = description

        session.commit()
        session.refresh(expense)
        return expense

    except Exception:
        session.rollback()
        raise


def delete_expense(session, expense_id):
    expense = get_expense(session, expense_id)

    if expense is None:
        return False

    try:
        session.delete(expense)
        session.commit()
        return True

    except Exception:
        session.rollback()
        raise


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
    )