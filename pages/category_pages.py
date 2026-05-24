from nicegui import ui

import app_context
from services import get_category_details, get_dashboard_data, search_expenses
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

        ui.label("Filter Expenses").classes("text-2xl font-bold mt-8")

        with ui.card().classes("w-full rounded-2xl shadow-sm p-5 mt-3 bg-white"):
            with ui.grid(columns=3).classes("w-full gap-4"):
                search_input = ui.input(
                    "Search description",
                    placeholder="Example: dinner, train, hotel",
                ).classes("w-full")

                start_date_input = ui.input(
                    "Start date",
                    placeholder="YYYY-MM-DD",
                ).classes("w-full")

                end_date_input = ui.input(
                    "End date",
                    placeholder="YYYY-MM-DD",
                ).classes("w-full")

                min_amount_input = ui.number(
                    "Min amount",
                ).classes("w-full")

                max_amount_input = ui.number(
                    "Max amount",
                ).classes("w-full")

            def apply_filters():
                try:
                    filtered_expenses = search_expenses(
                        session=app_context.session,
                        budget_id=budget_id,
                        search_text=search_input.value or None,
                        category_id=category_id,
                        start_date=start_date_input.value or None,
                        end_date=end_date_input.value or None,
                        min_amount=min_amount_input.value,
                        max_amount=max_amount_input.value,
                    )

                    render_expenses(filtered_expenses, is_filtered=True)

                except Exception as error:
                    notify_error(error)

            def clear_filters():
                search_input.value = ""
                start_date_input.value = ""
                end_date_input.value = ""
                min_amount_input.value = None
                max_amount_input.value = None

                render_expenses(data["expenses"])

            with ui.row().classes("w-full justify-end gap-2 mt-4"):
                ui.button(
                    "Clear Filters",
                    icon="clear",
                    on_click=clear_filters,
                ).props("outline")

                ui.button(
                    "Apply Filters",
                    icon="filter_alt",
                    on_click=apply_filters,
                ).classes("bg-blue-600 text-white rounded-lg")

        ui.label("Expenses").classes("text-2xl font-bold mt-8")

        expense_container = ui.column().classes("w-full gap-0")

        def render_expenses(expenses, is_filtered=False):
            expense_container.clear()

            with expense_container:
                if not expenses:
                    if is_filtered:
                        empty_state(
                            icon="search_off",
                            title="No matching expenses",
                            subtitle="Try changing the filters or clear them.",
                            button_label="Clear Filters",
                            on_click=clear_filters,
                        )
                    else:
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
                                ui.label(
                                    expense["description"] or "No description"
                                ).classes("text-slate-500")
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

        render_expenses(data["expenses"])