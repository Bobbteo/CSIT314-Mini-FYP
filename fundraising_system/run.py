import os
from config import DB_NAME
from init_db import init_database
from app import app


def database_exists():
    return os.path.exists(DB_NAME)


def main():
    if not database_exists():
        print("Database not found. Creating a new one...")
        init_database()
    else:
        print("Database already exists:", DB_NAME)
        # still safe to call, because CREATE TABLE IF NOT EXISTS is used
        init_database()

    print("Starting Flask app...")
    app.run(debug=True, use_reloader=False)


if __name__ == "__main__":
    main()