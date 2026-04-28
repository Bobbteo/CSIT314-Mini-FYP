from database.db_helper import DBHelper


class UserProfile:
    def __init__(self, profile_id=None, account_id=None, role=None):
        self.profile_id = profile_id
        self.account_id = account_id
        self.role = role

    @staticmethod
    def create_profile(account_id, role):
        conn = DBHelper.get_connection()
        cursor = conn.cursor()

        cursor.execute("""
            INSERT INTO UserProfile (account_id, role)
            VALUES (?, ?)
        """, (account_id, role))

        conn.commit()
        profile_id = cursor.lastrowid
        conn.close()

        return profile_id

    @staticmethod
    def find_by_account_id(account_id):
        conn = DBHelper.get_connection()
        row = conn.execute("""
            SELECT * FROM UserProfile
            WHERE account_id = ?
        """, (account_id,)).fetchone()
        conn.close()

        if not row:
            return None

        return UserProfile(
            profile_id=row["profile_id"],
            account_id=row["account_id"],
            role=row["role"]
        )

    @staticmethod
    def update_role_by_account_id(account_id, role):
        conn = DBHelper.get_connection()

        conn.execute("""
            UPDATE UserProfile
            SET role = ?
            WHERE account_id = ?
        """, (role, account_id))

        conn.commit()
        conn.close()