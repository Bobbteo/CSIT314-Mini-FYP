from database.db_helper import DBHelper
from entity.fra import FRA
from datetime import date

class Donation:
    @staticmethod
    def create_donation(doner_account_id, fra_id, amount):
        try:
            amount = float(amount)
        except ValueError:
            return {"success": False, "message": "Donation amount must be a number."}

        if amount <= 0:
            return {"success": False, "message": "Donation amount must be greater than 0."}

        fra = FRA.find_by_id(fra_id)

        if not fra:
            return {"success": False, "message": "FRA not found."}

        FRA.refresh_fra_status(fra_id)
        fra = FRA.find_by_id(fra_id)

        today = date.today()
        end_date = date.fromisoformat(fra.end_date)

        if today > end_date:
            return {"success": False, "message": "This FRA has ended. Donations are no longer accepted."}

        if fra.status not in ["active", "goal_achieved"]:
            return {"success": False, "message": "Donations are no longer accepted for this FRA."}

        conn = DBHelper.get_connection()
        conn.execute("""
            INSERT INTO Donation (doner_account_id, fra_id, amount)
            VALUES (?, ?, ?)
        """, (doner_account_id, fra_id, amount))
        conn.commit()
        conn.close()

        FRA.add_donation_amount(fra_id, amount)

        return {"success": True, "message": "Donation successful."}

    @staticmethod
    def get_donation_history(doner_account_id):
        conn = DBHelper.get_connection()
        rows = conn.execute("""
            SELECT d.donation_id, d.amount, d.donated_at,
                   fra.fra_id, fra.title, fra.category, fra.current_amount, fra.target_amount
            FROM Donation d
            JOIN FundRaisingActivity fra ON d.fra_id = fra.fra_id
            WHERE d.doner_account_id = ?
            ORDER BY d.donated_at DESC
        """, (doner_account_id,)).fetchall()
        conn.close()

        return rows
    
    @staticmethod
    def search_donation_history(doner_account_id, keyword):
        keyword = keyword.strip().lower()

        if not keyword:
            return Donation.get_donation_history(doner_account_id)

        all_history = Donation.get_donation_history(doner_account_id)
        results = []

        for donation in all_history:
            if (
                keyword in str(donation["donation_id"]).lower()
                or keyword in donation["title"].lower()
                or keyword in donation["category"].lower()
                or keyword in str(donation["amount"]).lower()
                or keyword in donation["donated_at"].lower()
            ):
                results.append(donation)

        return results