import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from db import Base
from services import (
    validate_category_distribution,
    create_budget,
    add_expense,
    get_dashboard_data
)
from models import CategoryAllocation


# -------------------------
# Test DB setup
# -------------------------
@pytest.fixture
def session():
    engine = create_engine("sqlite:///:memory:")
    TestingSessionLocal = sessionmaker(bind=engine)

    Base.metadata.create_all(bind=engine)
    
    db = TestingSessionLocal()
    yield db
    db.close()


# Default valid categories
VALID_CATEGORIES = [
    {"name": "Transport", "percentage": 25},
    {"name": "Food", "percentage": 25},
    {"name": "Accommodation", "percentage": 35},
    {"name": "Leisure / Activities", "percentage": 15},
]


# ======================================================
# TC_001
# Validate category percentages add up to exactly 100
# ======================================================
def test_validate_category_distribution_valid():
    validate_category_distribution(VALID_CATEGORIES)


# ======================================================
# TC_002
# Reject percentages not adding to 100
# ======================================================
def test_validate_category_distribution_invalid_sum():
    invalid_categories = [
        {"name": "Transport", "percentage": 20},
        {"name": "Food", "percentage": 20},
        {"name": "Accommodation", "percentage": 30},
        {"name": "Leisure / Activities", "percentage": 10},
    ]

    with pytest.raises(
        ValueError,
        match="Category percentages must add up to exactly 100."
    ):
        validate_category_distribution(invalid_categories)


# ======================================================
# TC_003
# Reject empty category list
# ======================================================
def test_validate_category_distribution_empty():
    with pytest.raises(
        ValueError,
        match="At least one category is required."
    ):
        validate_category_distribution([])


# ======================================================
# TC_004
# Reject total budget <= 0
# ======================================================
def test_create_budget_invalid_total(session):
    with pytest.raises(
        ValueError,
        match="Total budget must be greater than 0."
    ):
        create_budget(
            session=session,
            trip_name="Test Trip",
            total_budget=0,
            currency="CHF",
            categories=VALID_CATEGORIES
        )


# ======================================================
# TC_005
# Reject expense amount <= 0
# ======================================================
def test_add_expense_invalid_amount(session):
    budget = create_budget(
        session=session,
        trip_name="Test Trip",
        total_budget=1000,
        currency="CHF",
        categories=VALID_CATEGORIES
    )

    category = session.query(CategoryAllocation).filter_by(
        budget_id=budget.id
    ).first()

    with pytest.raises(
        ValueError,
        match="Expense amount must be greater than 0."
    ):
        add_expense(
            session=session,
            budget_id=budget.id,
            category_id=category.id,
            amount=0,
            expense_date="2026-05-23"
        )


# ======================================================
# TC_006
# Calculate spent and remaining correctly
# ======================================================
def test_dashboard_calculation(session):
    budget = create_budget(
        session=session,
        trip_name="Test Trip",
        total_budget=1000,
        currency="CHF",
        categories=VALID_CATEGORIES
    )

    category = session.query(CategoryAllocation).filter_by(
        budget_id=budget.id
    ).first()

    add_expense(
        session=session,
        budget_id=budget.id,
        category_id=category.id,
        amount=200,
        expense_date="2026-05-23"
    )

    dashboard = get_dashboard_data(session, budget.id)

    assert dashboard["summary"]["total_spent"] == 200
    assert dashboard["summary"]["remaining_budget"] == 800