from database.db_helper import DBHelper
from entity.user_profile import UserProfile


class UserProfileRepository:
    def _row_to_profile(self, row):
        if not row:
            return None
        return UserProfile(
            profile_id=row["profile_id"],
            account_id=row["account_id"],
            role=row["role"]
        )

    def create_profile(self, account_id, role):
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

    def get_all_profiles(self):
        conn = DBHelper.get_connection()
        rows = conn.execute("""
            SELECT up.profile_id, up.account_id, up.role,
                   a.full_name, a.username, a.email, a.status
            FROM UserProfile up
            JOIN Account a ON up.account_id = a.account_id
            ORDER BY up.profile_id ASC
        """).fetchall()
        conn.close()
        return rows

    def find_by_id(self, profile_id):
        conn = DBHelper.get_connection()
        row = conn.execute("""
            SELECT * FROM UserProfile
            WHERE profile_id = ?
        """, (profile_id,)).fetchone()
        conn.close()
        return self._row_to_profile(row)

    def find_by_account_id(self, account_id):
        conn = DBHelper.get_connection()
        row = conn.execute("""
            SELECT * FROM UserProfile
            WHERE account_id = ?
        """, (account_id,)).fetchone()
        conn.close()
        return self._row_to_profile(row)

    def update_profile(self, profile_id, role):
        conn = DBHelper.get_connection()
        conn.execute("""
            UPDATE UserProfile
            SET role = ?
            WHERE profile_id = ?
        """, (role, profile_id))
        conn.commit()
        conn.close()

    def delete_profile(self, profile_id):
        conn = DBHelper.get_connection()
        conn.execute("""
            DELETE FROM UserProfile
            WHERE profile_id = ?
        """, (profile_id,))
        conn.commit()
        conn.close()

    def search_profiles(self, keyword):
        conn = DBHelper.get_connection()
        rows = conn.execute("""
            SELECT up.profile_id, up.account_id, up.role,
                   a.full_name, a.username, a.email, a.status
            FROM UserProfile up
            JOIN Account a ON up.account_id = a.account_id
            WHERE a.full_name LIKE ?
               OR a.username LIKE ?
               OR a.email LIKE ?
               OR up.role LIKE ?
            ORDER BY up.profile_id ASC
        """, (f"%{keyword}%", f"%{keyword}%", f"%{keyword}%", f"%{keyword}%")).fetchall()
        conn.close()
        return rows