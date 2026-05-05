from datetime import datetime, timedelta
from database.db_helper import DBHelper


class Report:
    @staticmethod
    def _get_date_range(report_type, selected_value):
        selected_date = datetime.strptime(selected_value, "%Y-%m-%d").date()

        if report_type == "daily":
            start_date = selected_date
            end_date = selected_date

        elif report_type == "weekly":
            start_date = selected_date
            end_date = selected_date + timedelta(days=6)

        elif report_type == "monthly":
            start_date = selected_date.replace(day=1)

            if start_date.month == 12:
                next_month = start_date.replace(year=start_date.year + 1, month=1, day=1)
            else:
                next_month = start_date.replace(month=start_date.month + 1, day=1)

            end_date = next_month - timedelta(days=1)

        else:
            start_date = selected_date
            end_date = selected_date

        return start_date.isoformat(), end_date.isoformat()

    @staticmethod
    def generate_report(report_type, selected_value):
        start_date, end_date = Report._get_date_range(report_type, selected_value)

        conn = DBHelper.get_connection()

        total_accounts = conn.execute("""
            SELECT COUNT(*) AS count FROM Account
        """).fetchone()["count"]

        new_accounts = conn.execute("""
            SELECT COUNT(*) AS count
            FROM Account
            WHERE DATE(created_at) BETWEEN DATE(?) AND DATE(?)
        """, (start_date, end_date)).fetchone()["count"]

        total_fras = conn.execute("""
            SELECT COUNT(*) AS count FROM FundRaisingActivity
        """).fetchone()["count"]

        new_fras = conn.execute("""
            SELECT COUNT(*) AS count
            FROM FundRaisingActivity
            WHERE DATE(created_at) BETWEEN DATE(?) AND DATE(?)
        """, (start_date, end_date)).fetchone()["count"]

        total_donations = conn.execute("""
            SELECT COUNT(*) AS count FROM Donation
        """).fetchone()["count"]

        period_donations = conn.execute("""
            SELECT COUNT(*) AS count
            FROM Donation
            WHERE DATE(donated_at) BETWEEN DATE(?) AND DATE(?)
        """, (start_date, end_date)).fetchone()["count"]

        period_amount = conn.execute("""
            SELECT COALESCE(SUM(amount), 0) AS total
            FROM Donation
            WHERE DATE(donated_at) BETWEEN DATE(?) AND DATE(?)
        """, (start_date, end_date)).fetchone()["total"]

        total_favourites = conn.execute("""
            SELECT COUNT(*) AS count FROM Favourite
        """).fetchone()["count"]

        period_favourites = conn.execute("""
            SELECT COUNT(*) AS count
            FROM Favourite
            WHERE DATE(created_at) BETWEEN DATE(?) AND DATE(?)
        """, (start_date, end_date)).fetchone()["count"]

        top_categories = conn.execute("""
            SELECT fra.category, COUNT(*) AS fra_count
            FROM FundRaisingActivity fra
            GROUP BY fra.category
            ORDER BY fra_count DESC
            LIMIT 5
        """).fetchall()

        conn.close()

        return {
            "report_type": report_type,
            "start_date": start_date,
            "end_date": end_date,
            "total_accounts": total_accounts,
            "new_accounts": new_accounts,
            "total_fras": total_fras,
            "new_fras": new_fras,
            "total_donations": total_donations,
            "period_donations": period_donations,
            "period_amount": period_amount,
            "total_favourites": total_favourites,
            "period_favourites": period_favourites,
            "top_categories": top_categories
        }