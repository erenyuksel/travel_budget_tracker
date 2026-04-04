from datetime import date

from db import SessionLocal, engine
from models import CategoryAllocation
from services import create_tables, create_budget, add_expense, get_dashboard_data, get_category_details


def main():
    create_tables(engine)
    session = SessionLocal()

    try:
        budget = create_budget(
            session=session,
            trip_name="Istanbul Vacation",
            total_budget=1200,
            currency="CHF",
            categories=[
                {"name": "Transport", "percentage": 20},
                {"name": "Food", "percentage": 25},
                {"name": "Accommodation", "percentage": 40},
                {"name": "Leisure / Activities", "percentage": 15},
            ],
        )

        food_category = (
            session.query(CategoryAllocation)
            .filter(CategoryAllocation.budget_id == budget.id)
            .filter(CategoryAllocation.name == "Food")
            .first()
        )

        add_expense(
            session=session,
            budget_id=budget.id,
            category_id=food_category.id,
            amount=45.50,
            expense_date=date.today(),
            description="Dinner",
        )

        print("DASHBOARD")
        print(get_dashboard_data(session, budget.id))

        print("\nFOOD CATEGORY DETAILS")
        print(get_category_details(session, budget.id, food_category.id))

    finally:
        session.close()


if __name__ == "__main__":
    main()
