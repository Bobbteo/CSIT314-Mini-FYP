import sqlite3
from werkzeug.security import generate_password_hash
from config import DB_NAME


def init_database():
    print("Initializing database at:", DB_NAME)

    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS Account (
        account_id INTEGER PRIMARY KEY AUTOINCREMENT,
        full_name TEXT NOT NULL,
        username TEXT NOT NULL UNIQUE,
        email TEXT NOT NULL UNIQUE,
        password_hash TEXT NOT NULL,
        role TEXT NOT NULL CHECK(role IN ('admin', 'fundraiser', 'doner', 'manager')),
        status TEXT NOT NULL DEFAULT 'active' CHECK(status IN ('active', 'inactive', 'suspended')),
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """)

    demo_accounts = [
        ("System Admin", "admin1", "admin1@example.com", "password123", "admin", "active"),
        ("Fund Raiser One", "fundraiser1", "fundraiser1@example.com", "password123", "fundraiser", "active"),
        ("Doner One", "doner1", "doner1@example.com", "password123", "doner", "active"),
        ("Platform Manager", "manager1", "manager1@example.com", "password123", "manager", "active"),
    ]

    for full_name, username, email, password, role, status in demo_accounts:
        cursor.execute("SELECT account_id FROM Account WHERE username = ?", (username,))
        existing_account = cursor.fetchone()

        if not existing_account:
            password_hash = generate_password_hash(password)
            cursor.execute("""
                INSERT INTO Account (full_name, username, email, password_hash, role, status)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (full_name, username, email, password_hash, role, status))

    conn.commit()
    conn.close()
    print("Database ready.")


if __name__ == "__main__":
    init_database()