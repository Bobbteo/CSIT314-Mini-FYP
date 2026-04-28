from database.db_helper import DBHelper
from datetime import date

class FRA:
    allowed_statuses = ["active", "goal_achieved", "completed", "closed", "cancelled"]

    def __init__(
        self,
        fra_id=None,
        fundraiser_account_id=None,
        title=None,
        description=None,
        category=None,
        target_amount=None,
        current_amount=0,
        view_count=0,
        status="active",
        start_date=None,
        end_date=None,
        created_at=None
    ):
        self.fra_id = fra_id
        self.fundraiser_account_id = fundraiser_account_id
        self.title = title
        self.description = description
        self.category = category
        self.target_amount = target_amount
        self.current_amount = current_amount
        self.view_count = view_count
        self.status = status
        self.start_date = start_date
        self.end_date = end_date
        self.created_at = created_at

    @staticmethod
    def _row_to_fra(row):
        if not row:
            return None

        return FRA(
            fra_id=row["fra_id"],
            fundraiser_account_id=row["fundraiser_account_id"],
            title=row["title"],
            description=row["description"],
            category=row["category"],
            target_amount=row["target_amount"],
            current_amount=row["current_amount"],
            view_count=row["view_count"],
            status=row["status"],
            start_date=row["start_date"],
            end_date=row["end_date"],
            created_at=row["created_at"]
        )

    @staticmethod
    def get_by_fundraiser(fundraiser_account_id):
        FRA.refresh_all_fra_statuses()

        conn = DBHelper.get_connection()
        rows = conn.execute("""
            SELECT * FROM FundRaisingActivity
            WHERE fundraiser_account_id = ?
            ORDER BY created_at DESC
        """, (fundraiser_account_id,)).fetchall()
        conn.close()

        return [FRA._row_to_fra(row) for row in rows]

    @staticmethod
    def find_by_id(fra_id):
        conn = DBHelper.get_connection()
        row = conn.execute("""
            SELECT * FROM FundRaisingActivity
            WHERE fra_id = ?
        """, (fra_id,)).fetchone()
        conn.close()

        return FRA._row_to_fra(row)

    @staticmethod
    def create_fra(fundraiser_account_id, title, description, category, target_amount, start_date, end_date):
        title = title.strip()
        description = description.strip()
        category = category.strip()
        start_date = start_date.strip()
        end_date = end_date.strip()

        if not title or not description or not category or not target_amount or not start_date or not end_date:
            return {"success": False, "message": "All fields are required."}

        try:
            target_amount = float(target_amount)
        except ValueError:
            return {"success": False, "message": "Target amount must be a number."}

        if target_amount <= 0:
            return {"success": False, "message": "Target amount must be greater than 0."}

        conn = DBHelper.get_connection()
        conn.execute("""
            INSERT INTO FundRaisingActivity
            (fundraiser_account_id, title, description, category, target_amount, current_amount, status, start_date, end_date)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            fundraiser_account_id,
            title,
            description,
            category,
            target_amount,
            0,
            "active",
            start_date,
            end_date
        ))

        conn.commit()
        conn.close()

        return {"success": True, "message": "Fund raising activity created successfully."}

    @staticmethod
    def update_fra(fra_id, fundraiser_account_id, title, description, category, target_amount, start_date, end_date):
        fra = FRA.find_by_id(fra_id)

        if not fra:
            return {"success": False, "message": "FRA not found."}

        if fra.fundraiser_account_id != fundraiser_account_id:
            return {"success": False, "message": "You can only edit your own FRA."}
        
        if fra.status == "cancelled":
            return {"success": False, "message": "Cancelled FRA cannot be edited. Reactivate it first."}

        title = title.strip()
        description = description.strip()
        category = category.strip()
        start_date = start_date.strip()
        end_date = end_date.strip()

        if not title or not description or not category or not target_amount or not start_date or not end_date:
            return {"success": False, "message": "All fields are required."}

        try:
            target_amount = float(target_amount)
        except ValueError:
            return {"success": False, "message": "Target amount must be a number."}

        if target_amount <= 0:
            return {"success": False, "message": "Target amount must be greater than 0."}

        conn = DBHelper.get_connection()
        conn.execute("""
            UPDATE FundRaisingActivity
            SET title = ?, description = ?, category = ?, target_amount = ?,
                start_date = ?, end_date = ?
            WHERE fra_id = ? AND fundraiser_account_id = ?
        """, (
            title,
            description,
            category,
            target_amount,
            start_date,
            end_date,
            fra_id,
            fundraiser_account_id
        ))

        conn.commit()
        conn.close()

        return {"success": True, "message": "FRA updated successfully."}
    
    
    @staticmethod
    def cancel_fra(fra_id, fundraiser_account_id):
        fra = FRA.find_by_id(fra_id)

        if not fra:
            return {"success": False, "message": "FRA not found."}

        if fra.fundraiser_account_id != fundraiser_account_id:
            return {"success": False, "message": "You can only cancel your own FRA."}

        conn = DBHelper.get_connection()
        conn.execute("""
            UPDATE FundRaisingActivity
            SET status = 'cancelled'
            WHERE fra_id = ? AND fundraiser_account_id = ?
        """, (fra_id, fundraiser_account_id))
        conn.commit()
        conn.close()

        return {"success": True, "message": "FRA cancelled successfully."}


    @staticmethod
    def reactivate_fra(fra_id, fundraiser_account_id):
        fra = FRA.find_by_id(fra_id)

        if not fra:
            return {"success": False, "message": "FRA not found."}

        if fra.fundraiser_account_id != fundraiser_account_id:
            return {"success": False, "message": "You can only reactivate your own FRA."}

        conn = DBHelper.get_connection()
        conn.execute("""
            UPDATE FundRaisingActivity
            SET status = 'active'
            WHERE fra_id = ? AND fundraiser_account_id = ?
        """, (fra_id, fundraiser_account_id))
        conn.commit()
        conn.close()

        FRA.refresh_fra_status(fra_id)

        return {"success": True, "message": "FRA reactivated successfully."}

    @staticmethod
    def search_fra(fundraiser_account_id, keyword):
        keyword = keyword.strip().lower()

        if not keyword:
            return FRA.get_by_fundraiser(fundraiser_account_id)

        all_fras = FRA.get_by_fundraiser(fundraiser_account_id)
        results = []

        for fra in all_fras:
            if (
                keyword in fra.title.lower()
                or keyword in fra.description.lower()
                or keyword in fra.category.lower()
                or keyword in fra.status.lower()
            ):
                results.append(fra)

        return results
    
    @staticmethod
    def get_public_fras():
        FRA.refresh_all_fra_statuses()

        conn = DBHelper.get_connection()
        rows = conn.execute("""
            SELECT * FROM FundRaisingActivity
            WHERE status != 'cancelled'
            ORDER BY created_at DESC
        """).fetchall()
        conn.close()

        return [FRA._row_to_fra(row) for row in rows]

    @staticmethod
    def search_public_fras(keyword):
        keyword = keyword.strip().lower()

        if not keyword:
            return FRA.get_public_fras()

        all_fras = FRA.get_public_fras()

        return [
            fra for fra in all_fras
            if keyword in fra.title.lower()
            or keyword in fra.description.lower()
            or keyword in fra.category.lower()
            or keyword in fra.status.lower()
        ]

    @staticmethod
    def refresh_fra_status(fra_id):
        fra = FRA.find_by_id(fra_id)

        if not fra:
            return

        if fra.status == "cancelled":
            return

        today = date.today()
        end_date = date.fromisoformat(fra.end_date)

        if today > end_date:
            if fra.current_amount >= fra.target_amount:
                new_status = "completed"
            else:
                new_status = "closed"
        else:
            if fra.current_amount >= fra.target_amount:
                new_status = "goal_achieved"
            else:
                new_status = "active"

        conn = DBHelper.get_connection()
        conn.execute("""
            UPDATE FundRaisingActivity
            SET status = ?
            WHERE fra_id = ?
        """, (new_status, fra_id))
        conn.commit()
        conn.close()


    @staticmethod
    def refresh_all_fra_statuses():
        conn = DBHelper.get_connection()
        rows = conn.execute("""
            SELECT fra_id FROM FundRaisingActivity
        """).fetchall()
        conn.close()

        for row in rows:
            FRA.refresh_fra_status(row["fra_id"])

    @staticmethod
    def add_donation_amount(fra_id, amount):
        conn = DBHelper.get_connection()
        conn.execute("""
            UPDATE FundRaisingActivity
            SET current_amount = current_amount + ?
            WHERE fra_id = ?
        """, (amount, fra_id))
        conn.commit()
        conn.close()

        FRA.refresh_fra_status(fra_id)

    
    @staticmethod
    def increment_view_count(fra_id):
        conn = DBHelper.get_connection()
        conn.execute("""
            UPDATE FundRaisingActivity
            SET view_count = view_count + 1
            WHERE fra_id = ?
        """, (fra_id,))
        conn.commit()
        conn.close()


    @staticmethod
    def get_favourite_count(fra_id):
        conn = DBHelper.get_connection()
        row = conn.execute("""
            SELECT COUNT(*) AS favourite_count
            FROM Favourite
            WHERE fra_id = ?
        """, (fra_id,)).fetchone()
        conn.close()

        return row["favourite_count"] if row else 0


    @staticmethod
    def get_fra_statistics_by_fundraiser(fundraiser_account_id):
        FRA.refresh_all_fra_statuses()

        conn = DBHelper.get_connection()
        rows = conn.execute("""
            SELECT *
            FROM FundRaisingActivity
            WHERE fundraiser_account_id = ?
            AND status NOT IN ('completed', 'closed')
            ORDER BY created_at DESC
        """, (fundraiser_account_id,)).fetchall()
        conn.close()

        fra_list = [FRA._row_to_fra(row) for row in rows]

        results = []
        for fra in fra_list:
            results.append({
                "fra": fra,
                "view_count": fra.view_count,
                "favourite_count": FRA.get_favourite_count(fra.fra_id)
            })

        return results


    @staticmethod
    def get_completed_closed_fras_by_fundraiser(fundraiser_account_id):
        FRA.refresh_all_fra_statuses()

        conn = DBHelper.get_connection()
        rows = conn.execute("""
            SELECT *
            FROM FundRaisingActivity
            WHERE fundraiser_account_id = ?
            AND status IN ('completed', 'closed')
            ORDER BY end_date DESC
        """, (fundraiser_account_id,)).fetchall()
        conn.close()

        fra_list = [FRA._row_to_fra(row) for row in rows]

        results = []
        for fra in fra_list:
            results.append({
                "fra": fra,
                "view_count": fra.view_count,
                "favourite_count": FRA.get_favourite_count(fra.fra_id)
            })

        return results