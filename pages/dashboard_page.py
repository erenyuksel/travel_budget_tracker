from nicegui import ui

import app_context
from services import get_dashboard_data
from ui_helpers import (
    clear_content,
    money,
    notify_error,
    page_title,
    percentage_text,
    safe_ratio,
    summary_card,
)


# -----------------------------
# Dashboard
# Shared page:
# - Person 1 owns the top summary section.
# - Person 2 owns the category cards section.
# -----------------------------

def show_dashboard(budget_id):
    from pages.home_page import show_home
    from pages.budget_pages import show_edit_budget
    from pages.category_pages import show_category_details
    from pages.expense_pages import show_add_expense_dialog

    clear_content()

    try:
        data = get_dashboard_data(app_context.session, budget_id)
    except Exception as error:
        notify_error(error)
        show_home()
        return

    summary = data["summary"]
    currency = data["currency"]

    with app_context.content:
        with ui.row().classes("w-full justify-between items-start"):
            page_title(
                data["trip_name"],
                "Overview of your travel budget and category progress.",
            )

            ui.button(
                "Edit Vacation",
                icon="edit",
                on_click=lambda: show_edit_budget(budget_id),
            ).props("outline")

        # Person 1 section: overall vacation summary
        with ui.row().classes("w-full gap-4 mt-6"):
            summary_card(
                "Total Budget",
                money(summary["total_budget"], currency),
                "account_balance_wallet",
                "text-blue-500",
            )
            summary_card(
                "Total Spent",
                money(summary["total_spent"], currency),
                "payments",
                "text-orange-500",
            )
            summary_card(
                "Remaining",
                money(summary["remaining_budget"], currency),
                "savings",
                "text-green-500",
            )

        progress = safe_ratio(summary["total_spent"], summary["total_budget"])

        with ui.card().classes("w-full rounded-2xl shadow-sm p-5 mt-6 bg-white"):
            ui.label("Overall spending progress").classes("text-lg font-bold")
            ui.linear_progress(value=progress, show_value=False).classes("mt-3")
            ui.label(percentage_text(progress)).classes("text-sm text-slate-500 mt-2")

        # Person 2 section: category cards
        ui.label("Categories").classes("text-2xl font-bold mt-8")

        with ui.grid(columns=2).classes("w-full gap-4 mt-3"):
            for category in data["categories"]:
                allocated = category["allocated_amount"]
                spent = category["spent_amount"]
                remaining = category["remaining_amount"]
                category_progress = safe_ratio(spent, allocated)

                with ui.card().classes(
                    "rounded-2xl shadow-sm border border-slate-100 p-5 bg-white"
                ):
                    with ui.row().classes("w-full justify-between items-start"):
                        with ui.column().classes("gap-1"):
                            ui.label(category["name"]).classes(
                                "text-xl font-bold text-slate-800"
                            )
                            ui.label(f"{category['percentage']}% of total budget").classes(
                                "text-sm text-slate-500"
                            )

                        if remaining < 0:
                            ui.badge("Overspent", color="red")
                        else:
                            ui.badge("On track", color="green")

                    ui.separator().classes("my-3")

                    with ui.row().classes("w-full gap-4"):
                        with ui.column().classes("gap-0 flex-1"):
                            ui.label("Allocated").classes("text-xs text-slate-400")
                            ui.label(money(allocated, currency)).classes("font-semibold")

                        with ui.column().classes("gap-0 flex-1"):
                            ui.label("Spent").classes("text-xs text-slate-400")
                            ui.label(money(spent, currency)).classes(
                                "font-semibold text-orange-600"
                            )

                        with ui.column().classes("gap-0 flex-1"):
                            ui.label("Remaining").classes("text-xs text-slate-400")
                            ui.label(money(remaining, currency)).classes(
                                "font-semibold text-green-600"
                                if remaining >= 0
                                else "font-semibold text-red-600"
                            )

                    ui.linear_progress(
                        value=category_progress,
                        show_value=False,
                    ).classes("mt-4")

                    ui.label(percentage_text(category_progress)).classes(
                        "text-xs text-slate-500 mt-1"
                    )

                    with ui.row().classes("w-full justify-end gap-2 mt-4"):
                        ui.button(
                            "Details",
                            icon="visibility",
                            on_click=lambda c_id=category["id"]: show_category_details(
                                budget_id,
                                c_id,
                            ),
                        ).props("outline")

                        ui.button(
                            "Add Expense",
                            icon="add",
                            on_click=lambda c_id=category["id"]: show_add_expense_dialog(
                                budget_id=budget_id,
                                category_id=c_id,
                                return_category_id=None,
                            ),
                        ).classes("bg-blue-600 text-white rounded-lg")
