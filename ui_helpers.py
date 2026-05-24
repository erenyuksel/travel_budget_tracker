from nicegui import ui

import app_context




def money(amount, currency):
    return f"{float(amount):,.2f} {currency}"


def safe_ratio(value, total):
    if not total or total <= 0:
        return 0

    ratio = float(value) / float(total)
    return max(0, min(ratio, 1))


def percentage_text(value):
    return f"{round(float(value) * 100, 1)}% used"


def clear_content():
    if app_context.content is not None:
        app_context.content.clear()


def notify_success(message):
    ui.notify(message, type="positive", position="top")


def notify_error(error):
    ui.notify(str(error), type="negative", position="top")


def page_title(title, subtitle=None):
    ui.label(title).classes("text-3xl font-bold text-slate-800")

    if subtitle:
        ui.label(subtitle).classes("text-slate-500 mt-1")


def confirm_action(title, message, confirm_label, on_confirm):
    with ui.dialog() as dialog, ui.card().classes("w-96 rounded-2xl p-6"):
        ui.label(title).classes("text-xl font-bold text-slate-800")
        ui.label(message).classes("text-slate-500 mt-2")

        with ui.row().classes("w-full justify-end gap-2 mt-6"):
            ui.button("Cancel", on_click=dialog.close).props("flat")

            def confirm():
                dialog.close()
                on_confirm()

            ui.button(confirm_label, on_click=confirm).classes(
                "bg-red-600 text-white rounded-lg"
            )

    dialog.open()


def summary_card(title, value, icon, icon_class):
    with ui.card().classes(
        "rounded-2xl shadow-sm border border-slate-100 p-5 flex-1 min-w-56 bg-white"
    ):
        with ui.row().classes("w-full justify-between items-center"):
            with ui.column().classes("gap-1"):
                ui.label(title).classes("text-sm text-slate-500")
                ui.label(value).classes("text-2xl font-bold text-slate-800")

            ui.icon(icon).classes(f"text-4xl {icon_class}")


def empty_state(icon, title, subtitle, button_label=None, on_click=None):
    with ui.card().classes(
        "w-full rounded-2xl p-8 text-center border border-dashed border-slate-300 bg-white"
    ):
        ui.icon(icon).classes("text-6xl text-slate-400")
        ui.label(title).classes("text-2xl font-bold text-slate-800 mt-2")
        ui.label(subtitle).classes("text-slate-500 mt-1")

        if button_label and on_click:
            ui.button(button_label, on_click=on_click).classes(
                "bg-blue-600 text-white rounded-lg mt-4"
            )
