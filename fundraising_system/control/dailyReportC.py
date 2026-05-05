from entity.report import Report


class DailyReportController:
    def generate_daily_report(self, selected_date):
        return Report.generate_report("daily", selected_date)