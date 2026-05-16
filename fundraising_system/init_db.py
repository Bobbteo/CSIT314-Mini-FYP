import sqlite3
import random
from datetime import date, timedelta
from werkzeug.security import generate_password_hash
from config import DB_NAME
import requests
from faker import Faker

fake = Faker()

CATEGORY_DATA = [
    ("Medical", "Support medical treatment and healthcare needs."),
    ("Education", "Support school fees, learning materials, and education access."),
    ("Emergency", "Urgent support for unexpected emergencies."),
    ("Community", "Support community improvement and outreach projects."),
    ("Animal Welfare", "Support animal rescue, treatment, and shelters."),
    ("Disaster Relief", "Help victims affected by disasters."),
    ("Family Support", "Support families facing financial hardship."),
    ("Food Assistance", "Provide meals and food support."),
    ("Housing", "Support rental, shelter, or housing needs."),
    ("Mental Health", "Support counselling and mental health services."),
    ("Elderly Care", "Support elderly care and assistance."),
    ("Children Support", "Support children in need."),
    ("Sports", "Support sports development and participation."),
    ("Arts and Culture", "Support creative and cultural projects."),
    ("Environment", "Support environmental and sustainability efforts.")
]


def fetch_random_users_from_api(count=100):
    try:
        response = requests.get(
            f"https://randomuser.me/api/?results={count}",
            timeout=5
        )
        response.raise_for_status()

        data = response.json()
        users = []

        for item in data["results"]:
            full_name = f"{item['name']['first']} {item['name']['last']}"
            username = item["login"]["username"]
            email = item["email"]

            users.append({
                "full_name": full_name,
                "username": username,
                "email": email
            })

        print("Loaded users from RandomUser API.")
        return users

    except Exception as e:
        print("RandomUser API failed. Using Faker instead.")
        print("Reason:", e)
        return generate_users_with_faker(count)


def generate_users_with_faker(count=100):
    users = []
    used_usernames = set()
    used_emails = set()

    while len(users) < count:
        username = fake.user_name()
        email = fake.email()

        if username in used_usernames or email in used_emails:
            continue

        used_usernames.add(username)
        used_emails.add(email)

        users.append({
            "full_name": fake.name(),
            "username": username,
            "email": email
        })

    print("Loaded users from Faker.")
    return users


def create_tables(cursor):
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS Account (
        account_id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT NOT NULL UNIQUE,
        full_name TEXT NOT NULL,
        email TEXT NOT NULL UNIQUE,
        password_hash TEXT NOT NULL,
        status TEXT NOT NULL DEFAULT 'active'
            CHECK(status IN ('active', 'restricted', 'suspended')),
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

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS FRACategory (
        category_id INTEGER PRIMARY KEY AUTOINCREMENT,
        category_name TEXT NOT NULL UNIQUE,
        description TEXT,
        status TEXT NOT NULL DEFAULT 'active'
            CHECK(status IN ('active', 'inactive')),
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """)

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


def reset_tables(cursor):
    cursor.execute("DROP TABLE IF EXISTS Donation")
    cursor.execute("DROP TABLE IF EXISTS Favourite")
    cursor.execute("DROP TABLE IF EXISTS FundRaisingActivity")
    cursor.execute("DROP TABLE IF EXISTS FRACategory")
    cursor.execute("DROP TABLE IF EXISTS UserProfile")
    cursor.execute("DROP TABLE IF EXISTS Account")


def seed_accounts_and_profiles(cursor):
    password_hash = generate_password_hash("password123")

    admin_password_hash = generate_password_hash("admin")

    cursor.execute("""
        INSERT INTO Account (username, full_name, email, password_hash, status)
        VALUES (?, ?, ?, ?, ?)
    """, ("admin", "System Admin", "admin@example.com", admin_password_hash, "active"))

    admin_id = cursor.lastrowid

    cursor.execute("""
        INSERT INTO UserProfile (account_id, role)
        VALUES (?, ?)
    """, (admin_id, "admin"))

    roles = ["fundraiser", "doner", "manager"]
    status_choices = ["active", "active", "active", "restricted", "suspended"]

    account_ids_by_role = {
        "admin": [admin_id],
        "fundraiser": [],
        "doner": [],
        "manager": []
    }

    demo_accounts = [
        ("fundraiser", "Demo Fundraiser", "fundraiser@example.com", "fundraiser", "fundraiser"),
        ("doner", "Demo Donor", "doner@example.com", "doner", "doner"),
        ("manager", "Demo Manager", "manager@example.com", "manager", "manager"),
    ]
    for username, full_name, email, password, role in demo_accounts:
        demo_hash = generate_password_hash(password)
        cursor.execute("""
            INSERT INTO Account (username, full_name, email, password_hash, status)
            VALUES (?, ?, ?, ?, ?)
        """, (username, full_name, email, demo_hash, "active"))
        demo_id = cursor.lastrowid
        cursor.execute("""
            INSERT INTO UserProfile (account_id, role)
            VALUES (?, ?)
        """, (demo_id, role))
        account_ids_by_role[role].append(demo_id)

    random_users = fetch_random_users_from_api(99)

    for i in range(2, 101):
        role = roles[(i - 2) % len(roles)]

        user_data = random_users[i - 2]
        username = f"{role}_{user_data['username']}_{i}"
        full_name = user_data["full_name"]
        email = f"{role}_{i}_{user_data['email']}"
        status = random.choice(status_choices)

        cursor.execute("""
            INSERT INTO Account (username, full_name, email, password_hash, status)
            VALUES (?, ?, ?, ?, ?)
        """, (username, full_name, email, password_hash, status))

        account_id = cursor.lastrowid

        cursor.execute("""
            INSERT INTO UserProfile (account_id, role)
            VALUES (?, ?)
        """, (account_id, role))

        account_ids_by_role[role].append(account_id)

    return account_ids_by_role


def seed_categories(cursor):
    selected_categories = CATEGORY_DATA[:15]

    for category_name, description in selected_categories:
        cursor.execute("""
            INSERT INTO FRACategory (category_name, description, status)
            VALUES (?, ?, ?)
        """, (category_name, description, "active"))

    return [category[0] for category in selected_categories]


def calculate_status(current_amount, target_amount, end_date_string):
    today = date.today()
    end_date = date.fromisoformat(end_date_string)

    if today > end_date:
        if current_amount >= target_amount:
            return "completed"
        return "closed"

    if current_amount >= target_amount:
        return "goal_achieved"

    return "active"


def seed_fras(cursor, fundraiser_ids, categories):
    fra_ids = []

    title_templates = [
        "Help Support {category} Needs",
        "{category} Fundraising Campaign",
        "Community Support for {category}",
        "Urgent {category} Assistance",
        "Give Hope Through {category}"
    ]

    for i in range(1, 101):
        fundraiser_id = random.choice(fundraiser_ids)
        category = random.choice(categories)
        target_amount = random.randint(1000, 50000)
        current_amount = random.randint(0, int(target_amount * 1.2))
        start_date = date.today() - timedelta(days=random.randint(1, 90))
        end_date = start_date + timedelta(days=random.randint(15, 120))

        status = calculate_status(current_amount, target_amount, end_date.isoformat())

        if random.random() < 0.08:
            status = "cancelled"

        title = random.choice(title_templates).format(category=category)
        description = (
            f"This fundraising activity aims to support {category.lower()} related needs. "
            f"Funds collected will be used to provide meaningful assistance to the donees."
        )
        view_count = random.randint(0, 500)

        cursor.execute("""
            INSERT INTO FundRaisingActivity
            (fundraiser_account_id, title, description, category, target_amount,
             current_amount, view_count, status, start_date, end_date)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            fundraiser_id,
            title,
            description,
            category,
            target_amount,
            current_amount,
            view_count,
            status,
            start_date.isoformat(),
            end_date.isoformat()
        ))

        fra_ids.append(cursor.lastrowid)

    return fra_ids


def seed_favourites(cursor, doner_ids, fra_ids):
    favourite_pairs = set()
    favourite_count_by_doner = {doner_id: 0 for doner_id in doner_ids}

    attempts = 0
    while len(favourite_pairs) < 100 and attempts < 5000:
        attempts += 1
        doner_id = random.choice(doner_ids)

        if favourite_count_by_doner[doner_id] >= 5:
            continue

        fra_id = random.choice(fra_ids)
        pair = (doner_id, fra_id)

        if pair in favourite_pairs:
            continue

        favourite_pairs.add(pair)
        favourite_count_by_doner[doner_id] += 1

        cursor.execute("""
            INSERT INTO Favourite (doner_account_id, fra_id)
            VALUES (?, ?)
        """, pair)


def seed_donations(cursor, doner_ids, fra_ids):
    for _ in range(100):
        doner_id = random.choice(doner_ids)
        fra_id = random.choice(fra_ids)
        amount = round(random.uniform(5, 500), 2)

        cursor.execute("""
            INSERT INTO Donation (doner_account_id, fra_id, amount)
            VALUES (?, ?, ?)
        """, (doner_id, fra_id, amount))

        cursor.execute("""
            UPDATE FundRaisingActivity
            SET current_amount = current_amount + ?
            WHERE fra_id = ?
        """, (amount, fra_id))


def refresh_fra_statuses(cursor):
    rows = cursor.execute("""
        SELECT fra_id, current_amount, target_amount, end_date, status
        FROM FundRaisingActivity
    """).fetchall()

    for row in rows:
        if row["status"] == "cancelled":
            continue

        new_status = calculate_status(
            row["current_amount"],
            row["target_amount"],
            row["end_date"]
        )

        cursor.execute("""
            UPDATE FundRaisingActivity
            SET status = ?
            WHERE fra_id = ?
        """, (new_status, row["fra_id"]))


def init_database():
    print("Initializing database at:", DB_NAME)

    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    reset_tables(cursor)
    create_tables(cursor)

    account_ids_by_role = seed_accounts_and_profiles(cursor)
    categories = seed_categories(cursor)

    fra_ids = seed_fras(
        cursor,
        fundraiser_ids=account_ids_by_role["fundraiser"],
        categories=categories
    )

    seed_favourites(
        cursor,
        doner_ids=account_ids_by_role["doner"],
        fra_ids=fra_ids
    )

    seed_donations(
        cursor,
        doner_ids=account_ids_by_role["doner"],
        fra_ids=fra_ids
    )

    refresh_fra_statuses(cursor)

    conn.commit()
    conn.close()

    print("Database ready with demo data.")
    print("Demo logins: admin / admin, fundraiser / fundraiser, doner / doner, manager / manager")
    print("Other seeded users use password123.")


if __name__ == "__main__":
    init_database()