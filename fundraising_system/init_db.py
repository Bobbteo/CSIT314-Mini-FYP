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
        status TEXT NOT NULL DEFAULT 'active' CHECK(status IN ('active', 'inactive', 'suspended')),
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS UserProfile (
        profile_id INTEGER PRIMARY KEY AUTOINCREMENT,
        account_id INTEGER NOT NULL UNIQUE,
        role TEXT NOT NULL CHECK(role IN ('admin', 'fundraiser', 'doner', 'manager')),
        FOREIGN KEY (account_id) REFERENCES Account(account_id)
    )
    """)

    cursor.execute("SELECT account_id FROM Account WHERE username = ?", ("admin1",))
    existing_admin = cursor.fetchone()

    if not existing_admin:
        password_hash = generate_password_hash("password123")

        cursor.execute("""
            INSERT INTO Account (full_name, username, email, password_hash, status)
            VALUES (?, ?, ?, ?, ?)
        """, ("System Admin", "admin1", "admin1@example.com", password_hash, "active"))

        admin_account_id = cursor.lastrowid

        cursor.execute("""
            INSERT INTO UserProfile (account_id, role)
            VALUES (?, ?)
        """, (admin_account_id, "admin"))

    conn.commit()
    conn.close()
    print("Database ready.")


if __name__ == "__main__":
    init_database()