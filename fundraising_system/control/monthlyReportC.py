from entity.report import Report


class MonthlyReportController:
    def generate_monthly_report(self, selected_month):
        selected_month_start = selected_month + "-01"
        return Report.generate_report("monthly", selected_month_start)