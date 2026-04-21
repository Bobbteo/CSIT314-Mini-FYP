from database.db_helper import DBHelper
from entity.account import Account


class AccountRepository:
    def _row_to_account(self, row):
        if not row:
            return None
        return Account(
            account_id=row["account_id"],
            full_name=row["full_name"],
            username=row["username"],
            email=row["email"],
            password_hash=row["password_hash"],
            status=row["status"],
            created_at=row["created_at"]
        )

    def find_by_username_or_email(self, username_or_email):
        conn = DBHelper.get_connection()
        row = conn.execute("""
            SELECT * FROM Account
            WHERE username = ? OR email = ?
        """, (username_or_email, username_or_email)).fetchone()
        conn.close()
        return self._row_to_account(row)

    def find_by_id(self, account_id):
        conn = DBHelper.get_connection()
        row = conn.execute("""
            SELECT * FROM Account
            WHERE account_id = ?
        """, (account_id,)).fetchone()
        conn.close()
        return self._row_to_account(row)

    def get_all_accounts(self):
        conn = DBHelper.get_connection()
        rows = conn.execute("""
            SELECT * FROM Account
            ORDER BY account_id ASC
        """).fetchall()
        conn.close()
        return [self._row_to_account(row) for row in rows]

    def search_accounts(self, keyword):
        conn = DBHelper.get_connection()
        rows = conn.execute("""
            SELECT * FROM Account
            WHERE full_name LIKE ?
               OR username LIKE ?
               OR email LIKE ?
            ORDER BY account_id ASC
        """, (f"%{keyword}%", f"%{keyword}%", f"%{keyword}%")).fetchall()
        conn.close()
        return [self._row_to_account(row) for row in rows]

    def username_exists(self, username, exclude_account_id=None):
        conn = DBHelper.get_connection()
        if exclude_account_id is None:
            row = conn.execute("""
                SELECT account_id FROM Account WHERE username = ?
            """, (username,)).fetchone()
        else:
            row = conn.execute("""
                SELECT account_id FROM Account
                WHERE username = ? AND account_id != ?
            """, (username, exclude_account_id)).fetchone()
        conn.close()
        return row is not None

    def email_exists(self, email, exclude_account_id=None):
        conn = DBHelper.get_connection()
        if exclude_account_id is None:
            row = conn.execute("""
                SELECT account_id FROM Account WHERE email = ?
            """, (email,)).fetchone()
        else:
            row = conn.execute("""
                SELECT account_id FROM Account
                WHERE email = ? AND account_id != ?
            """, (email, exclude_account_id)).fetchone()
        conn.close()
        return row is not None

    def create_account(self, full_name, username, email, password_hash, status="active"):
        conn = DBHelper.get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO Account (full_name, username, email, password_hash, status)
            VALUES (?, ?, ?, ?, ?)
        """, (full_name, username, email, password_hash, status))
        conn.commit()
        new_id = cursor.lastrowid
        conn.close()
        return new_id

    def update_account(self, account_id, full_name, username, email, status):
        conn = DBHelper.get_connection()
        conn.execute("""
            UPDATE Account
            SET full_name = ?, username = ?, email = ?, status = ?
            WHERE account_id = ?
        """, (full_name, username, email, status, account_id))
        conn.commit()
        conn.close()

    def update_password(self, account_id, password_hash):
        conn = DBHelper.get_connection()
        conn.execute("""
            UPDATE Account
            SET password_hash = ?
            WHERE account_id = ?
        """, (password_hash, account_id))
        conn.commit()
        conn.close()

    def suspend_account(self, account_id):
        conn = DBHelper.get_connection()
        conn.execute("""
            UPDATE Account
            SET status = 'suspended'
            WHERE account_id = ?
        """, (account_id,))
        conn.commit()
        conn.close()