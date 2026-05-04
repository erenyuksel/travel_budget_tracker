# user-interface.py

from datetime import date
from nicegui import ui

from db import engine, SessionLocal
from services import (
    create_tables,
    create_budget,
    list_budgets,
    get_dashboard_data,
    get_category_details,
    add_expense,
)

create_tables(engine)

session = SessionLocal()
current_budget_id = None


def clear_page():
    ui.query("body").classes("bg-gray-100")


def show_home():
    content.clear()
    with content:
        ui.label("Travel Budget Tracker").classes("text-3xl font-bold mb-4")

        ui.button("Setup Budget", on_click=show_budget_setup).classes("mb-2")
        ui.button("Dashboard", on_click=show_dashboard).classes("mb-2")
        ui.button("Add Expense", on_click=show_add_expense).classes("mb-2")


def show_budget_setup():
    content.clear()

    with content:
        ui.label("Setup Budget").classes("text-2xl font-bold mb-4")

        trip_name = ui.input("Trip name", value="Istanbul Vacation")
        total_budget = ui.number("Total budget", value=1200)
        currency = ui.input("Currency", value="CHF")

        ui.label("Category percentages").classes("text-lg font-bold mt-4")

        transport = ui.number("Transport %", value=20)
        food = ui.number("Food %", value=25)
        accommodation = ui.number("Accommodation %", value=40)
        leisure = ui.number("Leisure / Activities %", value=15)

        def save_budget():
            global current_budget_id

            categories = [
                {"name": "Transport", "percentage": transport.value},
                {"name": "Food", "percentage": food.value},
                {"name": "Accommodation", "percentage": accommodation.value},
                {"name": "Leisure / Activities", "percentage": leisure.value},
            ]

            try:
                budget = create_budget(
                    session=session,
                    trip_name=trip_name.value,
                    total_budget=float(total_budget.value),
                    currency=currency.value,
                    categories=categories,
                )
                current_budget_id = budget.id
                ui.notify("Budget created successfully", type="positive")
                show_dashboard()
            except Exception as e:
                ui.notify(str(e), type="negative")

        ui.button("Create Budget", on_click=save_budget).classes("mt-4")
        ui.button("Back", on_click=show_home).classes("mt-2")


def get_selected_budget_id():
    global current_budget_id

    if current_budget_id is not None:
        return current_budget_id

    budgets = list_budgets(session)
    if not budgets:
        return None

    current_budget_id = budgets[0].id
    return current_budget_id


def show_dashboard():
    content.clear()

    budget_id = get_selected_budget_id()

    with content:
        ui.label("Dashboard").classes("text-2xl font-bold mb-4")

        if budget_id is None:
            ui.label("No budget found. Please create a budget first.")
            ui.button("Setup Budget", on_click=show_budget_setup)
            return

        try:
            data = get_dashboard_data(session, budget_id)
        except Exception as e:
            ui.notify(str(e), type="negative")
            return

        summary = data["summary"]

        ui.label(data["trip_name"]).classes("text-xl font-semibold")
        ui.label(f"Currency: {data['currency']}")

        with ui.row().classes("gap-4 my-4"):
            with ui.card():
                ui.label("Total Budget")
                ui.label(f"{summary['total_budget']} {data['currency']}").classes("text-xl font-bold")

            with ui.card():
                ui.label("Total Spent")
                ui.label(f"{summary['total_spent']} {data['currency']}").classes("text-xl font-bold")

            with ui.card():
                ui.label("Remaining")
                ui.label(f"{summary['remaining_budget']} {data['currency']}").classes("text-xl font-bold")

        ui.label("Categories").classes("text-xl font-bold mt-4")

        for category in data["categories"]:
            over_budget = category["remaining_amount"] < 0
            color_class = "text-red-600" if over_budget else "text-green-600"

            with ui.card().classes("w-full my-2"):
                ui.label(category["name"]).classes("text-lg font-bold")
                ui.label(f"Limit: {category['allocated_amount']} {data['currency']}")
                ui.label(f"Spent: {category['spent_amount']} {data['currency']}")
                ui.label(f"Remaining: {category['remaining_amount']} {data['currency']}").classes(color_class)

                ui.button(
                    "Details",
                    on_click=lambda c_id=category["id"]: show_category_details(c_id),
                )

        ui.button("Add Expense", on_click=show_add_expense).classes("mt-4")
        ui.button("Back", on_click=show_home).classes("mt-2")


def show_add_expense():
    content.clear()

    budget_id = get_selected_budget_id()

    with content:
        ui.label("Add Expense").classes("text-2xl font-bold mb-4")

        if budget_id is None:
            ui.label("No budget found. Please create a budget first.")
            ui.button("Setup Budget", on_click=show_budget_setup)
            return

        data = get_dashboard_data(session, budget_id)
        categories = {c["name"]: c["id"] for c in data["categories"]}

        amount = ui.number("Amount", value=0)
        category_select = ui.select(list(categories.keys()), label="Category")
        description = ui.input("Description")
        expense_date = ui.input("Date YYYY-MM-DD", value=str(date.today()))

        def save_expense():
            try:
                selected_category_id = categories[category_select.value]

                add_expense(
                    session=session,
                    budget_id=budget_id,
                    category_id=selected_category_id,
                    amount=float(amount.value),
                    expense_date=date.fromisoformat(expense_date.value),
                    description=description.value,
                )

                ui.notify("Expense added successfully", type="positive")
                show_dashboard()

            except Exception as e:
                ui.notify(str(e), type="negative")

        ui.button("Save Expense", on_click=save_expense).classes("mt-4")
        ui.button("Back", on_click=show_dashboard).classes("mt-2")


def show_category_details(category_id):
    content.clear()

    budget_id = get_selected_budget_id()

    with content:
        ui.label("Category Details").classes("text-2xl font-bold mb-4")

        try:
            data = get_category_details(session, budget_id, category_id)
        except Exception as e:
            ui.notify(str(e), type="negative")
            return

        category = data["category"]

        ui.label(category["name"]).classes("text-xl font-bold")
        ui.label(f"Budget limit: {category['allocated_amount']}")
        ui.label(f"Spent: {category['spent_amount']}")
        ui.label(f"Remaining: {category['remaining_amount']}")

        ui.label("Expenses").classes("text-xl font-bold mt-4")

        if not data["expenses"]:
            ui.label("No expenses yet.")
        else:
            for expense in data["expenses"]:
                with ui.card().classes("w-full my-2"):
                    ui.label(f"{expense['amount']}")
                    ui.label(expense["description"] or "No description")
                    ui.label(str(expense["expense_date"]))

        ui.button("Back to Dashboard", on_click=show_dashboard).classes("mt-4")


ui.query("body").classes("bg-gray-100")

with ui.column().classes("w-full max-w-4xl mx-auto p-6") as content:
    pass

show_home()

ui.run()

