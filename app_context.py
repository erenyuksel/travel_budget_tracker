from db import engine, SessionLocal
from services import create_tables


APP_TITLE = "Travel Budget Tracker"

create_tables(engine)
session = SessionLocal()

# NiceGUI content container is created in app.py and stored here
# so all page files can reuse the same main area.
content = None


def set_content(content_container):
    global content
    content = content_container
