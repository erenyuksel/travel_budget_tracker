from sqlalchemy import text

from db import engine, SessionLocal
from services import create_tables, seed_default_budget


def main():
    create_tables(engine)
    session = SessionLocal()

    try:
        has_data = session.execute(text("SELECT 1 FROM budgets LIMIT 1")).first()

        if has_data:
            print("Database already exists and contains data.")
        else:
            seed_default_budget(session)
            print("Database created and sample data inserted.")
    finally:
        session.close()


if __name__ == "__main__":
    main()
