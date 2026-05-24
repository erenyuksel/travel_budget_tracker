from datetime import date

from nicegui import ui

import app_context
from services import (
    add_expense,
    delete_expense,
    get_dashboard_data,
    get_expense,
    update_expense,
)
from ui_helpers import (
    clear_content,
    confirm_action,
    notify_error,
    notify_success,
    page_title,
)


def get_category_options(budget_id):
    data = get_dashboard_data(app_context.session, budget_id)

    category_names_to_ids = {
        category["name"]: category["id"]
        for category in data["categories"]
    }

    return data, category_names_to_ids


def show_add_expense_dialog(budget_id, category_id, return_category_id=None):
    from pages.dashboard_page import show_dashboard
    from pages.category_pages import get_category_by_id, show_category_details

    try:
        data, selected_category = get_category_by_id(budget_id, category_id)
    except Exception as error:
        notify_error(error)
        return

    with ui.dialog() as dialog, ui.card().classes("w-96 rounded-2xl p-6 bg-white"):
        ui.label("Add Expense").classes("text-xl font-bold text-slate-800")
        ui.label(f"Category: {selected_category['name']}").classes(
            "text-sm text-slate-500"
        )

        amount_input = ui.number(
            "Amount spent",
            value=0,
        ).classes("w-full mt-4")

        date_input = ui.input(
            "Expense date",
            value=str(date.today()),
            placeholder="YYYY-MM-DD",
        ).classes("w-full mt-2")

        description_input = ui.input(
            "Description",
            placeholder="Example: Dinner, train ticket, museum ticket",
        ).classes("w-full mt-2")

        def save_expense():
            try:
                description = description_input.value

                if not description:
                    description = f"Expense for {selected_category['name']}"

                add_expense(
                    session=app_context.session,
                    budget_id=budget_id,
                    category_id=category_id,
                    amount=amount_input.value,
                    expense_date=date_input.value,
                    description=description,
                )

                dialog.close()
                notify_success("Expense added successfully.")

                if return_category_id is not None:
                    show_category_details(budget_id, return_category_id)
                else:
                    show_dashboard(budget_id)

            except Exception as error:
                notify_error(error)

        with ui.row().classes("w-full justify-end gap-2 mt-4"):
            ui.button("Cancel", on_click=dialog.close).props("flat")

            ui.button(
                "Add",
                icon="add",
                on_click=save_expense,
            ).classes("bg-blue-600 text-white rounded-lg")

    dialog.open()


def show_edit_expense(expense_id, back_budget_id=None, back_category_id=None):
    from pages.home_page import show_home
    from pages.dashboard_page import show_dashboard
    from pages.category_pages import show_category_details

    clear_content()

    try:
        expense = get_expense(app_context.session, expense_id)

        if expense is None:
            raise ValueError("Expense not found.")

        budget_id = expense.budget_id
        data, category_names_to_ids = get_category_options(budget_id)

    except Exception as error:
        notify_error(error)

        if back_budget_id:
            show_dashboard(back_budget_id)
        else:
            show_home()

        return

    current_category_name = None

    for name, found_category_id in category_names_to_ids.items():
        if found_category_id == expense.category_id:
            current_category_name = name
            break

    with app_context.content:
        page_title(
            "Edit Expense",
            f"Update expense from {data['trip_name']}.",
        )

        with ui.card().classes("w-full max-w-3xl rounded-2xl shadow-sm p-6 mt-6 bg-white"):
            amount_input = ui.number(
                "Amount",
                value=expense.amount,
            ).classes("w-full")

            category_select = ui.select(
                list(category_names_to_ids.keys()),
                label="Category",
                value=current_category_name,
            ).classes("w-full")

            date_input = ui.input(
                "Expense date",
                value=str(expense.expense_date),
                placeholder="YYYY-MM-DD",
            ).classes("w-full")

            description_input = ui.input(
                "Description",
                value=expense.description or "",
            ).classes("w-full")

            def go_back():
                if back_category_id is not None:
                    show_category_details(budget_id, back_category_id)
                else:
                    show_dashboard(budget_id)

            def save_expense_changes():
                try:
                    selected_category_id = category_names_to_ids[category_select.value]

                    update_expense(
                        session=app_context.session,
                        expense_id=expense_id,
                        category_id=selected_category_id,
                        amount=amount_input.value,
                        expense_date=date_input.value,
                        description=description_input.value,
                    )

                    notify_success("Expense updated successfully.")
                    go_back()

                except Exception as error:
                    notify_error(error)

            with ui.row().classes("w-full justify-between mt-4"):
                ui.button(
                    "Delete Expense",
                    icon="delete",
                    on_click=lambda: confirm_delete_expense(
                        expense_id,
                        budget_id,
                        back_category_id,
                    ),
                ).classes("bg-red-600 text-white rounded-lg")

                with ui.row().classes("gap-2"):
                    ui.button("Back", on_click=go_back).props("flat")

                    ui.button(
                        "Save Changes",
                        icon="save",
                        on_click=save_expense_changes,
                    ).classes("bg-blue-600 text-white rounded-lg")


def confirm_delete_expense(expense_id, budget_id, category_id=None):
    from pages.dashboard_page import show_dashboard
    from pages.category_pages import show_category_details

    def do_delete():
        try:
            deleted = delete_expense(app_context.session, expense_id)

            if deleted:
                notify_success("Expense deleted successfully.")

                if category_id is not None:
                    show_category_details(budget_id, category_id)
                else:
                    show_dashboard(budget_id)
            else:
                notify_error("Expense not found.")

        except Exception as error:
            notify_error(error)

    confirm_action(
        title="Delete expense?",
        message="This expense will be permanently removed.",
        confirm_label="Delete Expense",
        on_confirm=do_delete,
    )