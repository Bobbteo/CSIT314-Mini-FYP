from werkzeug.security import generate_password_hash, check_password_hash
from database.db_helper import DBHelper
from entity.user_profile import UserProfile


class Account:
    allowed_roles = ["fundraiser", "doner", "manager"]
    allowed_statuses = ["active", "restricted", "suspended"]

    def __init__(self, account_id=None, username=None, full_name=None, email=None,
                 password_hash=None, status=None, created_at=None, role=None):
        self.account_id = account_id
        self.username = username
        self.full_name = full_name
        self.email = email
        self.password_hash = password_hash
        self.status = status
        self.created_at = created_at
        self.role = role

    def is_suspended(self):
        return self.status == "suspended"

    def is_restricted(self):
        return self.status == "restricted"

    @staticmethod
    def _row_to_account(row):
        if not row:
            return None

        profile = UserProfile.find_by_account_id(row["account_id"])
        role = profile.role if profile else None

        return Account(
            account_id=row["account_id"],
            username=row["username"],
            full_name=row["full_name"],
            email=row["email"],
            password_hash=row["password_hash"],
            status=row["status"],
            created_at=row["created_at"],
            role=role
        )

    @staticmethod
    def find_by_username_or_email(username_or_email):
        conn = DBHelper.get_connection()
        row = conn.execute("""
            SELECT * FROM Account
            WHERE username = ? OR email = ?
        """, (username_or_email, username_or_email)).fetchone()
        conn.close()

        return Account._row_to_account(row)

    @staticmethod
    def find_by_id(account_id):
        conn = DBHelper.get_connection()
        row = conn.execute("""
            SELECT * FROM Account
            WHERE account_id = ?
        """, (account_id,)).fetchone()
        conn.close()

        return Account._row_to_account(row)

    @staticmethod
    def authenticate(username_or_email, password):
        username_or_email = username_or_email.strip()
        password = password.strip()

        if not username_or_email or not password:
            return {"success": False, "message": "Please enter both username/email and password."}

        account = Account.find_by_username_or_email(username_or_email)

        if account is None:
            return {"success": False, "message": "Invalid username/email or password."}

        if account.is_suspended():
            return {"success": False, "message": "Your account has been suspended."}

        if not check_password_hash(account.password_hash, password):
            return {"success": False, "message": "Invalid username/email or password."}

        if not account.role:
            return {"success": False, "message": "No role assigned to this account."}

        return {
            "success": True,
            "message": f"Welcome, {account.full_name}!",
            "account": account
        }

    @staticmethod
    def get_dashboard_route(role):
        if role == "admin":
            return "admin_dashboard"
        elif role == "fundraiser":
            return "fundraiser_dashboard"
        elif role == "doner":
            return "doner_dashboard"
        elif role == "manager":
            return "manager_dashboard"
        return None

    @staticmethod
    def get_all_accounts():
        conn = DBHelper.get_connection()
        rows = conn.execute("""
            SELECT * FROM Account
            ORDER BY account_id ASC
        """).fetchall()
        conn.close()

        return [Account._row_to_account(row) for row in rows]

    @staticmethod
    def search_accounts(keyword):
        keyword = keyword.strip().lower()

        if not keyword:
            return Account.get_all_accounts()

        all_accounts = Account.get_all_accounts()
        results = []

        for account in all_accounts:
            role = account.role or ""

            if (
                keyword in account.username.lower()
                or keyword in account.full_name.lower()
                or keyword in account.email.lower()
                or keyword in role.lower()
                or keyword in account.status.lower()
            ):
                results.append(account)

        return results

    @staticmethod
    def username_exists(username, exclude_account_id=None):
        conn = DBHelper.get_connection()

        if exclude_account_id:
            row = conn.execute("""
                SELECT account_id FROM Account
                WHERE username = ? AND account_id != ?
            """, (username, exclude_account_id)).fetchone()
        else:
            row = conn.execute("""
                SELECT account_id FROM Account
                WHERE username = ?
            """, (username,)).fetchone()

        conn.close()
        return row is not None

    @staticmethod
    def email_exists(email, exclude_account_id=None):
        conn = DBHelper.get_connection()

        if exclude_account_id:
            row = conn.execute("""
                SELECT account_id FROM Account
                WHERE email = ? AND account_id != ?
            """, (email, exclude_account_id)).fetchone()
        else:
            row = conn.execute("""
                SELECT account_id FROM Account
                WHERE email = ?
            """, (email,)).fetchone()

        conn.close()
        return row is not None

    @staticmethod
    def create_account(username, full_name, email, password, role):
        username = username.strip()
        full_name = full_name.strip()
        email = email.strip()
        password = password.strip()
        role = role.strip()

        if not username or not full_name or not email or not password or not role:
            return {"success": False, "message": "All fields are required."}

        if role not in Account.allowed_roles:
            return {"success": False, "message": "Invalid role selected."}

        if Account.username_exists(username):
            return {"success": False, "message": "Username already exists."}

        if Account.email_exists(email):
            return {"success": False, "message": "Email already exists."}

        password_hash = generate_password_hash(password)

        conn = DBHelper.get_connection()
        cursor = conn.cursor()

        cursor.execute("""
            INSERT INTO Account (username, full_name, email, password_hash, status)
            VALUES (?, ?, ?, ?, ?)
        """, (username, full_name, email, password_hash, "active"))

        account_id = cursor.lastrowid
        conn.commit()
        conn.close()

        UserProfile.create_profile(account_id, role)

        return {"success": True, "message": "Account created successfully."}

    @staticmethod
    def update_account(account_id, username, full_name, email, role, new_password=None):
        account = Account.find_by_id(account_id)

        if not account:
            return {"success": False, "message": "Account not found."}

        if account.role == "admin":
            return {"success": False, "message": "Admin account cannot be edited."}

        username = username.strip()
        full_name = full_name.strip()
        email = email.strip()
        role = role.strip()

        if not username or not full_name or not email or not role:
            return {"success": False, "message": "Please fill in all required fields."}

        if role not in Account.allowed_roles:
            return {"success": False, "message": "Invalid role selected."}

        if Account.username_exists(username, exclude_account_id=account_id):
            return {"success": False, "message": "Username already exists."}

        if Account.email_exists(email, exclude_account_id=account_id):
            return {"success": False, "message": "Email already exists."}

        conn = DBHelper.get_connection()

        conn.execute("""
            UPDATE Account
            SET username = ?, full_name = ?, email = ?,
            WHERE account_id = ?
        """, (username, full_name, email, account_id))

        if new_password and new_password.strip():
            password_hash = generate_password_hash(new_password.strip())
            conn.execute("""
                UPDATE Account
                SET password_hash = ?
                WHERE account_id = ?
            """, (password_hash, account_id))

        conn.commit()
        conn.close()

        profile = UserProfile.find_by_account_id(account_id)

        if profile:
            UserProfile.update_role_by_account_id(account_id, role)
        else:
            UserProfile.create_profile(account_id, role)

        return {"success": True, "message": "Account updated successfully."}
    
    @staticmethod
    def restrict_account(account_id):
        account = Account.find_by_id(account_id)

        if not account:
            return {"success": False, "message": "Account not found."}

        if account.role == "admin":
            return {"success": False, "message": "Admin account cannot be restricted."}

        conn = DBHelper.get_connection()
        conn.execute("""
            UPDATE Account
            SET status = 'restricted'
            WHERE account_id = ?
        """, (account_id,))
        conn.commit()
        conn.close()

        return {"success": True, "message": "Account restricted successfully."}


    @staticmethod
    def remove_restriction(account_id):
        account = Account.find_by_id(account_id)

        if not account:
            return {"success": False, "message": "Account not found."}

        conn = DBHelper.get_connection()
        conn.execute("""
            UPDATE Account
            SET status = 'active'
            WHERE account_id = ?
        """, (account_id,))
        conn.commit()
        conn.close()

        return {"success": True, "message": "Restriction removed successfully."}

    @staticmethod
    def suspend_account(account_id):
        account = Account.find_by_id(account_id)

        if not account:
            return {"success": False, "message": "Account not found."}

        if account.role == "admin":
            return {"success": False, "message": "Admin account cannot be suspended."}

        conn = DBHelper.get_connection()

        conn.execute("""
            UPDATE Account
            SET status = 'suspended'
            WHERE account_id = ?
        """, (account_id,))

        conn.commit()
        conn.close()

        return {"success": True, "message": "Account suspended successfully."}
    
    @staticmethod
    def remove_suspension(account_id):
        account = Account.find_by_id(account_id)

        if not account:
            return {"success": False, "message": "Account not found."}

        conn = DBHelper.get_connection()
        conn.execute("""
            UPDATE Account
            SET status = 'active'
            WHERE account_id = ?
        """, (account_id,))
        conn.commit()
        conn.close()

        return {"success": True, "message": "Suspension removed successfully."}