from database.db_helper import DBHelper
from entity.account import Account

class AccountRepository:
    def find_by_username_or_email(self, username_or_email):
        conn = DBHelper.get_connection()
        row = conn.execute("""
            SELECT * FROM Account
            WHERE username = ? OR email = ?
        """, (username_or_email, username_or_email)).fetchone()
        conn.close()

        if row:
            return Account(
                account_id=row["account_id"],
                full_name=row["full_name"],
                username=row["username"],
                email=row["email"],
                password_hash=row["password_hash"],
                role=row["role"],
                status=row["status"],
                created_at=row["created_at"]
            )
        return None