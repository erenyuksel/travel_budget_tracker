from nicegui import ui

import app_context
from services import get_category_details, get_dashboard_data
from ui_helpers import (
    clear_content,
    empty_state,
    money,
    notify_error,
    page_title,
    percentage_text,
    safe_ratio,
    summary_card,
)


# -----------------------------
# Category Details
# Person 2 responsibility
# -----------------------------

def get_category_by_id(budget_id, category_id):
    data = get_dashboard_data(app_context.session, budget_id)

    for category in data["categories"]:
        if category["id"] == category_id:
            return data, category

    raise ValueError("Category not found.")


def show_category_details(budget_id, category_id):
    from pages.dashboard_page import show_dashboard
    from pages.expense_pages import (
        show_add_expense_dialog,
        show_edit_expense,
        confirm_delete_expense,
    )

    clear_content()

    try:
        data = get_category_details(app_context.session, budget_id, category_id)
        dashboard = get_dashboard_data(app_context.session, budget_id)
    except Exception as error:
        notify_error(error)
        show_dashboard(budget_id)
        return

    category = data["category"]
    currency = dashboard["currency"]

    with app_context.content:
        with ui.row().classes("w-full justify-between items-start"):
            page_title(
                category["name"],
                "Category details and related expenses.",
            )

            with ui.row().classes("gap-2"):
                ui.button(
                    "Back to Dashboard",
                    icon="arrow_back",
                    on_click=lambda: show_dashboard(budget_id),
                ).props("outline")

                ui.button(
                    "Add Expense Here",
                    icon="add",
                    on_click=lambda: show_add_expense_dialog(
                        budget_id=budget_id,
                        category_id=category_id,
                        return_category_id=category_id,
                    ),
                ).classes("bg-blue-600 text-white rounded-lg")

        with ui.row().classes("w-full gap-4 mt-6"):
            summary_card(
                "Allocated",
                money(category["allocated_amount"], currency),
                "account_balance_wallet",
                "text-blue-500",
            )
            summary_card(
                "Spent",
                money(category["spent_amount"], currency),
                "payments",
                "text-orange-500",
            )
            summary_card(
                "Remaining",
                money(category["remaining_amount"], currency),
                "savings",
                "text-green-500",
            )

        category_progress = safe_ratio(
            category["spent_amount"],
            category["allocated_amount"],
        )

        with ui.card().classes("w-full rounded-2xl shadow-sm p-5 mt-6 bg-white"):
            ui.label("Category spending progress").classes("text-lg font-bold")
            ui.linear_progress(
                value=category_progress,
                show_value=False,
            ).classes("mt-3")
            ui.label(percentage_text(category_progress)).classes(
                "text-sm text-slate-500 mt-2"
            )

        ui.label("Expenses").classes("text-2xl font-bold mt-8")

        expenses = data["expenses"]

        if not expenses:
            empty_state(
                icon="receipt_long",
                title="No expenses in this category",
                subtitle="Add an expense directly to this category when you need it.",
                button_label="Add Expense Here",
                on_click=lambda: show_add_expense_dialog(
                    budget_id=budget_id,
                    category_id=category_id,
                    return_category_id=category_id,
                ),
            )
            return

        for expense in expenses:
            with ui.card().classes(
                "w-full rounded-2xl shadow-sm border border-slate-100 p-4 mt-3 bg-white"
            ):
                with ui.row().classes("w-full justify-between items-center"):
                    with ui.column().classes("gap-1"):
                        ui.label(money(expense["amount"], currency)).classes(
                            "text-xl font-bold text-slate-800"
                        )
                        ui.label(expense["description"] or "No description").classes(
                            "text-slate-500"
                        )
                        ui.label(str(expense["expense_date"])).classes(
                            "text-xs text-slate-400"
                        )

                    with ui.row().classes("gap-2"):
                        ui.button(
                            "Edit",
                            icon="edit",
                            on_click=lambda e_id=expense["id"]: show_edit_expense(
                                e_id,
                                back_budget_id=budget_id,
                                back_category_id=category_id,
                            ),
                        ).props("outline")

                        ui.button(
                            "Delete",
                            icon="delete",
                            on_click=lambda e_id=expense["id"]: confirm_delete_expense(
                                e_id,
                                budget_id,
                                category_id,
                            ),
                        ).classes("bg-red-600 text-white rounded-lg")
