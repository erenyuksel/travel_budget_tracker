from db import engine, SessionLocal
from services import create_tables


APP_TITLE = "Trip Tracker"

create_tables(engine)
session = SessionLocal()

content = None


def set_content(content_container):
    global content
    content = content_container