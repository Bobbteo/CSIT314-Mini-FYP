from database.db_helper import DBHelper
from entity.fra import FRA


class Favourite:
    @staticmethod
    def add_favourite(doner_account_id, fra_id):
        conn = DBHelper.get_connection()

        try:
            conn.execute("""
                INSERT INTO Favourite (doner_account_id, fra_id)
                VALUES (?, ?)
            """, (doner_account_id, fra_id))
            conn.commit()
            return {"success": True, "message": "FRA added to favourites."}

        except Exception:
            return {"success": False, "message": "This FRA is already in your favourites."}

        finally:
            conn.close()

    @staticmethod
    def remove_favourite(doner_account_id, fra_id):
        conn = DBHelper.get_connection()
        conn.execute("""
            DELETE FROM Favourite
            WHERE doner_account_id = ? AND fra_id = ?
        """, (doner_account_id, fra_id))
        conn.commit()
        conn.close()

        return {"success": True, "message": "FRA removed from favourites."}

    @staticmethod
    def get_favourites(doner_account_id):
        conn = DBHelper.get_connection()
        rows = conn.execute("""
            SELECT fra.*
            FROM Favourite fav
            JOIN FundRaisingActivity fra ON fav.fra_id = fra.fra_id
            WHERE fav.doner_account_id = ?
            ORDER BY fav.created_at DESC
        """, (doner_account_id,)).fetchall()
        conn.close()

        return [FRA._row_to_fra(row) for row in rows]

    @staticmethod
    def is_favourite(doner_account_id, fra_id):
        conn = DBHelper.get_connection()
        row = conn.execute("""
            SELECT favourite_id FROM Favourite
            WHERE doner_account_id = ? AND fra_id = ?
        """, (doner_account_id, fra_id)).fetchone()
        conn.close()

        return row is not None