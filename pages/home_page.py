from nicegui import ui

import app_context
from services import list_budgets, get_dashboard_data
from ui_helpers import (
    clear_content,
    empty_state,
    money,
    notify_error,
    page_title,
    percentage_text,
    safe_ratio,
)


# -----------------------------
# Home
# Person 1 responsibility
# -----------------------------

def show_home():
    from pages.budget_pages import (
        show_create_budget,
        show_edit_budget,
        confirm_delete_budget,
    )
    from pages.dashboard_page import show_dashboard

    clear_content()

    with app_context.content:
        with ui.row().classes("w-full justify-between items-start"):
            page_title(
                "Your Vacations",
                "Manage all travel budgets from one simple overview.",
            )

            ui.button(
                "Create Vacation",
                icon="add",
                on_click=show_create_budget,
            ).classes("bg-blue-600 text-white rounded-lg")

        budgets = list_budgets(app_context.session)

        if not budgets:
            empty_state(
                icon="travel_explore",
                title="No vacations yet",
                subtitle="Create your first vacation budget to start tracking expenses.",
                button_label="Create Vacation",
                on_click=show_create_budget,
            )
            return

        with ui.grid(columns=2).classes("w-full gap-4 mt-6"):
            for budget in budgets:
                try:
                    data = get_dashboard_data(app_context.session, budget.id)
                    summary = data["summary"]

                    with ui.card().classes(
                        "rounded-2xl shadow-sm border border-slate-100 p-5 bg-white"
                    ):
                        with ui.row().classes("w-full justify-between items-start"):
                            with ui.column().classes("gap-1"):
                                ui.label(data["trip_name"]).classes(
                                    "text-xl font-bold text-slate-800"
                                )
                                ui.label(f"Currency: {data['currency']}").classes(
                                    "text-slate-500"
                                )
                                ui.label(
                                    f"Created: {str(data['created_at'])[:10]}"
                                ).classes("text-xs text-slate-400")

                            ui.icon("luggage").classes("text-4xl text-blue-500")

                        ui.separator().classes("my-3")

                        with ui.row().classes("w-full gap-4"):
                            with ui.column().classes("gap-0 flex-1"):
                                ui.label("Total").classes("text-xs text-slate-400")
                                ui.label(
                                    money(summary["total_budget"], data["currency"])
                                ).classes("font-semibold")

                            with ui.column().classes("gap-0 flex-1"):
                                ui.label("Spent").classes("text-xs text-slate-400")
                                ui.label(
                                    money(summary["total_spent"], data["currency"])
                                ).classes("font-semibold text-orange-600")

                            with ui.column().classes("gap-0 flex-1"):
                                ui.label("Remaining").classes("text-xs text-slate-400")
                                ui.label(
                                    money(summary["remaining_budget"], data["currency"])
                                ).classes("font-semibold text-green-600")

                        progress = safe_ratio(
                            summary["total_spent"],
                            summary["total_budget"],
                        )

                        ui.linear_progress(
                            value=progress,
                            show_value=False,
                        ).classes("mt-4")

                        ui.label(percentage_text(progress)).classes(
                            "text-xs text-slate-500 mt-1"
                        )

                        with ui.row().classes("w-full justify-end gap-2 mt-4"):
                            ui.button(
                                "Open",
                                icon="visibility",
                                on_click=lambda b_id=budget.id: show_dashboard(b_id),
                            ).classes("bg-blue-600 text-white rounded-lg")

                            ui.button(
                                "Edit",
                                icon="edit",
                                on_click=lambda b_id=budget.id: show_edit_budget(b_id),
                            ).props("outline")

                            ui.button(
                                "Delete",
                                icon="delete",
                                on_click=lambda b_id=budget.id: confirm_delete_budget(b_id),
                            ).classes("bg-red-600 text-white rounded-lg")

                except Exception as error:
                    notify_error(error)
