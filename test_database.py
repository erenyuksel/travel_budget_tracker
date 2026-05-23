from datetime import date

import pytest
from sqlalchemy import create_engine, inspect
from sqlalchemy.orm import sessionmaker

from db import Base
from models import Budget, CategoryAllocation, Expense


@pytest.fixture
def test_db_session():
    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False}
    )

    Base.metadata.create_all(bind=engine)

    TestingSessionLocal = sessionmaker(
        autocommit=False,
        autoflush=False,
        bind=engine
    )

    session = TestingSessionLocal()

    try:
        yield session, engine
    finally:
        session.close()
        Base.metadata.drop_all(bind=engine)


def test_tc_007_create_database_tables_successfully(test_db_session):
    session, engine = test_db_session

    inspector = inspect(engine)
    tables = inspector.get_table_names()

    assert "budgets" in tables
    assert "category_allocations" in tables
    assert "expenses" in tables


def test_tc_008_save_budget_with_predefined_categories(test_db_session):
    session, engine = test_db_session

    budget = Budget(
        trip_name="Sample Trip",
        total_budget=1000,
        currency="CHF"
    )

    budget.categories = [
        CategoryAllocation(name="Transport", percentage=25, allocated_amount=250),
        CategoryAllocation(name="Food", percentage=25, allocated_amount=250),
        CategoryAllocation(name="Accommodation", percentage=35, allocated_amount=350),
        CategoryAllocation(name="Leisure", percentage=15, allocated_amount=150),
    ]

    session.add(budget)
    session.commit()

    saved_budget = session.query(Budget).filter_by(
        trip_name="Sample Trip"
    ).first()

    assert saved_budget is not None
    assert saved_budget.total_budget == 1000
    assert saved_budget.currency == "CHF"
    assert len(saved_budget.categories) == 4

    categories = {
        category.name: category
        for category in saved_budget.categories
    }

    assert categories["Transport"].percentage == 25
    assert categories["Transport"].allocated_amount == 250

    assert categories["Food"].percentage == 25
    assert categories["Food"].allocated_amount == 250

    assert categories["Accommodation"].percentage == 35
    assert categories["Accommodation"].allocated_amount == 350

    assert categories["Leisure"].percentage == 15
    assert categories["Leisure"].allocated_amount == 150


def test_tc_009_save_and_retrieve_expense(test_db_session):
    session, engine = test_db_session

    budget = Budget(
        trip_name="Sample Trip",
        total_budget=1000,
        currency="CHF"
    )

    food_category = CategoryAllocation(
        name="Food",
        percentage=25,
        allocated_amount=250
    )

    budget.categories.append(food_category)

    session.add(budget)
    session.commit()

    expense = Expense(
        budget_id=budget.id,
        category_id=food_category.id,
        amount=35,
        description="Dinner",
        expense_date=date.today()
    )

    session.add(expense)
    session.commit()

    saved_expense = session.query(Expense).filter_by(
        description="Dinner"
    ).first()

    assert saved_expense is not None
    assert saved_expense.budget_id == budget.id
    assert saved_expense.category_id == food_category.id
    assert saved_expense.amount == 35
    assert saved_expense.description == "Dinner"
    assert saved_expense.expense_date == date.today()