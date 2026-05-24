from nicegui import ui

import app_context
from services import (
    ALLOWED_CURRENCIES,
    create_budget,
    delete_budget,
    get_dashboard_data,
    update_budget,
)
from ui_helpers import (
    clear_content,
    confirm_action,
    notify_error,
    notify_success,
    page_title,
)


def show_create_budget():
    from pages.home_page import show_home
    from pages.dashboard_page import show_dashboard

    clear_content()

    with app_context.content:
        page_title(
            "Create Vacation",
            "Set your total budget and divide it into categories.",
        )

        with ui.card().classes("w-full rounded-2xl shadow-sm p-6 mt-6 bg-white"):
            trip_name_input = ui.input(
                "Trip name",
                placeholder="Example: Italy Trip",
            ).classes("w-full")

            with ui.row().classes("w-full gap-4"):
                total_budget_input = ui.number(
                    "Total budget",
                    value=1000,
                ).classes("flex-1")

                currency_select = ui.select(
                    ALLOWED_CURRENCIES,
                    label="Currency",
                    value="CHF",
                ).classes("flex-1")

            ui.label("Budget categories").classes("text-xl font-bold mt-6")

            category_inputs = []

            default_categories = [
                ("Transport", 25),
                ("Food", 25),
                ("Accommodation", 35),
                ("Leisure / Activities", 15),
            ]

            with ui.grid(columns=2).classes("w-full gap-4 mt-2"):
                for name, percentage in default_categories:
                    with ui.card().classes("rounded-xl border border-slate-100 p-4"):
                        name_input = ui.input(
                            "Category name",
                            value=name,
                        ).classes("w-full")

                        percentage_input = ui.number(
                            "Percentage",
                            value=percentage,
                        ).classes("w-full")

                        category_inputs.append(
                            {
                                "name_input": name_input,
                                "percentage_input": percentage_input,
                            }
                        )

            total_label = ui.label("").classes("text-sm mt-2")

            def update_percentage_total():
                total = 0

                for item in category_inputs:
                    value = item["percentage_input"].value

                    if value is not None:
                        total += float(value)

                total_label.text = f"Current total: {round(total, 2)}% / 100%"

                if round(total, 2) == 100:
                    total_label.classes(replace="text-sm text-green-600 mt-2")
                else:
                    total_label.classes(replace="text-sm text-red-600 mt-2")

            for item in category_inputs:
                item["percentage_input"].on(
                    "update:model-value",
                    update_percentage_total,
                )

            update_percentage_total()

            def save_budget():
                try:
                    categories = []

                    for item in category_inputs:
                        categories.append(
                            {
                                "name": item["name_input"].value,
                                "percentage": item["percentage_input"].value,
                            }
                        )

                    budget = create_budget(
                        session=app_context.session,
                        trip_name=trip_name_input.value,
                        total_budget=total_budget_input.value,
                        currency=currency_select.value,
                        categories=categories,
                    )

                    notify_success("Vacation created successfully.")
                    show_dashboard(budget.id)

                except Exception as error:
                    notify_error(error)

            with ui.row().classes("w-full justify-end gap-2 mt-6"):
                ui.button("Cancel", on_click=show_home).props("flat")

                ui.button(
                    "Create Vacation",
                    icon="check",
                    on_click=save_budget,
                ).classes("bg-blue-600 text-white rounded-lg")


def show_edit_budget(budget_id):
    from pages.home_page import show_home
    from pages.dashboard_page import show_dashboard

    clear_content()

    try:
        data = get_dashboard_data(app_context.session, budget_id)
    except Exception as error:
        notify_error(error)
        show_home()
        return

    with app_context.content:
        page_title(
            "Edit Vacation",
            "Update trip details, vacation date, and category percentages.",
        )

        with ui.card().classes("w-full rounded-2xl shadow-sm p-6 mt-6 bg-white"):
            trip_name_input = ui.input(
                "Trip name",
                value=data["trip_name"],
            ).classes("w-full")

            vacation_date_input = ui.input(
                "Vacation date",
                value=str(data["created_at"])[:10],
                placeholder="YYYY-MM-DD",
            ).classes("w-full")

            with ui.row().classes("w-full gap-4"):
                total_budget_input = ui.number(
                    "Total budget",
                    value=data["summary"]["total_budget"],
                ).classes("flex-1")

                currency_select = ui.select(
                    ALLOWED_CURRENCIES,
                    label="Currency",
                    value=data["currency"],
                ).classes("flex-1")

            ui.label("Categories").classes("text-xl font-bold mt-6")

            category_inputs = []

            with ui.grid(columns=2).classes("w-full gap-4 mt-2"):
                for category in data["categories"]:
                    with ui.card().classes("rounded-xl border border-slate-100 p-4"):
                        name_input = ui.input(
                            "Category name",
                            value=category["name"],
                        ).classes("w-full")

                        percentage_input = ui.number(
                            "Percentage",
                            value=category["percentage"],
                        ).classes("w-full")

                        category_inputs.append(
                            {
                                "id": category["id"],
                                "name_input": name_input,
                                "percentage_input": percentage_input,
                            }
                        )

            total_label = ui.label("").classes("text-sm mt-2")

            def update_percentage_total():
                total = 0

                for item in category_inputs:
                    value = item["percentage_input"].value

                    if value is not None:
                        total += float(value)

                total_label.text = f"Current total: {round(total, 2)}% / 100%"

                if round(total, 2) == 100:
                    total_label.classes(replace="text-sm text-green-600 mt-2")
                else:
                    total_label.classes(replace="text-sm text-red-600 mt-2")

            for item in category_inputs:
                item["percentage_input"].on(
                    "update:model-value",
                    update_percentage_total,
                )

            update_percentage_total()

            def save_changes():
                try:
                    categories = []

                    for item in category_inputs:
                        categories.append(
                            {
                                "id": item["id"],
                                "name": item["name_input"].value,
                                "percentage": item["percentage_input"].value,
                            }
                        )

                    update_budget(
                        session=app_context.session,
                        budget_id=budget_id,
                        trip_name=trip_name_input.value,
                        total_budget=total_budget_input.value,
                        currency=currency_select.value,
                        categories=categories,
                        created_at=vacation_date_input.value,
                    )

                    notify_success("Vacation updated successfully.")
                    show_dashboard(budget_id)

                except Exception as error:
                    notify_error(error)

            ui.separator().classes("my-6")

            with ui.row().classes("w-full justify-between items-center"):
                ui.button(
                    "Delete Vacation",
                    icon="delete",
                    on_click=lambda: confirm_delete_budget(budget_id),
                ).classes("bg-red-600 text-white rounded-lg")

                with ui.row().classes("gap-2"):
                    ui.button(
                        "Back",
                        on_click=lambda: show_dashboard(budget_id),
                    ).props("flat")

                    ui.button(
                        "Save Changes",
                        icon="save",
                        on_click=save_changes,
                    ).classes("bg-blue-600 text-white rounded-lg")


def confirm_delete_budget(budget_id):
    from pages.home_page import show_home

    def do_delete():
        try:
            deleted = delete_budget(app_context.session, budget_id)

            if deleted:
                notify_success("Vacation deleted successfully.")
                show_home()
            else:
                notify_error("Vacation not found.")

        except Exception as error:
            notify_error(error)

    confirm_action(
        title="Delete vacation?",
        message="This deletes the whole vacation, all categories, and all expenses.",
        confirm_label="Delete Vacation",
        on_confirm=do_delete,
    )