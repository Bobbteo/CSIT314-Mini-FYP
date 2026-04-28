import sqlite3
from werkzeug.security import generate_password_hash
from config import DB_NAME


def init_database():
    print("Initializing database at:", DB_NAME)

    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    # Account table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS Account (
        account_id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT NOT NULL UNIQUE,
        full_name TEXT NOT NULL,
        email TEXT NOT NULL UNIQUE,
        password_hash TEXT NOT NULL,
        status TEXT NOT NULL DEFAULT 'active' CHECK(status IN ('active', 'restricted', 'suspended')),
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """)

    # UserProfile table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS UserProfile (
        profile_id INTEGER PRIMARY KEY AUTOINCREMENT,
        account_id INTEGER NOT NULL UNIQUE,
        role TEXT NOT NULL CHECK(role IN ('admin', 'fundraiser', 'doner', 'manager')),
        FOREIGN KEY (account_id) REFERENCES Account(account_id)
    )
    """)

    # Check if admin account already exists
    cursor.execute("SELECT account_id FROM Account WHERE username = ?", ("admin",))
    existing_admin = cursor.fetchone()

    if existing_admin is None:
        password_hash = generate_password_hash("admin")

        cursor.execute("""
            INSERT INTO Account (username, full_name, email, password_hash, status)
            VALUES (?, ?, ?, ?, ?)
        """, (
            "admin",
            "admin",
            "-",
            password_hash,
            "active"
        ))

        admin_account_id = cursor.lastrowid

        cursor.execute("""
            INSERT INTO UserProfile (account_id, role)
            VALUES (?, ?)
        """, (admin_account_id, "admin"))

        print("Admin account created.")
    else:
        # Make sure admin profile exists too
        admin_account_id = existing_admin[0]
        cursor.execute("SELECT profile_id FROM UserProfile WHERE account_id = ?", (admin_account_id,))
        existing_profile = cursor.fetchone()

        if existing_profile is None:
            cursor.execute("""
                INSERT INTO UserProfile (account_id, role)
                VALUES (?, ?)
            """, (admin_account_id, "admin"))
            print("Admin profile created.")

    # FRA Table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS FundRaisingActivity (
        fra_id INTEGER PRIMARY KEY AUTOINCREMENT,
        fundraiser_account_id INTEGER NOT NULL,
        title TEXT NOT NULL,
        description TEXT NOT NULL,
        category TEXT NOT NULL,
        target_amount REAL NOT NULL,
        current_amount REAL NOT NULL DEFAULT 0,
        view_count INTEGER NOT NULL DEFAULT 0,
        status TEXT NOT NULL DEFAULT 'active'
        CHECK(status IN ('active', 'goal_achieved', 'completed', 'closed', 'cancelled')),
        start_date TEXT NOT NULL,
        end_date TEXT NOT NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (fundraiser_account_id) REFERENCES Account(account_id)
    )
    """)

    # Favourite Table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS Favourite (
        favourite_id INTEGER PRIMARY KEY AUTOINCREMENT,
        doner_account_id INTEGER NOT NULL,
        fra_id INTEGER NOT NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        UNIQUE(doner_account_id, fra_id),
        FOREIGN KEY (doner_account_id) REFERENCES Account(account_id),
        FOREIGN KEY (fra_id) REFERENCES FundRaisingActivity(fra_id)
    )
    """)

    # Donation Table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS Donation (
        donation_id INTEGER PRIMARY KEY AUTOINCREMENT,
        doner_account_id INTEGER NOT NULL,
        fra_id INTEGER NOT NULL,
        amount REAL NOT NULL,
        donated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (doner_account_id) REFERENCES Account(account_id),
        FOREIGN KEY (fra_id) REFERENCES FundRaisingActivity(fra_id)
    )
    """)

    conn.commit()
    conn.close()
    print("Database ready.")


if __name__ == "__main__":
    init_database()