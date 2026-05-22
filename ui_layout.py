from nicegui import ui

from app_context import APP_TITLE


# -----------------------------
# Header / navigation
# Person 1 can own this file.
# -----------------------------

def app_header():
    from pages.home_page import show_home
    from pages.budget_pages import show_create_budget

    with ui.header().classes("bg-slate-900 text-white shadow-md px-6 py-3"):
        with ui.row().classes("w-full justify-between items-center"):
            with ui.row().classes("items-center gap-3"):
                ui.icon("flight_takeoff").classes("text-3xl text-blue-300")
                ui.label(APP_TITLE).classes("text-xl font-bold")

            with ui.row().classes("gap-2"):
                ui.button("Home", icon="home", on_click=show_home).props("flat")
                ui.button(
                    "New Vacation",
                    icon="add",
                    on_click=show_create_budget,
                ).classes("bg-blue-600 text-white rounded-lg")
