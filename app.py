from nicegui import ui

import app_context
from app_context import APP_TITLE
from pages.home_page import show_home
from ui_layout import app_header


# -----------------------------
# App start
# Shared entry point
# -----------------------------

ui.add_head_html(
    """
    <style>
        body {
            background: #f8fafc;
        }
    </style>
    """
)

app_header()

main_content = ui.column().classes(
    "w-full max-w-7xl mx-auto px-6 py-8 gap-0"
)

app_context.set_content(main_content)

show_home()

ui.run(
    title=APP_TITLE,
    reload=False,
)
